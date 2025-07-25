from pathlib import Path

import pytest

from archipelago_py import packets
from tests.parsing import PATH

@pytest.mark.parametrize("file", [p for p in (PATH/"test_connected").glob("*.json")])
def test_model(file: Path):

    data: str = file.read_text(encoding="utf-8")
    assert data  # Ensure the file is not empty

    packet = packets.Connected.model_validate_json(json_data=data)
    assert isinstance(packet, packets.Connected)
