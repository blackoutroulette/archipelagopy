import json

import pytest

from archipelago_py import packets
from archipelago_py.packets import PACKET_TYPE_ADAPTER, ServerPacket


def test_bounced():
    js = json.dumps([{
        'cmd': 'Bounced',
        'slots': [0, 1],
        'data': {'key': 'value'},
        'games': ['Game1', 'Game2'],
        'tags': ['AP', 'DeathLink']
    }])

    packet: ServerPacket = PACKET_TYPE_ADAPTER.validate_json(js)

    assert isinstance(packet, list)
    assert len(packet) == 1
    assert isinstance(packet[0], packets.Bounced)


def test_connected():
    js = json.dumps([{
        'cmd': 'Connected',
        'team': 0,
        'slot': 1,
        'hint_points': 10,
        'slot_info': {
            0: {'game': 'Game1', 'name': 'Player1', 'type': 1, 'group_members': []},
            1: {'game': 'Game2', 'name': 'Player2', 'type': 0, 'group_members': []},
            2: {'game': '', 'name': 'Team1', 'type': 2, 'group_members': [0]}
        },
        'players': [
            {'name': 'Player1', 'team': 0, 'slot': 0, 'alias': 'P1'},
            {'name': 'Player2', 'team': 0, 'slot': 1, 'alias': 'P2'}
        ],
        'missing_location': [100, 200],
        'checked_location': [300, 400],
        'slot_data': {'key': 'value'}
    }])

    packet: ServerPacket = PACKET_TYPE_ADAPTER.validate_json(js)

    assert isinstance(packet, list)
    assert len(packet) == 1
    assert isinstance(packet[0], packets.Connected)