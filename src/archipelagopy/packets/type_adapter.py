from typing import Annotated, Final, Union

from pydantic import TypeAdapter, Field

from archipelagopy import packets

ServerPacketUnionType: Union = (
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

ClientPacketUnionType: Union = (
        packets.Bounce |
        packets.Connect |
        packets.ConnectUpdate |
        packets.Get |
        packets.GetDataPackage |
        packets.LocationChecks |
        packets.LocationScouts |
        packets.Say |
        packets.Set |
        packets.SetNotify |
        packets.StatusUpdate |
        packets.Sync |
        packets.UpdateHint
)

PacketUnionType: Union = ServerPacketUnionType | ClientPacketUnionType

PACKET_TYPE_ADAPTER: Final[TypeAdapter] = TypeAdapter(
    list[Annotated[PacketUnionType, Field(discriminator="cmd")]]
)
