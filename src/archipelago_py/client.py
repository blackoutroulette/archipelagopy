import asyncio
import collections
import inspect
import logging
import math
import ssl
import time
import traceback
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
# The lambda (resolve function) is needed to make dynamic function overrides (monkey patching) work.
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


def packet_to_json(packet: packets.ClientPacket) -> str:
    """
    Converts a ClientPacket to a JSON string.
    """

    json_data: str = f"[{packet.model_dump_json(by_alias=True)}]"
    return json_data

class ConnectionClosedError(BaseException):
    def __init__(self, close_code: websockets.CloseCode):
        self.close_code = close_code


class Client(CCInterface):

    # Accumulation period for reconnect attempts. Reconnect attempts which are older than this period will be ignored.
    RECONNECT_ACCUMULATION_PERIOD: float = 60  # seconds

    def __init__(self, port: int, host: str = "archipelago.gg", ssl_context: SSLContext | None = None, secure: bool = True, auto_reconnect: bool = False):
        """
        :param port: The port to connect to.
        :param host: The host to connect to. Defaults to "archipelago.gg".
        :param ssl_context: An optional SSLContext to use for secure connections.
        :param secure: Whether to use a secure connection (wss://) or not (ws://).
        :param auto_reconnect: Whether to automatically trying to reconnect.
         This only applies to when the server is going into standby or
         the server is already in standby during the connecting phase.
        """

        super().__init__()
        self._addr: str = f"wss://{host}:{port}" if secure else f"ws://{host}:{port}"
        self._secure: bool = secure
        self._ssl_context = ssl.create_default_context() if ssl_context is None else ssl_context
        self._auto_reconnect: bool = auto_reconnect

        self._socket: ClientConnection | None = None
        self._task: asyncio.Task | None = None
        self._send_lock = asyncio.Lock()
        self._send_queue: asyncio.Queue[str] = asyncio.Queue()
        self._receiver_task: asyncio.Task | None = None
        self._sender_task: asyncio.Task | None = None
        self._stop_event: asyncio.Event = asyncio.Event()

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

        self._task = None
        self._socket = None

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
        self._receiver_task = asyncio.create_task(self._task_wrapper(self._receive_loop))
        self._sender_task = asyncio.create_task(self._task_wrapper(self._send_loop))
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

    async def wait_closed(self, task: asyncio.Task | None = None) -> None:
        """
        Waits until the client is closed. If a task is provided,
        it will wait for the task to complete or for the client to be closed.
        :param task: An optional task to wait for. If provided,
         the client will wait for either the task to complete or for the client to be closed.
        :return: None
        """

        if task is not None:
            stop_event_task: asyncio.Task = asyncio.create_task(self._stop_event.wait())
            await asyncio.wait(
                [task, stop_event_task],
                return_when=asyncio.FIRST_COMPLETED
            )
        else:
            await self._stop_event.wait()

    def _create_websocket_connection(self) -> websockets.connect:
        kwargs: dict = {
            "uri": self._addr,
            "max_size": None,  # Disable size limit for messages
        }

        if self._secure:
            kwargs["ssl"] = self._ssl_context

        return websockets.connect(**kwargs)


    async def _connect(self):
        ws: ClientConnection
        async with self._create_websocket_connection() as ws:

            self._socket = ws
            self._increase_reconnects()

            _LOGGER.info("[%s]: Connected", self._addr)

            # fire on_ready event
            await self.on_ready()

            await self._loop_handler()

            # if we are here, the connection was closed by the server
            raise ConnectionClosedError(websockets.CloseCode(ws.close_code))

    async def _handle_reconnect_backoff(self):
        self._increase_reconnects()
        backoff: int = self._exponential_backoff(
            self._get_reconnect_frequency()
        )
        _LOGGER.info("[%s]: Connect call failed, retrying in %s", self._addr, backoff)
        await asyncio.sleep(backoff)

    async def _connect_wrapper(self):
        while True:
            try:
                await self._connect()
            except ConnectionRefusedError as error:
                self.on_connect_error(error)

                if self._auto_reconnect:
                    await self._handle_reconnect_backoff()
                    continue

            except ConnectionClosedError as error:
                close_code = error.close_code
                _LOGGER.info("[%s]: ConnectionClosed: %s(%s)",self._addr, close_code.name, close_code.value)
                self.on_connection_closed(close_code)
                if error.close_code == websockets.CloseCode.GOING_AWAY and self._auto_reconnect:
                    continue

            except (
                websockets.exceptions.InvalidURI,
                websockets.exceptions.InvalidHandshake,
                websockets.exceptions.InvalidProxy,
                TimeoutError,
                OSError
            ) as error:
                self.on_connect_error(error)

            except asyncio.CancelledError:
                pass

            # except Exception as error:
            #     _LOGGER.exception("[%s]: %s", self._addr, traceback.format_exc())
            #     raise error

            break

        _LOGGER.debug("[%s]: Connect loop stopped", self._addr)
        # signal that the client has stopped
        self._stop_event.set()


    async def _process_packet(self, packet: packets.ServerPacket):

        # fire on_packet event
        await self.on_packet(packet)

        # manage callback
        callback: Callable[..., Awaitable] = self._resolve_packet_callback(packet)
        if callback is not None:
            await callback(packet)

    async def _task_wrapper(self, func: Callable[..., Awaitable]) -> None:
        try:
            await func()
        except asyncio.CancelledError:
            _LOGGER.debug("[%s][%s]: Task canceled", func.__name__, self._addr)
        except websockets.exceptions.ConnectionClosed as e:
            close_code = websockets.CloseCode(e.sent.code)
            _LOGGER.debug("[%s][%s]: ConnectionClosed: %s(%s)", func.__name__, self._addr, close_code.name,  close_code.value)
        # except Exception as error:
        #     _LOGGER.exception("[%s][%s]: %s", func.__name__, self._addr, traceback.format_exc())
        #     raise error
        finally:
            _LOGGER.debug("[%s][%s]: Stopped", func.__name__, self._addr)

    async def _receive_loop(self):
        js: str
        async for js in self._socket:

            # fire on_received event
            await self.on_received(js)

            packet_list: list[packets.ServerPacket] = packets.PACKET_TYPE_ADAPTER.validate_json(js)

            packet: packets.ServerPacket
            await asyncio.gather(*[
                self._process_packet(packet) for packet in packet_list
            ])

    async def send(self, packet: packets.ClientPacket):
        json_data: str = packet_to_json(packet)
        await self._send_queue.put(json_data)

    async def _send_loop(self):
        while True:
            message: str = await self._send_queue.get()
            _LOGGER.debug("[%s]: << %s", self._addr, message)
            await self._socket.send(message, text=True)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    def _monkey_patch_handler(self, key: str, value: object):
        """
        Assert that monkey patched callbacks are of the same signature as the original ones, e.g.
        coroutine functions must be patched with coroutine functions, and regular functions with regular functions.
        """

        if not hasattr(self, key):
            return

        obj: object = getattr(self, key)
        if not callable(obj):
            return

        if not callable(value):
            _LOGGER.warning("Monkey patching callable %s with non-callable %s", key, value)

        func_is_co: bool = inspect.iscoroutinefunction(obj)
        patch_is_co: bool = inspect.iscoroutinefunction(value)

        if func_is_co and not patch_is_co:
            raise TypeError(f"Cannot monkey patch coroutine function {key} with non-coroutine function.")

        if not func_is_co and patch_is_co:
            raise TypeError(f"Cannot monkey patch non-coroutine function {key} with coroutine function.")

    def __setattr__(self, key: str, value: object):
        self._monkey_patch_handler(key, value)
        super().__setattr__(key, value)

