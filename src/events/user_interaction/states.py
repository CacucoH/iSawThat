from enum import Enum

class States(Enum):
    DEFAULT = "DEFAULT"
    PENDING_LIST_UPDATE = "PENDING_LIST_UPDATE"
    LIST_UPDATED = "LIST_UPDATED"