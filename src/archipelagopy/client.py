import asyncio
import functools
import inspect
import logging
import ssl
import time
import traceback
from collections.abc import Awaitable, Callable
from ssl import SSLContext
from types import MappingProxyType
from typing import Final, cast

import websockets.exceptions
from websockets.asyncio.client import ClientConnection

from archipelagopy import packets
from archipelagopy import structs
from archipelagopy.callback_interface import ClientCallbackInterface as CCInterface

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


def packet_to_json(packet: packets.ClientPacket) -> str:
    """
    Converts a ClientPacket to a JSON string.
    """

    json_data: str = f"[{packet.model_dump_json(by_alias=True)}]"
    return json_data


class ConnectionClosedError(BaseException):
    def __init__(self, close_code: websockets.CloseCode):
        self.close_code = close_code


def task_wrapper(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
    """
    Wraps a coroutine function to add exception handling and logging.
    :param self: instance of client
    :param func: coroutine function to wrap
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            _LOGGER.debug("[%s]: Task canceled", func.__name__)
            raise
        except websockets.exceptions.ConnectionClosed as e:
            close_code = websockets.CloseCode(e.sent.code)
            _LOGGER.debug("[%s]: ConnectionClosed: %s(%s)", func.__name__, close_code.name, close_code.value)
            raise
        except Exception:
            _LOGGER.exception("[%s]: Exception %s", func.__name__, traceback.format_exc())
            raise
        finally:
            _LOGGER.debug("[%s]: Stopped", func.__name__)

    return wrapper


class Client(CCInterface):
    # Accumulation period for reconnect attempts. Reconnect attempts which are older than this period will be ignored.
    RECONNECT_ACCUMULATION_PERIOD: float = 60  # seconds

    def __init__(self, port: int, host: str = "archipelago.gg", ssl_context: SSLContext | None = None,
                 secure: bool = True, auto_reconnect: bool = False):
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
        self.__addr: str = f"wss://{host}:{port}" if secure else f"ws://{host}:{port}"
        self.__secure: bool = secure
        self.__ssl_context = ssl.create_default_context() if ssl_context is None else ssl_context
        self.__auto_reconnect: bool = auto_reconnect

        self.__socket: ClientConnection | None = None
        self.__run_task: asyncio.Task | None = None
        self.__stop_task: asyncio.Task | None = None
        self.__send_lock = asyncio.Lock()
        self.__send_queue: asyncio.Queue[str] = asyncio.Queue()
        self.__stop_event: asyncio.Event = asyncio.Event()
        self.__stop_lock: asyncio.Lock = asyncio.Lock()

        # keep track of server connection close events
        self.__reconnect_timestamps: list[float] = []

    async def start(self):
        if self.__run_task is not None and not self.__run_task.done():
            return

        self.__run_task = asyncio.create_task(
            self._connect_wrapper(),
            name=f"{__name__}.connect_wrapper[{self.__addr}]"
        )

    async def _stop(self):
        if self.__socket is not None:
            await self.__socket.close()

        if self.__run_task is None:
            return

        self.__run_task.cancel()
        try:
            await self.__run_task
        except asyncio.CancelledError:
            pass
        except Exception:
            _LOGGER.exception("[%s]: %s", self.__addr, traceback.format_exc())

        self.__run_task = None
        self.__socket = None

        self.__stop_event.set()

        _LOGGER.debug("[%s]: Client stopped.", self.__addr)

    async def stop(self):

        async with self.__stop_lock:
            # schedule stop task to avoid creating a circular cancellation chain (a task cannot cancel itself)
            self.__stop_task = asyncio.create_task(
                self._stop(),
                name=f"{__name__}.stop_task[{self.__addr}]"
            )
            await self.__stop_task

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

        callback: Callable[..., Awaitable] | None = PACKET_CALLBACK_MAP.get(type(packet), None)

        if callback is None:
            return None

        return callback(self)

    async def _loop_handler(self):

        receiver_task: asyncio.Task | None = None
        sender_task: asyncio.Task | None = None

        try:
            receiver_task = asyncio.create_task(
                self._receive_loop(),
                name=f"{__name__}.receive_loop[{self.__addr}]"
            )

            sender_task = asyncio.create_task(
                self._send_loop(),
                name=f"{__name__}.send_loop[{self.__addr}]"
            )

            await asyncio.wait(
                [receiver_task, sender_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

        finally:

            if sender_task is not None:
                if not sender_task.done():
                    sender_task.cancel()
                    try:
                        await sender_task
                    except asyncio.CancelledError:
                        pass

            if receiver_task is not None:
                if not receiver_task.done():
                    receiver_task.cancel()
                    try:
                        await receiver_task
                    except asyncio.CancelledError:
                        pass

    def _get_reconnect_frequency(self) -> int:
        now: float = time.time()

        # Remove timestamps that are older than the RECONNECT_ACCUMULATION_PERIOD
        self.__reconnect_timestamps = [
            ts for ts in self.__reconnect_timestamps
            if (now - ts) < self.RECONNECT_ACCUMULATION_PERIOD
        ]

        return len(self.__reconnect_timestamps)

    def _increase_reconnects(self):
        self.__reconnect_timestamps.append(time.time())

    async def wait_closed(self, task: asyncio.Task | None = None) -> None:
        """
        Waits until the client is closed. If a task is provided,
        it will wait for the task to complete or for the client to be closed.
        :param task: An optional task to wait for. If provided,
         the client will wait for either the task to complete or for the client to be closed.
        :return: None
        """

        if task is not None:
            stop_event_task: asyncio.Task = asyncio.create_task(
                self.__stop_event.wait(),
                name=f"{__name__}.wait_closed_stop_event[{self.__addr}]"
            )

            await asyncio.wait(
                [task, stop_event_task],
                return_when=asyncio.FIRST_COMPLETED
            )
        else:
            await self.__stop_event.wait()

    def _create_websocket_connection(self) -> websockets.connect:
        kwargs: dict = {
            "uri": self.__addr,
            "max_size": None,  # Disable size limit for messages
        }

        if self.__secure:
            kwargs["ssl"] = self.__ssl_context

        return websockets.connect(**kwargs)

    async def _connect(self):
        ws: ClientConnection
        async with self._create_websocket_connection() as ws:
            self.__socket = ws
            self._increase_reconnects()

            _LOGGER.debug("[%s]: Connected", self.__addr)

            # fire on_ready event
            await self.on_ready()

            await self._loop_handler()

            if ws.close_code is not None:
                raise ConnectionClosedError(websockets.CloseCode(ws.close_code))

    async def _handle_reconnect_backoff(self):
        self._increase_reconnects()
        backoff: int = self._exponential_backoff(
            self._get_reconnect_frequency()
        )
        _LOGGER.info("[%s]: Connect call failed, retrying in %s", self.__addr, backoff)
        await asyncio.sleep(backoff)

    async def _connect_wrapper(self):
        try:
            while True:
                try:
                    await self._connect()
                except ConnectionRefusedError as error:
                    self.on_connect_error(error)

                    if self.__auto_reconnect:
                        await self._handle_reconnect_backoff()
                        continue

                except ConnectionClosedError as error:
                    close_code = error.close_code
                    _LOGGER.info("[%s]: ConnectionClosed: %s(%s)", self.__addr, close_code.name, close_code.value)
                    self.on_connection_closed(close_code)
                    if error.close_code == websockets.CloseCode.GOING_AWAY and self.__auto_reconnect:
                        continue

                except (
                        websockets.exceptions.InvalidURI,
                        websockets.exceptions.InvalidHandshake,
                        websockets.exceptions.InvalidProxy,
                        TimeoutError,
                        OSError
                ) as error:
                    _LOGGER.debug("[%s]: %s", self.__addr, error)
                    self.on_connect_error(error)

                except Exception:
                    _LOGGER.exception("[%s]: %s", self.__addr, traceback.format_exc())
                    raise

                break
        finally:
            _LOGGER.debug("[%s]: Connect loop stopped", self.__addr)
            # signal that the client has stopped
            self.__stop_event.set()

    async def _process_packet(self, packet: packets.ServerPacket):

        # fire on_packet event
        await self.on_packet(packet)

        # manage callback
        callback: Callable[..., Awaitable] = self._resolve_packet_callback(packet)
        if callback is not None:
            await callback(packet)

    @task_wrapper
    async def _receive_loop(self):
        js: str
        async for js in self.__socket:
            # fire on_received event
            await self.on_received(js)

            packet_list: list[packets.ServerPacket] = packets.PACKET_TYPE_ADAPTER.validate_json(js)

            packet: packets.ServerPacket
            for packet in packet_list:
                await self._process_packet(packet)

    @task_wrapper
    async def _send_loop(self):
        while True:
            message: str = await self.__send_queue.get()
            await self.__socket.send(message, text=True)
            _LOGGER.debug("[%s]: << %s", self.__addr, message)

    async def send(self, packet: packets.ClientPacket):
        json_data: str = packet_to_json(packet)
        await self.__send_queue.put(json_data)

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

    @property
    def address(self) -> str:
        return self.__addr
