import asyncio
import inspect
import logging
import ssl
from collections.abc import Awaitable, Callable
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


def _ensure_callback_is_coroutine(callback: Callable[..., Awaitable]):
    if not inspect.iscoroutinefunction(callback):
        raise RuntimeError(f"Callback {callback.__name__} must be a coroutine function.")


class Client(CCInterface):

    def __init__(self, port: int, host: str = "archipelago.gg", ssl_context: SSLContext | None = None):
        super().__init__()
        self._addr = f"wss://{host}:{port}"
        self._ssl_context = ssl.create_default_context() if ssl_context is None else ssl_context
        self._socket: ClientConnection | None = None
        self._task: asyncio.Task | None = None
        self._send_lock = asyncio.Lock()
        self._send_queue: asyncio.Queue[str] = asyncio.Queue()
        self._receiver_task: asyncio.Task | None = None
        self._sender_task: asyncio.Task | None = None

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
        for task in pending:
            task.cancel()

        raise next(iter(done)).exception()

    async def _connect(self):
        try:
            ws: ClientConnection
            async for ws in connect(self._addr, ssl=self._ssl_context):

                _LOGGER.info("[%s]: Connected", self._addr)
                self._socket = ws

                # fire on_ready event
                _ensure_callback_is_coroutine(self.on_ready)
                await self.on_ready()

                try:
                    await self._loop_handler()
                except websockets.exceptions.ConnectionClosed as e:
                    close_code = websockets.CloseCode(e.sent.code)
                    _LOGGER.error(
                        "[%s]: The server closed the connection, close code: %s (%s)",
                        self._addr, close_code.name, e.sent.code
                    )
                    continue
                except asyncio.CancelledError:
                    break

        except (
            websockets.exceptions.InvalidURI,
            websockets.exceptions.InvalidHandshake,
            websockets.exceptions.InvalidProxy,
            TimeoutError,
            OSError
        ) as error:
            self.on_connect_error(error)
        except Exception as error:
            _LOGGER.error("[%s]: %s", self._addr, error)
            raise error

    async def _process_packet(self, packet: packets.ServerPacket):
        # fire on_packet event
        _ensure_callback_is_coroutine(self.on_packet)
        await self.on_packet(packet)

        # manage callback
        callback: Callable[..., Awaitable] = self._resolve_packet_callback(packet)
        if callback is not None:
            _ensure_callback_is_coroutine(callback)
            await callback(packet)


    async def _receive_loop(self):

        js: str
        async for js in self._socket:

            packet_list: list[packets.ServerPacket] = packets.PACKET_TYPE_ADAPTER.validate_json(js)

            packet: packets.ServerPacket
            await asyncio.gather(*[
                self._process_packet(packet) for packet in packet_list
            ])


    async def send(self, packet: packets.ClientPacket):
        json_data: str = f"[{packet.model_dump_json(by_alias=True)}]"
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
