import json

import pytest

from archipelago_py import packets, structs
from archipelago_py.enums import ConnectionRefusedFlag, PacketProblemType, NetworkItemFlag
from archipelago_py.packets import PACKET_TYPE_ADAPTER, ServerPacket
from archipelago_py.structs.data_package_data import DataPackageData


def test_bounced():
    js = [{
        'cmd': 'Bounced',
        'slots': [0, 1],
        'data': {'key': 'value'},
        'games': ['Game1', 'Game2'],
        'tags': ['AP', 'DeathLink']
    }]

    packet: ServerPacket = PACKET_TYPE_ADAPTER.validate_json(
        json.dumps(js)
    )

    assert isinstance(packet, list)
    assert len(packet) == 1
    assert isinstance(packet[0], packets.Bounced)

    j = js[0]
    p: packets.Bounced = packet[0]

    # command
    assert p.cmd == 'Bounced'
    # slots
    assert p.slots == tuple(j['slots'])
    # data
    assert p.data == j['data']
    # games
    assert p.games == tuple(j['games'])
    # tags
    assert p.tags == tuple(j['tags'])


def test_connected():
    js = [{
        'cmd': 'Connected',
        'team': 0,
        'slot': 1,
        'hint_points': 10,
        'slot_info': {
            0: {'game': 'Game1', 'name': 'Player1', 'type': 1, 'group_members': [], "class": "NetworkSlot"},
            1: {'game': 'Game2', 'name': 'Player2', 'type': 0, 'group_members': [], "class": "NetworkSlot"},
            2: {'game': '', 'name': 'Team1', 'type': 2, 'group_members': [0], "class": "NetworkSlot"}
        },
        'players': [
            {'name': 'Player1', 'team': 0, 'slot': 0, 'alias': 'P1', "class": "NetworkPlayer"},
            {'name': 'Player2', 'team': 0, 'slot': 1, 'alias': 'P2', "class": "NetworkPlayer"}
        ],
        'missing_location': [100, 200],
        'checked_location': [300, 400],
        'slot_data': {'key': 'value'}
    }]

    packet: ServerPacket = PACKET_TYPE_ADAPTER.validate_json(
        json.dumps(js)
    )

    assert isinstance(packet, list)
    assert len(packet) == 1
    assert isinstance(packet[0], packets.Connected)

    j = js[0]
    p: packets.Connected = packet[0]

    # command
    assert j['cmd'] == p.cmd
    # team
    assert j['team'] == p.team
    # slot
    assert j['slot'] == p.slot
    # hint points
    assert j['hint_points'] == p.hint_points

    # slot info
    for k, v in j['slot_info'].items():
        assert k in p.slot_info
        assert isinstance(p.slot_info[k], structs.NetworkSlot)
        assert p.slot_info[k].game == v['game']
        assert p.slot_info[k].name == v['name']
        assert p.slot_info[k].type == v['type']
        assert p.slot_info[k].group_members == tuple(v['group_members'])

    # players
    for i, player in enumerate(j['players']):
        assert i < len(p.players)
        assert isinstance(p.players[i], structs.NetworkPlayer)
        assert p.players[i].name == player['name']
        assert p.players[i].team == player['team']
        assert p.players[i].slot == player['slot']
        assert p.players[i].alias == player['alias']

    # missing locations
    assert p.missing_location == tuple(j['missing_location'])
    # checked locations
    assert p.checked_location == tuple(j['checked_location'])
    # slot data
    assert p.slot_data == j['slot_data']


