from enum import Enum, unique


@unique
class RolesTypes(Enum):
    admin = 1
    customer = 2
    meterreader = 3  # meter reader
    employee = 4
    senioremployee = 5


@unique
class Portals(Enum):
    bo = 1
    corp = 2
    admin = 3


@unique
class ReadingFilters(Enum):
    CLEAR = 1
    PENDING = 2
    VERIFIED = 3
    REJECTED = 4
