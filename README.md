# ArchipelagoPy
ArchipelagoPy is a Python library which implements the Archipelago Network Protocol by parsing all network data into Python classes using Pydantic and Asyncio.
ArchipelagoPy aims to provide an easy to use, bare minimum implementation and type safety regarding the Archipelago protocol,
allowing developers to create their own clients or servers for the Archipelago network.

# How to install

ArchipelagoPy can easily be installed using pip:
```bash
pip install git+https://github.com/blackoutroulette/ArchipelagoPy.git
```

# How to use

A simple example of how to connect to an Archipelago server and send a connect packet to authenticate:
```python
import asyncio
from archipelago_py import Client, packets, structs, enums

async def on_packet_handler(packet: packets.ServerPacket):
    print(f"Received packet: {packet}")

async def main():
    client = Client(port=12345)
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
```

A more advanced example can be found in the `examples` directory of the repository, which demonstrates how to handle different packet types.

# Callbacks
Callbacks are used to handle events in the Archipelago client. The `Client` class provides several callback methods that can be overridden to respond to specific events, such as when the client connects to the server, receives a packet, or disconnects.
For a complete list of available callback functions, refer to the `ClientCallbackInterface` class.

Callbacks can be dynamically overridden like this:
```python
from archipelago_py import Client

async def on_ready():
    print("Connected to the server")

client = Client(port=12345)
client.on_ready = on_ready
```

A more clean approach is to subclass the `Client` class and override the methods:
```python
from archipelago_py import Client, packets

class MyClient(Client):
    async def on_connected(self, packet: packets.Connected):
        print("Authenticated to the server")
        # You can send packets here or perform other actions
```

# Further Documentation
For further documentation please refer to the [Archipelago Network Protocol](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md)