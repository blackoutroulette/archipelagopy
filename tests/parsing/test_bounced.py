from pathlib import Path

import pytest

from archipelago_py import packets
from tests.parsing import PATH, parse_json


@pytest.mark.parametrize("file", [p for p in (PATH/"test_bounced").glob("*.json")], ids=lambda p: p.name)
def test_model(file: Path):
    parse_json(file, packets.Bounced)
