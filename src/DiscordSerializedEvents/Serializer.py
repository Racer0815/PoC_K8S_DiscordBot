import json
from .Event_registry import get_event_class

class EventSerializer:
    @staticmethod
    def serialize(event_obj):
        return json.dumps(event_obj.to_dict())

    @staticmethod
    def deserialize(json_str):
        data = json.loads(json_str)
        event_type = data.get("type")
    
        event_class = get_event_class(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
    
        return event_class.from_dict(data)
