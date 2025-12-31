from archipelagopy.enums.operation import Operation
from archipelagopy.structs.struct import Struct


class DataStorageOperation(Struct):
    """
    A DataStorageOperation manipulates or alters the value of a key in the data storage.
    If the operation transforms the value from one state to another then the current value
    of the key is used as the starting point otherwise the Set's package default is used
    if the key does not exist on the server already. DataStorageOperations consist of an object
    containing both the operation to be applied, as well as the value to be used for that operation.

    :ivar operation: The operation to apply to the value.
    :ivar value: The value to use for the operation.

    `DataStorageOperation on github.com/ArchipelagoMW`_.

    .. _DataStorageOperation on github.com/ArchipelagoMW:
        https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md#datastorageoperation
    """

    operation: Operation
    value: int
