# archipelagopy - An API wrapper for Archipelago written in Python
archipelagopy is an API wrapper for Archipelago written in Python using Pydantic and Asyncio.
archipelagopy aims to provide an easy to use, bare minimum implementation and type safety regarding the Archipelago protocol,
allowing developers to create their own clients or servers for the Archipelago network.

# Features
- **Type Safety**: Uses Pydantic and Type Hints for data validation and type safety.
- **Asynchronous**: Built on top of Python's `asyncio` for non-blocking I/O operations.
- **Packet Handling**: Automatically parses packets according to the Archipelago protocol.
- **Callbacks**: Provides a callback system to handle network events.

# How to install

archipelagopy can easily be installed using pip:
```bash
pip install git+https://github.com/blackoutroulette/archipelagopy.git
```
A Python version of 3.10 or higher is required to run archipelagopy.

# How to use

A simple example of how to connect to an Archipelago server and send a connect packet to authenticate:
```python
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
```
Output:
```
>> Link (Team #1) playing Ocarina of Time has joined. Client(6.0.0), ['AP'].
>> Now that you are connected, you can use !help to list commands to run via the server. If your client supports it, you may have additional local commands you can list with /help.
```

A more advanced example can be found in the `examples` directory of the repository, which demonstrates how to handle different packet types.

# Callbacks
Callbacks are used to handle events in the Archipelago client. The `Client` class provides several callback methods that can be overridden to respond to specific events, such as when the client connects to the server, receives a packet, or disconnects.
For a complete list of available callback functions, refer to the `ClientCallbackInterface` class.

Callbacks can be dynamically overridden (monkey patched) like this:
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

# Contributing
Contributions are welcome! Please open an issue about your changes prior to writing a pull request. In the issue please mention if it is a bug fix or feature request.

# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Credits
Documentation is partly or fully taken from the [Archipelago Network Protocol](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md)
