from archipelagopy.enums.permission import Permission
from archipelagopy.structs.struct import Struct


class Permissions(Struct):
    release: Permission
    collect: Permission
    remaining: Permission
