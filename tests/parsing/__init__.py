from pathlib import Path
from typing import TypeVar

from archipelago_py import packets

PATH = Path(__file__).parent

T = TypeVar("T", bound=packets.Packet)
def helper_test_parse_json(data: str, packet_cls: type[T]) -> T:

    packet = packet_cls.model_validate_json(json_data=data)
    assert isinstance(packet, packet_cls)

    return packet

def helper_test_packet_adapter(data: str, packet_cls: type[T]) -> T:
    packet = packets.PACKET_TYPE_ADAPTER.validate_json(f"[{data}]")

    assert isinstance(packet, list)
    assert len(packet) == 1
    assert isinstance(packet[0], packet_cls)

    return packet[0]

def load_data(folder: Path, recursive: bool = False) -> list[tuple[Path, str]]:
    files = folder.rglob("*.json") if recursive else folder.glob("*.json")
    assert files, f"No JSON files found in {PATH/folder}"

    data = [
        (p, p.read_text("utf-8"))
        for p
        in files
    ]

    for (p, d) in data:
        assert d, f"File {p} is empty"

    return data
