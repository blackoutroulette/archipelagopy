import asyncio
import collections
import inspect
import logging
import ssl
import time
from collections.abc import Awaitable, Callable, AsyncIterator
from ssl import SSLContext
from types import MappingProxyType
from typing import Final, cast

import websockets.exceptions
from websockets.asyncio.client import ClientConnection
from websockets.asyncio.client import connect

from archipelago_py import packets
from archipelago_py import structs
from archipelago_py.callback_interface import ClientCallbackInterface as CCInterface

_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)

PacketCallbackMapType = Final[
        MappingProxyType[type[packets.ServerPacket], Callable[[CCInterface], Callable[..., Awaitable]]]
]

# Maps packets.ServerPacket types to their respective callback functions.
# The lambda (resolve function) is needed to make dynamic function overrides work.
PACKET_CALLBACK_MAP: PacketCallbackMapType = MappingProxyType({
    packets.Bounced: lambda x: cast(CCInterface, x).on_bounced,
    packets.Connected: lambda x: cast(CCInterface, x).on_connected,
    packets.ConnectionRefused: lambda x: cast(CCInterface, x).on_connection_refused,
    packets.DataPackage: lambda x: cast(CCInterface, x).on_data_package,
    packets.InvalidPacket: lambda x: cast(CCInterface, x).on_invalid_packet,
    packets.LocationInfo: lambda x: cast(CCInterface, x).on_location_info,
    packets.PrintJSON: lambda x: cast(CCInterface, x).on_print_json,
    packets.ReceivedItems: lambda x: cast(CCInterface, x).on_received_items,
    packets.Retrieved: lambda x: cast(CCInterface, x).on_retrieved,
    packets.RoomInfo: lambda x: cast(CCInterface, x).on_room_info,
    packets.RoomUpdate: lambda x: cast(CCInterface, x).on_room_update,
    packets.SetReply: lambda x: cast(CCInterface, x).on_set_reply,
})

def json_default_encode(obj: object):
    if isinstance(obj, packets.ClientPacket):
        v: dict = {k: json_default_encode(v) for k, v in vars(obj).items()}
        v["cmd"] = obj.__class__.__name__
        return [v]

    if isinstance(obj, structs.Struct):
        v: dict = {k: json_default_encode(v) for k, v in vars(obj).items()}
        v["class"] = obj.__class__.__name__
        return v

    return obj


def _handle_task_exception(task: asyncio.Task):
    exc = task.exception()
    if exc:
        _LOGGER.error(exc)


def ensure_callback_is_coroutine(callback: Callable[..., Awaitable]):
    if not inspect.iscoroutinefunction(callback):
        raise RuntimeError(f"Callback {callback.__name__} must be a coroutine function.")


def packet_to_json(packet: packets.ClientPacket) -> str:
    """
    Converts a ClientPacket to a JSON string.
    """

    json_data: str = f"[{packet.model_dump_json(by_alias=True)}]"
    return json_data


