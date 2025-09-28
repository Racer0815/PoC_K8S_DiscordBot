import os
import redis
import discord
import logging
import asyncio
import threading

from src.DiscordSerializedEvents.Events import status, messageEvents
from src.DiscordSerializedEvents.Serializer import EventSerializer

intents = discord.Intents.all()
redis_client = redis.Redis()
discord_client = discord.Bot(intents=intents)

logging.basicConfig(level=logging.DEBUG)


@discord_client.event
async def on_ready():
    logging.info(f'✅ Logged in as {discord_client.user} (ID: {discord_client.user.id})')
    logging.info(f"Guilds: {len(discord_client.guilds)}")
    logging.info("Starting Redis message sender thread...")

    threading.Thread(target=redis_listener_thread, daemon=True).start()

    startup_event = status.StartupEvent()
    startup_event.initialize(discord_client.user.id, discord_client.user.name)
    serialized_event = EventSerializer.serialize(startup_event)
    result = redis_client.publish('f/discord/startup', serialized_event)
    logging.info(f"📤 Published StartupEvent: {serialized_event} with result: {result}")


@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    logging.info(f"📥 Message from {message.author}: {message.content}")
    event = messageEvents.RecvMessageEvent()
    event.initialize(message.id, message.channel.id, message.author.id, message.content)
    serialized_event = EventSerializer.serialize(event)
    result = redis_client.publish('f/discord/recv.message', serialized_event)
    logging.info(f"📤 Published RecvMessageEvent: {serialized_event} with result: {result}")


def redis_listener_thread():
    logging.info("🔄 Redis listener started in separate thread.")
    subscriber = redis_client.pubsub()
    subscriber.subscribe('t/discord/message')
    logging.info("✅ Subscribed to Redis channel: t/discord/message")

    for message in subscriber.listen():
        if message['type'] == 'message':
            try:
                raw = message['data']
                data = raw.decode('utf-8')
                logging.debug(f"📨 Redis received message: {data}")
                event = EventSerializer.deserialize(data)

                if not event.is_initialized:
                    logging.error(f"❌ Event {event.event_id} is not initialized")
                    continue

                asyncio.run_coroutine_threadsafe(handle_event(event), discord_client.loop)

            except Exception as e:
                logging.exception(f"❌ Error in Redis listener: {e}")


async def handle_event(event):
    if event.type == 'send.message':
        channel = discord_client.get_channel(event.channel_id)
        if channel:
            await channel.send(event.content)
        else:
            logging.warning(f"⚠️ Channel {event.channel_id} not found")

    elif event.type == 'reply.message':
        channel = discord_client.get_channel(event.channel_id)
        if channel:
            try:
                msg = await channel.fetch_message(event.message_id)
                await msg.reply(event.content)
            except discord.NotFound:
                logging.warning(f"⚠️ Message {event.message_id} not found")
        else:
            logging.warning(f"⚠️ Channel {event.channel_id} not found")

    else:
        logging.warning(f"⚠️ Unknown event type: {event.type}")


if __name__ == "__main__":
    discord_client.run(os.getenv('DISCORD_TOKEN'))