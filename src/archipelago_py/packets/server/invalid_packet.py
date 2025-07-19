from typing import Literal

from archipelago_py.enums.packet_problem_type import PacketProblemType
from archipelago_py.packets.server.server_packet import ServerPacket


class InvalidPacket(ServerPacket):
    """
    Sent to clients if the server caught a problem with a packet. This only occurs for errors
    that are explicitly checked for.

    :ivar type: The PacketProblemType that was detected in the packet.
    :ivar original_cmd: The cmd argument of the faulty packet, will be None if the cmd failed to be parsed.
    :ivar text: A descriptive message of the problem at hand.

    `InvalidPacket on github.com/ArchipelagoMW`_.

    .. _InvalidPacket on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#invalidpacket
    """

    cmd: Literal["InvalidPacket"] = "InvalidPacket"
    type: PacketProblemType
    text: str
    original_cmd: str | None = None