class Client(CCInterface):

    RECONNECT_THRESHOLD: Final[int] = 3
    RECONNECT_ACCUMULATION_PERIOD: Final[int] = 60  # seconds

    def __init__(self, port: int, host: str = "archipelago.gg", ssl_context: SSLContext | None = None, secure: bool = True):
        super().__init__()
        self._addr: str = f"wss://{host}:{port}" if secure else f"ws://{host}:{port}"
        self._secure: bool = secure
        self._ssl_context = ssl.create_default_context() if ssl_context is None else ssl_context
        self._socket: ClientConnection | None = None
        self._task: asyncio.Task | None = None
        self._send_lock = asyncio.Lock()
        self._send_queue: asyncio.Queue[str] = asyncio.Queue()
        self._receiver_task: asyncio.Task | None = None
        self._sender_task: asyncio.Task | None = None
        self._stop_event: asyncio.Event = asyncio.Event()

        # Save last successful connect packet to reconnect in case of connection loss
        self._connect_packet_queue: asyncio.Queue[packets.Connect] = asyncio.Queue()
        self._last_successful_connect_packet: packets.Connect | None = None

        # keep track of server connection close events
        self._server_connection_close_timestamps: list[float] = []

    async def start(self):
        self._task = asyncio.create_task(
            self._connect()
        )
        self._task.add_done_callback(_handle_task_exception)


    async def stop(self):
        if self._socket is not None:
            await self._socket.close()

        if self._task is None:
            return

        self._task.cancel()
        await self._task

        self._stop_event.set()

        _LOGGER.info("[%s]: Client stopped.", self._addr)

    def _resolve_packet_callback(self, packet: packets.ServerPacket) -> Callable[..., Awaitable] | None:
        """
        Resolves the callback function for a given packet type.
        """

        callback: Callable[..., Awaitable] | None = PACKET_CALLBACK_MAP.get(type(packet), None)(self)
        return callback

    async def _loop_handler(self):
        self._receiver_task = asyncio.create_task(self._receive_loop())
        self._sender_task = asyncio.create_task(self._send_loop())
        done, pending = await asyncio.wait(
            [self._receiver_task, self._sender_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        pending = next(iter(pending))
        pending.cancel()

        done = next(iter(done))
        await done

        exc = done.exception()
        if exc:
            raise exc

    def _get_server_connection_close_frequency(self) -> int:
        now = time.time()

        self._server_connection_close_timestamps = [
            timestamp for timestamp in self._server_connection_close_timestamps
            if (now - timestamp) < self.RECONNECT_ACCUMULATION_PERIOD
        ]

        return len(self._server_connection_close_timestamps)

    async def wait_closed(self) -> None:
        await self._stop_event.wait()

    async def _handle_connection_closed(self):
        # log the connection close event timestamp
        now: float = time.time()
        self._server_connection_close_timestamps.append(now)

        # get the close code from the socket
        close_code = websockets.CloseCode(self._socket.close_code)

        # check if server went into standby mode
        if close_code == websockets.CloseCode.GOING_AWAY:
            ensure_callback_is_coroutine(self.on_server_shutdown)
            await self.on_server_shutdown()

        _LOGGER.info(
            "[%s]: The server closed the connection, reason: %s(%s)",
            self._addr, close_code.name, close_code
        )

        # stop the client if the server closed the connection too many times in a short period
        if self._get_server_connection_close_frequency() >= self.RECONNECT_THRESHOLD:
            _LOGGER.warning(
                "[%s]: The server closed the connection %d times in the last 60 seconds, stopping client.",
                self._addr, self.RECONNECT_THRESHOLD
            )
            await self.stop()
            return

        # wait at least 1 second before trying to reconnect
        await asyncio.sleep(1)

    def _create_websocket_connection(self) -> connect:
        if self._secure:
            return connect(self._addr, ssl=self._ssl_context)

        return connect(self._addr)

    async def _connect(self):
        try:
            ws: ClientConnection
            while True:

                async with self._create_websocket_connection() as ws:

                    self._socket = ws

                    if self._last_successful_connect_packet is not None:
                        # if we have a last successful connect packet, send it again
                        _LOGGER.info("[%s]: Reconnecting with last successful connect packet", self._addr)
                        await self._socket.send(
                            packet_to_json(self._last_successful_connect_packet)
                        )
                    else:
                        _LOGGER.info("[%s]: Connected", self._addr)

                    # fire on_ready event
                    ensure_callback_is_coroutine(self.on_ready)
                    await self.on_ready()

                    try:
                        await self._loop_handler()

                        # if we are here, the connection was closed by the server
                        await self._handle_connection_closed()

                    except asyncio.CancelledError:
                        # The task was cancelled, likely due to stop() being called
                        break

        except (
            websockets.exceptions.InvalidURI,
            websockets.exceptions.InvalidHandshake,
            websockets.exceptions.InvalidProxy,
            ConnectionRefusedError,
            TimeoutError,
            OSError
        ) as error:
            await self.on_connect_error(error)
        except Exception as error:
            _LOGGER.error("[%s]: %s", self._addr, error)

        # signal that the client has stopped
        self._stop_event.set()

    def _handle_connect_response(self, packet: packets.ServerPacket):
        if self._connect_packet_queue.empty():
            # should not happen, but just in case
            return

        if isinstance(packet, packets.Connected):
            # if the packet last Connect packet was successful, save it
            self._last_successful_connect_packet = self._connect_packet_queue.get_nowait()

        if isinstance(packet, packets.ConnectionRefused):
            # remove the connect packet from the queue if the connection was refused
            # and reset the last successful connect packet
            self._connect_packet_queue.get_nowait()
            self._last_successful_connect_packet = None

    async def _process_packet(self, packet: packets.ServerPacket):
        self._handle_connect_response(packet)

        # fire on_packet event
        ensure_callback_is_coroutine(self.on_packet)
        await self.on_packet(packet)

        # manage callback
        callback: Callable[..., Awaitable] = self._resolve_packet_callback(packet)
        if callback is not None:
            ensure_callback_is_coroutine(callback)
            await callback(packet)


    async def _receive_loop(self):

        js: str
        # loop will silently break if the connection is closed and will not raise an exception
        async for js in self._socket:

            # fire on_received event
            ensure_callback_is_coroutine(self.on_received)
            await self.on_received(js)

            packet_list: list[packets.ServerPacket] = packets.PACKET_TYPE_ADAPTER.validate_json(js)

            packet: packets.ServerPacket
            await asyncio.gather(*[
                self._process_packet(packet) for packet in packet_list
            ])


    async def send(self, packet: packets.ClientPacket):
        if isinstance(packet, packets.Connect):
            self._connect_packet_queue.put_nowait(packet)

        json_data: str = packet_to_json(packet)
        await self._send_queue.put(json_data)

    async def _send_loop(self):
        while True:
            message: str = await self._send_queue.get()
            await self._socket.send(message, text=True)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
