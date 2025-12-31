from typing import Literal

from archipelagopy.enums.client_status import ClientStatus
from archipelagopy.packets.client.client_packet import ClientPacket


class StatusUpdate(ClientPacket):
    """
    Sent to the server to update on the sender's status. Examples include readiness or goal completion. (Example: defeated Ganon in A Link to the Past)

    :ivar status: One of Client States. Send as int. Follow the link for more information.

    `StatusUpdate on github.com/ArchipelagoMW`_.

    .. _StatusUpdate on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#statusupdate
    """

    cmd: Literal["StatusUpdate"] = "StatusUpdate"
    status: ClientStatus
