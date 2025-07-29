import logging
from telethon import TelegramClient
from telethon.events.callbackquery import CallbackQuery

from events.handlers.message_handler import handle_start_message
from events.user_interaction.gui_settings import back_to_main_menu_button, change_mode_button, change_mode_menu_button
from db.operations import update_userlist, update_whitelist_mode, get_user_settings, activate_bot


async def callbacks_handler(event: CallbackQuery.Event):
    user_id = str(event.sender_id)
    callback = event.data

    match callback:
        case b"sw_mode":
            settings = await get_user_settings()
            await update_whitelist_mode()
            await event.edit(
                f"🔧 Режим изменен на **{'Whitelist ✅' if settings.is_whitelist_mode else 'Blacklist ❌'}**",
                buttons=[ change_mode_button(), back_to_main_menu_button() ]
            )
        
        case b"sw_mode_menu":
            settings = await get_user_settings()
            await event.edit(
                f"🔧 Текущий режим: **{'Whitelist ✅' if settings.is_whitelist_mode else 'Blacklist ❌'}**",
                buttons=[ change_mode_menu_button(), back_to_main_menu_button() ]
            )

        case b"toggle_bot":
            settings = await get_user_settings()
            new_state = not settings.bot_active
            await activate_bot()
            await event.edit(
                f"{'✅ Бот активен' if new_state else '⛔ Бот отключён'}",
                buttons=back_to_main_menu_button()
            )
        
        case b"update_list":
            await event.edit("Ах, обновить список? Ну давай, я обновлю его для тебя! Введи список username'ов через запятую:")

        case b"back_to_main_menu":
            await handle_start_message(event, True)

        case _:
            await event.answer("Неизвестная команда", alert=True)