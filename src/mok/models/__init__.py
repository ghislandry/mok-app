from enum import Enum, unique


@unique
class RolesTypes(Enum):
    admin = 1
    customer = 2
    meterreader = 3  # meter reader
    employee = 4
    senioremployee = 5
