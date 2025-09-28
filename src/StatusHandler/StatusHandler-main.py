import redis
import logging

from src.DiscordSerializedEvents.Serializer import EventSerializer
from src.DiscordSerializedEvents.Events import messageEvents, status

# Setup Redis
redis_client = redis.Redis()
subscriber = redis_client.pubsub()

# Setup Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

subscriber.subscribe('f/discord/startup')
logging.info("📥 Subscribed to Redis channel: f/discord/startup")

for message in subscriber.listen():
    if message['type'] != 'message':
        continue

    try:
        raw_data = message['data'].decode('utf-8')
        logging.debug(f"🔄 Raw Redis message: {raw_data}")

        event = EventSerializer.deserialize(raw_data)

        if event.type == 'startup':
            logging.info(f"📩 Received StartupEvent: {event.event_id}")

            if not event.is_initialized:
                logging.error(f"❌ Event {event.event_id} is not initialized")
                continue

            login_message = (
                "Bot ist erfolgreich gestartet!\n"
                f"ID: {event.client_id}\n"
                f"Name: {event.client_username}"
            )
            
            message_event = messageEvents.SendMessageEvent()
            message_event.initialize(829327103710986245, login_message)
            
            serialized_event = EventSerializer.serialize(message_event)
            result = redis_client.publish('t/discord/message', serialized_event)

            logging.debug(f"📤 Initialized SendMessageEvent: {message_event.event_id}")
            logging.info(f"📤 Published SendMessageEvent to t/discord/message with result: {result}")

        else:
            logging.warning(f"⚠️ Unhandled event type: {event.type}")

    except Exception as e:
        logging.exception(f"❌ Error handling Redis message: {e}")
