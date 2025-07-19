from typing import Literal

from pydantic import BaseModel


class Packet(BaseModel):
    cmd: Literal["Packet"]
