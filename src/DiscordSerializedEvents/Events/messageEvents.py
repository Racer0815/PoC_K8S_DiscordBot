from ..Events.baseEvent import BaseEvent
from ..Event_registry import register_event

@register_event("recv.message")
class RecvMessageEvent(BaseEvent):
    def __init__(self):
        super().__init__("recv.message")
        self.message_id = None
        self.channel_id = None
        self.author_id = None
        self.content = None
        
    def initialize(self, message_id, channel_id, author_id, content):
        super().initialize()
        self.message_id = message_id
        self.channel_id = channel_id
        self.author_id = author_id
        self.content = content

@register_event("send.message")
class SendMessageEvent(BaseEvent):
    def __init__(self):
        super().__init__("send.message")
        self.channel_id = None
        self.content = None
        
    def initialize(self, channel_id, content):
        super().initialize()
        self.channel_id = channel_id
        self.content = content

@register_event("reply.message")
class ReplyMessageEvent(BaseEvent):
    def __init__(self):
        super().__init__("reply.message")
        self.message_id = None
        self.channel_id = None
        self.content = None
        
    def initialize(self, message_id, channel_id, content):
        super().initialize()
        self.message_id = message_id
        self.channel_id = channel_id
        self.content = content