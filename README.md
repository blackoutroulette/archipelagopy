# archipelagopy - An API wrapper for Archipelago written in Python
archipelagopy is an API wrapper for the [Archipelago](https://archipelago.gg/) Randomizer network, written in Python.
It lets you build clients that connect to Archipelago multiworld servers to send and receive items, chat messages, and game state updates.

If you're new to Archipelago, see the [Archipelago setup guide](https://archipelago.gg/tutorial/Archipelago/setup/en) to get a server running.

# Features
- **Type Safety**: Uses [Pydantic](https://docs.pydantic.dev/) for automatic data validation.
- **Asynchronous**: Built on Python's [`asyncio`](https://docs.python.org/3/library/asyncio.html) for non-blocking I/O operations.
- **Packet Handling**: Automatically parses packets according to the Archipelago protocol.
- **Callbacks**: Provides a callback system to handle network events.
- **Auto-Reconnect**: Optional automatic reconnection with exponential backoff.

# Prerequisites

- Python 3.10 or higher
- Basic familiarity with Python's `async`/`await` syntax. If you haven't used asyncio before, see the [asyncio documentation](https://docs.python.org/3/library/asyncio.html) for an introduction.

# How to install

archipelagopy can be installed using pip:
```bash
pip install archipelagopy
```

# How to use

A simple example of how to connect to an Archipelago server and send a connect packet to authenticate:

```python
import asyncio
from archipelagopy import Client, packets, structs, enums


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
            name="Link",  # slot name
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

## Callback overview

The "Async" column indicates whether the callback must be defined with `async def` (Yes) or regular `def` (No).

| Callback | Async | Parameter | Description |
|---|---|---|---|
| `on_ready()` | Yes | — | WebSocket connection established, ready to send/receive |
| `on_connect_error(error)` | No | Connection error | Connection attempt failed (e.g. refused, timeout) |
| `on_connection_closed(close_code)` | No | Close code | Server closed the connection |
| `on_received(packet)` | Yes | `str` | Raw JSON string received (before parsing) |
| `on_packet(packet)` | Yes | `ServerPacket` | Any parsed packet (fires before specific handlers) |
| `on_connected(packet)` | Yes | `Connected` | Authentication successful |
| `on_connection_refused(packet)` | Yes | `ConnectionRefused` | Authentication rejected |
| `on_room_info(packet)` | Yes | `RoomInfo` | Server info received on connect |
| `on_room_update(packet)` | Yes | `RoomUpdate` | Room state changed |
| `on_print_json(packet)` | Yes | `PrintJSON` | Formatted message (chat, hints, etc.) |
| `on_received_items(packet)` | Yes | `ReceivedItems` | Items sent to player |
| `on_location_info(packet)` | Yes | `LocationInfo` | Location scout results |
| `on_data_package(packet)` | Yes | `DataPackage` | Game data received |
| `on_bounced(packet)` | Yes | `Bounced` | Bounced message from another client |
| `on_retrieved(packet)` | Yes | `Retrieved` | Data storage retrieval response |
| `on_set_reply(packet)` | Yes | `SetReply` | Data storage set response |
| `on_invalid_packet(packet)` | Yes | `InvalidPacket` | Server reports a malformed packet |

`on_connect_error` and `on_connection_closed` are the only two synchronous callbacks (defined with `def` instead of `async def`). All other callbacks are async and must use `async def`.

## Overriding callbacks

Callbacks can be replaced by assigning a new function directly on the client instance:

```python
from archipelagopy import Client


async def on_ready():
    print("Connected to the server")


client = Client(port=12345)
client.on_ready = on_ready  # replaces the default (empty) on_ready
```

The client checks that replacements match the original type: `async def` callbacks must be replaced with `async def` functions, and `def` callbacks with `def` functions. A mismatch raises a `TypeError`.

A cleaner approach is to subclass the `Client` class and override the methods:

```python
from archipelagopy import Client, packets


class MyClient(Client):
    async def on_connected(self, packet: packets.Connected):
        print("Authenticated to the server")
        # You can send packets here or perform other actions
```

# Connection lifecycle

Here is the typical sequence of events when connecting to an Archipelago server:

1. You call `client.start()` to initiate the WebSocket connection
2. Once connected, `on_ready()` fires — the connection is open but you haven't authenticated yet
3. The server automatically sends a `RoomInfo` packet with server details, triggering `on_room_info()`
4. You send a `Connect` packet with your slot name and game to authenticate
5. The server responds with either `Connected` (success) or `ConnectionRefused` (wrong password, invalid slot, etc.)
6. During the session, incoming packets are dispatched in order: `on_received()` (raw JSON string) -> `on_packet()` (parsed packet, all types) -> the specific handler (e.g. `on_print_json()`)
7. When the server disconnects, `on_connection_closed()` fires with a close code indicating the reason

# Auto-reconnect

When `auto_reconnect=True`, the client automatically retries the connection:
- On `ConnectionRefusedError`: retries with exponential backoff (up to 60 seconds)
- On server going to standby (`CloseCode.GOING_AWAY`): retries immediately

```python
client = Client(port=12345, auto_reconnect=True)
```

# Further documentation

For the full callback reference and additional guides, see the [Wiki](https://github.com/blackoutroulette/archipelagopy/wiki).

For protocol details, refer to the [Archipelago Network Protocol](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md).

# Contributing
Contributions are welcome! Please open an issue about your changes prior to writing a pull request. In the issue please mention if it is a bug fix or feature request.

# License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

# Credits
Documentation is partly or fully taken from the [Archipelago Network Protocol](https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md)

# AI Disclosure
Claude Code was used to generate the documentation (partly this README and the GitHub wiki), to review the codebase and identify bugs, and co-authored the PyPI publish workflow. The library's architecture, implementation, and test suite were written by the maintainer.