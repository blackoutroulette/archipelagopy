from pathlib import Path

import pytest

from archipelago_py import packets, enums
from tests.parsing import PATH, parse_json


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/countdown").glob("*.json")], ids=lambda p: p.name)
def test_countdown(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.COUNTDOWN


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/tags_changed").glob("*.json")], ids=lambda p: p.name)
def test_tags_changed(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.TAGS_CHANGED


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/join").glob("*.json")], ids=lambda p: p.name)
def test_join(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.JOIN


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/tutorial").glob("*.json")], ids=lambda p: p.name)
def test_tutorial(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.TUTORIAL


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/chat").glob("*.json")], ids=lambda p: p.name)
def test_chat(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.CHAT


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/item_send").glob("*.json")], ids=lambda p: p.name)
def test_item_send(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.ITEM_SEND


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/part").glob("*.json")], ids=lambda p: p.name)
def test_part(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.PART


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/hint").glob("*.json")], ids=lambda p: p.name)
def test_hint(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.HINT


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/goal").glob("*.json")], ids=lambda p: p.name)
def test_goal(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.GOAL


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/release").glob("*.json")], ids=lambda p: p.name)
def test_release(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.RELEASE


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/command_result").glob("*.json")], ids=lambda p: p.name)
def test_command_result(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.COMMAND_RESULT


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/item_cheat").glob("*.json")], ids=lambda p: p.name)
def test_item_cheat(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.ITEM_CHEAT


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/no_type").glob("*.json")], ids=lambda p: p.name)
def test_no_type(file: Path):
    packet = parse_json(file, packets.PrintJSON)
    assert packet.type is None