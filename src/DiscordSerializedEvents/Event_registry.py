_event_registry = {}

def register_event(event_type: str):
    def wrapper(cls):
        _event_registry[event_type] = cls
        return cls
    return wrapper

def get_event_class(event_type: str):
    return _event_registry.get(event_type)
