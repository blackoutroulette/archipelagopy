from enum import StrEnum


class Operation(StrEnum):
    """

    :ivar REPLACE: Sets the current value of the key to value.
    :ivar DEFAULT: If the key has no value yet, sets the current value of the key to default
     of the Set's package (value is ignored).
    :ivar ADD: Adds value to the current value of the key, if both the current value and
     value are arrays then value will be appended to the current value.
    :ivar MUL: Multiplies the current value of the key by value.
    :ivar POW: Multiplies the current value of the key to the power of value.
    :ivar MOD: Sets the current value of the key to the remainder after division by value.
    :ivar FLOOR: Floors the current value (value is ignored).
    :ivar CEIL: Ceils the current value (value is ignored).
    :ivar MAX: Sets the current value of the key to value if value is bigger.
    :ivar MIN: Sets the current value of the key to value if value is lower.
    :ivar AND: Applies a bitwise AND to the current value of the key with value.
    :ivar OR: Applies a bitwise OR to the current value of the key with value.
    :ivar XOR: Applies a bitwise Exclusive OR to the current value of the key with value.
    :ivar LEFT_SHIFT: Applies a bitwise left-shift to the current value of the key by value.
    :ivar RIGHT_SHIFT: Applies a bitwise right-shift to the current value of the key by value.
    :ivar REMOVE: List only: removes the first instance of value found in the list.
    :ivar POP: List or Dict: for lists it will remove the index of the value given. for dicts it removes the element
     with the specified key of value.
    :ivar UPDATE: List or Dict: Adds the elements of value to the container if they weren't already present.
     In the case of a Dict, already present keys will have their corresponding values updated.

    `DataStorageOperation on github.com/ArchipelagoMW`_.

    .. _DataStorageOperation on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#datastorageoperation
    """

    REPLACE = "replace"
    DEFAULT = "default"
    ADD = "add"
    MUL = "mul"
    POW = "pow"
    MOD = "mod"
    FLOOR = "floor"
    CEIL = "ceil"
    MAX = "max"
    MIN = "min"
    AND = "and"
    OR = "or"
    XOR = "xor"
    LEFT_SHIFT = "left_shift"
    RIGHT_SHIFT = "right_shift"
    REMOVE = "remove"
    POP = "pop"
    UPDATE = "update"
