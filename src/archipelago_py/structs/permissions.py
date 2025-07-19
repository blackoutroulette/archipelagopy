from archipelago_py.enums.permission import Permission
from archipelago_py.structs.struct import Struct


class Permissions(Struct):
    release: Permission
    collect: Permission
    remaining: Permission
