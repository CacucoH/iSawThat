from telethon import TelegramClient

async def get_user_info(client: TelegramClient, users):
    """Fetches the full user information of the current user."""
    userdata = []
    for user_id in users:
        try:
            user = await client.get_entity(user_id)
            user_full_name = user.first_name + (' ' + user.last_name if user.last_name else '')

            userdata.append({
                "id": str(user.id),
                "full_name": user_full_name,
                "username": user.username
            })
        except Exception as e:
            print(f"Error fetching user {user_id}: {e}")
    return userdata