from enum import Enum

class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    SKIPPED = "SKIPPED"