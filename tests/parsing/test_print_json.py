from pathlib import Path

import pytest

from archipelago_py import packets, enums
from tests.parsing import PATH

@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/countdown").glob("*.json")])
def test_countdown(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.COUNTDOWN


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/tags_changed").glob("*.json")])
def test_tags_changed(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.TAGS_CHANGED


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/join").glob("*.json")])
def test_join(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.JOIN


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/tutorial").glob("*.json")])
def test_tutorial(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.TUTORIAL


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/chat").glob("*.json")])
def test_chat(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.CHAT


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/item_send").glob("*.json")])
def test_item_send(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.ITEM_SEND


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/part").glob("*.json")])
def test_part(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.PART


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/hint").glob("*.json")])
def test_hint(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.HINT


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/goal").glob("*.json")])
def test_goal(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.GOAL


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/release").glob("*.json")])
def test_release(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.RELEASE


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/command_result").glob("*.json")])
def test_command_result(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.COMMAND_RESULT


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/item_cheat").glob("*.json")])
def test_item_cheat(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type == enums.PrintJSONType.ITEM_CHEAT


@pytest.mark.parametrize("file", [p for p in (PATH/"test_print_json/no_type").glob("*.json")])
def test_no_type(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.PrintJSON.model_validate_json(json_data=data)
    assert isinstance(packet, packets.PrintJSON)
    assert packet.type is None