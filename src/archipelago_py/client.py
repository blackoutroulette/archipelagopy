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
from websockets import ConnectionClosed
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

    RECONNECT_ACCUMULATION_PERIOD: float = 60  # seconds

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
        self._reconnect_timestamps: list[float] = []

    async def start(self):
        self._task = asyncio.create_task(self._connect_wrapper())
        self._task.add_done_callback(_handle_task_exception)


    async def stop(self):
        if self._socket is not None:
            await self._socket.close()

        if self._task is None:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass

        self._stop_event.set()

        _LOGGER.info("[%s]: Client stopped.", self._addr)

    @staticmethod
    def _exponential_backoff(attempt: int, max_wait: int = 60) -> int:
        """
        Returns an exponential backoff time in seconds based on the attempt number.
        """

        return min(2 ** attempt, max_wait)

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
        await pending

        done = next(iter(done))
        await done

    def _get_reconnect_frequency(self) -> int:
        now: float = time.time()

        # Remove timestamps that are older than the RECONNECT_ACCUMULATION_PERIOD
        self._reconnect_timestamps = [
            ts for ts in self._reconnect_timestamps
            if (now - ts) < self.RECONNECT_ACCUMULATION_PERIOD
        ]

        return len(self._reconnect_timestamps)

    def _increase_reconnects(self):
        self._reconnect_timestamps.append(time.time())

    async def wait_closed(self) -> None:
        await self._stop_event.wait()

    async def _handle_connection_closed(self):

        # get the close code from the socket
        close_code = websockets.CloseCode(self._socket.close_code)

        # check if server went into standby mode
        if close_code == websockets.CloseCode.GOING_AWAY:
            ensure_callback_is_coroutine(self.on_server_shutdown)
            await self.on_server_shutdown()

        _LOGGER.debug(
            "[%s]: ConnectionClosed: %s(%s)",
            self._addr, close_code.name, close_code
        )

        reconnect_frequency: int = self._get_reconnect_frequency()

        # wait with exponential backoff before trying to reconnect
        await asyncio.sleep(
            self._exponential_backoff(reconnect_frequency)
        )

    def _create_websocket_connection(self) -> websockets.connect:
        if self._secure:
            return websockets.connect(self._addr, ssl=self._ssl_context)

        return websockets.connect(self._addr)

    async def _handle_reauthentication(self):
        if self._last_successful_connect_packet is not None:
            # if we have a last successful connect packet, send it again
            _LOGGER.info("[%s]: Reconnecting with last successful connect packet", self._addr)
            await self._socket.send(
                packet_to_json(self._last_successful_connect_packet)
            )
        else:
            _LOGGER.info("[%s]: Connected", self._addr)

    async def _connect(self):
        ws: ClientConnection
        while True:

            async with self._create_websocket_connection() as ws:

                self._socket = ws
                self._increase_reconnects()

                await self._handle_reauthentication()

                # fire on_ready event
                ensure_callback_is_coroutine(self.on_ready)
                await self.on_ready()


                await self._loop_handler()
                # if we are here, the connection was closed by the server
                await self._handle_connection_closed()


    async def _connect_wrapper(self):
        try:
            await self._connect()
        except (
            websockets.exceptions.InvalidURI,
            websockets.exceptions.InvalidHandshake,
            websockets.exceptions.InvalidProxy,
            ConnectionRefusedError,
            TimeoutError,
            OSError
        ) as error:
            await self.on_connect_error(error)
        except asyncio.CancelledError:
            pass
        except Exception as error:
            _LOGGER.error("[%s]: %s", self._addr, error)

        _LOGGER.debug("[%s]: connect loop stopped", self._addr)
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

        try:
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
        except websockets.ConnectionClosed as e:
            _LOGGER.debug("[%s]: %s", self._addr, e)
        except asyncio.CancelledError:
            pass

        _LOGGER.debug("[%s]: receive task stopped", self._addr)


    async def send(self, packet: packets.ClientPacket):
        if isinstance(packet, packets.Connect):
            self._connect_packet_queue.put_nowait(packet)

        json_data: str = packet_to_json(packet)
        await self._send_queue.put(json_data)

    async def _send_loop(self):
        try:
            while True:
                message: str = await self._send_queue.get()
                await self._socket.send(message, text=True)
        except websockets.ConnectionClosed as e:
            _LOGGER.debug("[%s]: %s", self._addr, e)
        except asyncio.CancelledError:
            pass

        _LOGGER.debug("[%s]: send task stopped", self._addr)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
