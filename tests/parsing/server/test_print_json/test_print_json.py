from pathlib import Path
from typing import Final

import pytest

from archipelagopy import packets
from archipelagopy.enums import PrintJSONType
from tests.parsing import load_data, helper_test_packet_adapter, helper_test_parse_json

TEST_DATA: Final[list[tuple[PrintJSONType | None, str]]] = [
    (PrintJSONType.CHAT, "chat"),
    (PrintJSONType.COMMAND_RESULT, "command_result"),
    (PrintJSONType.COUNTDOWN, "countdown"),
    (PrintJSONType.GOAL, "goal"),
    (PrintJSONType.HINT, "hint"),
    (PrintJSONType.ITEM_CHEAT, "item_cheat"),
    (PrintJSONType.ITEM_SEND, "item_send"),
    (PrintJSONType.JOIN, "join"),
    (None, "no_type"),
    (PrintJSONType.PART, "part"),
    (PrintJSONType.RELEASE, "release"),
    (PrintJSONType.TAGS_CHANGED, "tags_changed"),
    (PrintJSONType.TUTORIAL, "tutorial")
]

FLAT_TEST_DATA: Final[list[tuple[PrintJSONType | None, tuple[Path, str]]]] = [
    (t[0], d) for t in TEST_DATA for d in load_data(Path(__file__).parent/t[1])
]

def id_func(data: tuple[PrintJSONType | None, tuple[Path, str]]) -> str:
    print_json_type, (path, _) = data
    return f"{packets.PrintJSON.__name__}/{print_json_type}/{path.name}"

@pytest.mark.parametrize("data", FLAT_TEST_DATA, ids=id_func)
def test_model(data: tuple[PrintJSONType | None, tuple[Path, str]]):
    print_json_type, (_, json_data) = data
    packet = helper_test_parse_json(json_data, packets.PrintJSON)
    assert packet.type == print_json_type


@pytest.mark.parametrize("data", FLAT_TEST_DATA, ids=id_func)
def test_packet_adapter(data: tuple[PrintJSONType | None, tuple[Path, str]]):
    _, (_, json_data) = data
    helper_test_packet_adapter(json_data, packets.PrintJSON)