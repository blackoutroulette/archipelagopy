import websockets.exceptions

from archipelago_py import packets

OnConnectExceptionUnion = (
    websockets.exceptions.InvalidURI |
    websockets.exceptions.InvalidHandshake |
    websockets.exceptions.InvalidProxy |
    ConnectionRefusedError |
    TimeoutError |
    OSError
)

class ClientCallbackInterface:

    def __init__(self):
        if type(self) is ClientCallbackInterface:
            raise TypeError("CallbackInterface is an abstract class and cannot be instantiated directly.")

    async def on_ready(self):
        """
        Called when the client is ready to send and receive packets.
        """

    def on_connect_error(self, error: OnConnectExceptionUnion):
        """
        Called when an error occurs during the connection to the server
        """

    def on_connection_closed(self, close_code: websockets.CloseCode):
        """
        Called when the connection is closed by the server.
        websockets.CloseCode.NORMAL_CLOSURE usually indicates that a sent packet is malformed causing
        the server to close the connection because of an internal exception being thrown. The exact cause
        can only be checked inside the server console on the lobby webpage if you are the creator of the lobby.
        websockets.CloseCode.GOING_AWAY indicates that the server is shutting down.
        """

    async def on_received(self, packet: str):
        """
        Called when a raw packet is received from the server. This should be a json string.
        :param packet: The raw unparsed json packet received from the server.
        """

    async def on_packet(self, packet: packets.ServerPacket):
        """
        Called when a packet is received from the server.
        This is a wildcard method that can be overridden to handle any packet type and
        will be called before any specific packet handler methods. Changes made to the packet
        in this method will be reflected in the specific packet handler methods.
        """

    async def on_bounced(self, packet: packets.Bounced):
        """
        Called when the client is bounced to a different server.
        """

    async def on_connected(self, packet: packets.Connected):
        """
        Called when the client has successfully connected to the server.
        """

    async def on_connection_refused(self, packet: packets.ConnectionRefused):
        """
        Called when the connection to the server is refused.
        """

    async def on_data_package(self, packet: packets.DataPackage):
        """
        Called when a DataPackage packet is received.
        This is used to send and receive data between the client and server.
        """

    async def on_invalid_packet(self, packet: packets.InvalidPacket):
        """
        Called when an invalid packet is received.
        """

    async def on_location_info(self, packet: packets.LocationInfo):
        """
        Called when the client receives location information from the server.
        This is used to update the client's location in the game.
        """

    async def on_print_json(self, packet: packets.PrintJSON):
        """
        Called when a PrintJSON packet is received.
        This is used for debugging and logging purposes.
        """

    async def on_received_items(self, packet: packets.ReceivedItems):
        """
        Called when the client receives items from the server.
        This is used to update the client's inventory.
        """

    async def on_retrieved(self, packet: packets.Retrieved):
        """
        Called when the client retrieves items from the server.
        This is used to update the client's inventory after a retrieval action.
        """

    async def on_room_info(self, packet: packets.RoomInfo):
        """
        Called when the client receives room information from the server.
        This is used to update the client's room state.
        """

    async def on_room_update(self, packet: packets.RoomUpdate):
        """
        Called when the client receives an update to the room state.
        This is used to update the client's view of the room.
        """

    async def on_set_reply(self, packet: packets.SetReply):
        """
        Called when the client receives a reply to a set command.
        This is used to confirm that a set command was successful.
        """