@pytest.mark.parametrize("error", [
    ConnectionRefusedFlag.INVALID_SLOT,
    ConnectionRefusedFlag.INVALID_GAME,
    ConnectionRefusedFlag.INCOMPATIBLE_VERSION,
    ConnectionRefusedFlag.INVALID_PASSWORD,
    ConnectionRefusedFlag.INVALID_ITEMS_HANDLING
])
def test_connection_refused(error: ConnectionRefusedFlag):
    js = [{
        'cmd': 'ConnectionRefused',
        'errors': [error.value]
    }]

    packet: ServerPacket = PACKET_TYPE_ADAPTER.validate_json(
        json.dumps(js)
    )

    assert isinstance(packet, list)
    assert len(packet) == 1
    assert isinstance(packet[0], packets.ConnectionRefused)

    p: packets.ConnectionRefused = packet[0]
    # command
    assert p.cmd == 'ConnectionRefused'
    # errors
    assert p.errors == (error,)


def test_data_package():
    js = [{
        'cmd': 'DataPackage',
        'data': {
            "games": {
                "Game1": {
                    'item_name_to_id': {"Item1": 1, "Item2": 2},
                    'location_name_to_id': {"Location1": 100, "Location2": 200},
                    'checksum': "abc123",
                    "class": "GameData"
                },
            }
        }
    }]

    packet: ServerPacket = PACKET_TYPE_ADAPTER.validate_json(
        json.dumps(js)
    )

    assert isinstance(packet, list)
    assert len(packet) == 1
    assert isinstance(packet[0], packets.DataPackage)

    j = js[0]
    p: packets.DataPackage = packet[0]

    # command
    assert p.cmd == 'DataPackage'
    # data
    assert isinstance(p.data, DataPackageData)
    for game, data in j['data']['games'].items():
        assert game in p.data.games
        assert isinstance(p.data.games[game], structs.GameData)
        assert p.data.games[game].item_name_to_id == data['item_name_to_id']
        assert p.data.games[game].location_name_to_id == data['location_name_to_id']
        assert p.data.games[game].checksum == data['checksum']


@pytest.mark.parametrize("type_", [
    PacketProblemType.ARGUMENTS,
    PacketProblemType.CMD
])
def test_invalid_packet(type_: PacketProblemType):
    js = [{
        'cmd': 'InvalidPacket',
        'type': type_.value,
        'text': "123abc",
        'original_cmd': 'Connect'
    }]

    packet: ServerPacket = PACKET_TYPE_ADAPTER.validate_json(
        json.dumps(js)
    )

    assert isinstance(packet, list)
    assert len(packet) == 1
    assert isinstance(packet[0], packets.InvalidPacket)

    j = js[0]
    p: packets.InvalidPacket = packet[0]

    # command
    assert p.cmd == 'InvalidPacket'
    # type
    assert p.type == type_
    # text
    assert p.text == j['text']
    # original_cmd
    assert p.original_cmd == j['original_cmd']


def test_location_info():
    js = [{
        'cmd': 'LocationInfo',
        'locations': [
            {"item": 0, "location": 4, "player": 8, "flags": NetworkItemFlag.COMMON.value, "class": "NetworkItem"},
            {"item": 1, "location": 5, "player": 9, "flags": NetworkItemFlag.MINOR.value, "class": "NetworkItem"},
            {"item": 2, "location": 6, "player": 10, "flags": NetworkItemFlag.MAJOR.value, "class": "NetworkItem"},
            {"item": 3, "location": 7, "player": 11, "flags": NetworkItemFlag.TRAP.value, "class": "NetworkItem"},
        ]
    }]

    packet: ServerPacket = PACKET_TYPE_ADAPTER.validate_json(
        json.dumps(js)
    )

    assert isinstance(packet, list)
    assert len(packet) == 1
    assert isinstance(packet[0], packets.LocationInfo)

    j = js[0]
    p: packets.LocationInfo = packet[0]

    # command
    assert p.cmd == 'LocationInfo'
    # locations
    assert isinstance(p.locations, tuple)
    for i, loc in enumerate(j['locations']):
        assert i < len(p.locations)
        assert isinstance(p.locations[i], structs.NetworkItem)
        assert p.locations[i].item == loc['item']
        assert p.locations[i].location == loc['location']
        assert p.locations[i].player == loc['player']
        assert p.locations[i].flags == NetworkItemFlag(loc['flags'])


