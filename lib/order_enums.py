from enum import Enum


class TaskListOrderValue(Enum):
    DEFAULT = 0
    ASCENDING = 1
    DESCENDING = 2
    RANDOM = 3


class TaskOrderKey(Enum):
    DEFAULT = 0
    NAME = 1
    STATUS = 2
    PRIORITY = 3


class TaskOrderValue(Enum):
    DEFAULT = 0
    ASCENDING = 1
    DESCENDING = 2
    RANDOM = 3

