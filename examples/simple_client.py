import asyncio
from archipelago_py import Client, packets, structs, enums

async def on_packet_handler(packet: packets.ServerPacket):
    print(f"Received packet: {packet}")

async def main():
    client = Client(port=62805)
    # override the default packet handler to print received packets
    client.on_packet = on_packet_handler

    # connect to the server
    await client.start()

    # send a connect packet to authenticate
    await client.send(
        packets.Connect(
            version=structs.Version(major=6, minor=0, build=0),
            tags=("AP",),
            name="Link",
            game="Ocarina of Time",
            items_handling=enums.ItemHandlingFlag.OWN_WORLD | enums.ItemHandlingFlag.OTHER_WORLDS,
        )
    )

    # wait for a while to receive packets
    await asyncio.sleep(5)

    # stop the client
    await client.stop()

if __name__ == "__main__":
    asyncio.run(main())