import asyncio
import logging
from collections.abc import Awaitable, Callable
from types import MappingProxyType
from typing import Final, cast

import websockets
from websockets.asyncio.client import ClientConnection
from websockets.asyncio.client import connect

from archipelago_py import packets
from archipelago_py import structs
from archipelago_py.callback_interface import ClientCallbackInterface as CCInterface

_LOGGER: Final[logging.Logger] = logging.getLogger(__name__)


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


class Client(CCInterface):
    PacketCallbackMapType = Final[
        MappingProxyType[type[packets.ServerPacket], Callable[[CCInterface], Callable[..., Awaitable]]]]

    # Maps packets.ServerPacket types to their respective callback functions.
    # The lambda (resolve function) is needed to make dynamic function overrides work.
    PACKET_CALLBACK_MAP: PacketCallbackMapType = MappingProxyType({
        packets.Bounced: lambda x: cast("CCInterface", x).on_bounced,
        packets.Connected: lambda x: cast("CCInterface", x).on_connected,
        packets.ConnectionRefused: lambda x: cast("CCInterface", x).on_connection_refused,
        packets.DataPackage: lambda x: cast("CCInterface", x).on_data_package,
        packets.InvalidPacket: lambda x: cast("CCInterface", x).on_invalid_packet,
        packets.LocationInfo: lambda x: cast("CCInterface", x).on_location_info,
        packets.PrintJSON: lambda x: cast("CCInterface", x).on_print_json,
        packets.ReceivedItems: lambda x: cast("CCInterface", x).on_received_items,
        packets.Retrieved: lambda x: cast("CCInterface", x).on_retrieved,
        packets.RoomInfo: lambda x: cast("CCInterface", x).on_room_info,
        packets.RoomUpdate: lambda x: cast("CCInterface", x).on_room_update,
        packets.SetReply: lambda x: cast("CCInterface", x).on_set_reply,
    })

    def __init__(self, port: int, host: str = "archipelago.gg"):
        super().__init__()
        self._addr = f"wss://{host}:{port}"
        self._socket: ClientConnection | None = None
        self._ready = asyncio.Event()
        self._task: asyncio.Task | None = None
        self._send_lock = asyncio.Lock()

    async def start(self):
        try:
            self._task = asyncio.create_task(
                self._connect()
            )
            self._task.add_done_callback(_handle_task_exception)
        except KeyboardInterrupt as e:
            await self.stop()
            raise e

    async def stop(self):
        if self._task is None:
            return

        self._task.cancel()
        await self._task

        _LOGGER.info("Client stopped.")

    def _resolve_packet_callback(self, packet: packets.ServerPacket) -> Callable[..., Awaitable] | None:
        """
        Resolves the callback function for a given packet type.
        """

        callback: Callable[..., Awaitable] | None = self.PACKET_CALLBACK_MAP.get(type(packet), None)(self)
        return callback

    async def _connect(self):
        try:
            ws: ClientConnection
            async for ws in connect(self._addr):
                try:
                    _LOGGER.info("Connected to %s", self._addr)
                    self._socket = ws
                    self._ready.set()

                    # fire on_ready event
                    await self.on_ready()

                    await self.loop()
                except websockets.exceptions.ConnectionClosed as exc:
                    if exc.sent.code == websockets.CloseCode.NORMAL_CLOSURE:
                        _LOGGER.error(
                            "The Server closed the connection unexpectedly. This is likely caused by a missing key in a send packet."
                        )
                        break

                    if exc.sent.code == websockets.CloseCode.GOING_AWAY:
                        _LOGGER.error("The Server shut down due to lobby inactivity.")
                        break

                    _LOGGER.error(exc)
                    continue
        except websockets.InvalidURI as exc:
            _LOGGER.error(exc)
        except asyncio.exceptions.CancelledError:
            self._ready.clear()
            if self._socket is not None:
                await self._socket.close()
            return
        except ConnectionRefusedError:
            exc = ConnectionRefusedError(
                f"Connect call failed for {self._addr}. The server is probably in standby"
                " and needs to be started by opening the web interface"
            )
            _LOGGER.error(exc)

    async def loop(self):

        while True:

            js: str = await self._socket.recv()
            packet_list: list[packets.ServerPacket] = packets.PACKET_TYPE_ADAPTER.validate_json(js)

            for packet in packet_list:

                # fire on_packet event
                await self.on_packet(packet)

                # manage callback
                callback: Callable[..., Awaitable] = self._resolve_packet_callback(packet)
                if callback is not None:
                    await callback(packet)

                if isinstance(packet, packets.InvalidPacket):
                    _LOGGER.error("Received an invalid packet: %s", packet.errors)
                    continue

                if isinstance(packet, packets.ConnectionRefused):
                    _LOGGER.error("Connection refused by server: %s", ",".join(e.name for e in packet.errors))
                    break

    async def send(self, packet: packets.ClientPacket):

        if self._socket is None:
            raise RuntimeError("Client is not connected to a server.")

        json_data = f"[{packet.model_dump_json(by_alias=True)}]"

        await self._ready.wait()

        async with self._send_lock:
            await self._socket.send(json_data, text=True)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
