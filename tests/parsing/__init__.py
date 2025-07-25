from pathlib import Path
from typing import TypeVar

from archipelago_py import packets

PATH = Path(__file__).parent

T = TypeVar("T", bound=packets.Packet)
def parse_json(file: Path, packet_cls: type[T]) -> T:

    data: str = file.read_text(encoding="utf-8")
    assert data # Ensure the file is not empty

    packet = packet_cls.model_validate_json(json_data=data)
    assert isinstance(packet, packet_cls)

    return packet