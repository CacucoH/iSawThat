from telethon import events

from db.operations import get_deleted_messages, get_user_settings, get_victims_list
from logic.clients import bot, userbot


async def handle_message_deleted(event: events.MessageDeleted.Event):
    settings = await get_user_settings()
    # track_users = await get_victims_list()

    deleted_message_ids = event.deleted_ids
    print(f"Messages with IDs {deleted_message_ids} were deleted")
    messages = await get_deleted_messages(deleted_message_ids)
    for message in messages:
        # user = next((user for user in track_users if user["user_id"] == message["sender_id"]), None)
        user = await userbot.get_entity(int(message["sender_id"]))
        full_name = user.first_name + (' ' + user.last_name if user.last_name else '')
        location = "личке" if message["chat_id"] == message["sender_id"] else f"чате {message['chat_id']}"
        if message:
            await bot.send_message(int(settings.user_id), f"🚨 **{full_name if user else 'Unknown User'}** ({user.username}) удалил сообщение в **{location}**: {message['content']} от {message['date']}")