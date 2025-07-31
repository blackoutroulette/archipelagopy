import asyncio
from archipelago_py import Client, packets, structs, enums

async def on_print_json(packet: packets.PrintJSON):
    for msg in packet.data:
        if msg.text is not None:
            print(f">> {msg.text}")

async def main():
    client = Client(port=12345)
    # override the default packet handler to print received packets
    client.on_print_json = on_print_json

    # connect to the server
    await client.start()

    # send a connect packet to authenticate
    await client.send(
        packets.Connect(
            version=structs.Version(major=6, minor=0, build=0),
            tags=["AP"],
            name="Link", # slot name
            game="Ocarina of Time"
        )
    )

    # wait for a while to receive packets
    await asyncio.sleep(5)

    # stop the client
    await client.stop()

if __name__ == "__main__":
    asyncio.run(main())