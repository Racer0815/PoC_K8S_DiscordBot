from ..Events.baseEvent import BaseEvent
from ..Event_registry import register_event

@register_event("startup")
class StartupEvent(BaseEvent):
    def __init__(self):
        super().__init__("startup")
        self.client_id = None
        self.client_username = None
    
    def initialize(self, client_id, client_username):
        super().initialize()
        self.client_id = client_id
        self.client_username = client_username