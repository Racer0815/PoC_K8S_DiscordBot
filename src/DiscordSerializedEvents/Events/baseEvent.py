import uuid
from datetime import datetime, timezone

class BaseEvent:
    def __init__(self, event_type: str):
        self.is_initialized = False
        self.event_id = None
        self.created_at = None
        self.type = event_type

    def initialize(self):
        self.is_initialized = True
        self.event_id = str(uuid.uuid4())
        self.created_at = datetime.now(tz=timezone.utc).timestamp()

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls.__new__(cls)
        obj.__dict__.update(data)
        return obj
