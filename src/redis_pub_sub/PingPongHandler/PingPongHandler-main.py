import redis
import logging

from src.DiscordSerializedEvents.Serializer import EventSerializer
from src.DiscordSerializedEvents.Events import messageEvents

# Setup Redis
redis_client = redis.Redis()
subscriber = redis_client.pubsub()

# Setup Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

subscriber.subscribe('f/discord/recv.message')
logging.info("📥 Subscribed to Redis channel: f/discord/recv.message")

for message in subscriber.listen():
    if message['type'] != 'message':
        continue

    try:
        raw_data = message['data'].decode('utf-8')
        logging.debug(f"🔄 Raw Redis message: {raw_data}")

        event = EventSerializer.deserialize(raw_data)

        if event.type == 'recv.message':
            logging.info(f"📩 Received RecvMessageEvent: {event.event_id}")

            if not event.is_initialized:
                logging.error(f"❌ Event {event.event_id} is not initialized")
                continue

            if event.content.lower() == 'ping':
                logging.info(f"👋 Received 'ping' from author {event.author_id}")

                reply_event = messageEvents.ReplyMessageEvent()
                reply_event.initialize(event.message_id, event.channel_id, 'pong')

                serialized_event = EventSerializer.serialize(reply_event)
                result = redis_client.publish('t/discord/message', serialized_event)

                logging.debug(f"📤 Initialized ReplyMessageEvent: {reply_event.event_id}")
                logging.info(f"📤 Published ReplyMessageEvent to t/discord/message with result: {result}")

        else:
            logging.warning(f"⚠️ Unhandled event type: {event.type}")

    except Exception as e:
        logging.exception(f"❌ Error handling Redis message: {e}")
