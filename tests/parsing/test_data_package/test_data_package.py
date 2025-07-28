from pathlib import Path
from typing import Final

import pytest

from archipelago_py import packets
from tests.parsing import load_data, helper_test_packet_adapter, helper_test_parse_json

TEST_DATA: Final[list[tuple[Path, str]]] = load_data(Path(__file__).parent)
PACKET_TYPE: Final = packets.DataPackage

@pytest.mark.parametrize("data", TEST_DATA, ids=lambda p: p[0].name)
def test_model(data: tuple[Path, str]):
    helper_test_parse_json(data[1], PACKET_TYPE)

@pytest.mark.parametrize("data", TEST_DATA, ids=lambda p: p[0].name)
def test_packet_adapter(data: tuple[Path, str]):
    helper_test_packet_adapter(data[1], PACKET_TYPE)