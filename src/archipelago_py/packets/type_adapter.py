from typing import Annotated, Final

from pydantic import TypeAdapter, Field

from archipelago_py import packets

ServerPacketUnionType = (
        packets.Bounced |
        packets.Connected |
        packets.ConnectionRefused |
        packets.DataPackage |
        packets.InvalidPacket |
        packets.LocationInfo |
        packets.PrintJSON |
        packets.ReceivedItems |
        packets.Retrieved |
        packets.RoomInfo |
        packets.RoomUpdate |
        packets.SetReply
)

PACKET_TYPE_ADAPTER: Final[TypeAdapter] = TypeAdapter(
    list[Annotated[ServerPacketUnionType, Field(discriminator="cmd")]]
)
