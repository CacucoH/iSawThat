import logging
from telethon import TelegramClient
from telethon.events.callbackquery import CallbackQuery

from events.handlers.message_handler import handle_start_message
from events.user_interaction.gui_settings import back_to_main_menu_button, settings_buttons
from db.operations import get_victims_list, set_user_state, toggle_pm_filter, update_whitelist_mode, get_user_settings, activate_bot
from events.user_interaction.states import States
from logic.logic import owner_only


@owner_only
async def callbacks_handler(event: CallbackQuery.Event):
    callback = event.data
    settings = await get_user_settings()

    match callback:
        case b"sw_mode":
            await update_whitelist_mode()
            await event.edit(
                f"🔧 Режим изменен на **{'Whitelist ✅' if not settings.is_whitelist_mode else 'Blacklist ❌'}**",
                buttons=settings_buttons(await get_user_settings())
            )

        case b"sw_pm_filter":
            await toggle_pm_filter()
            await event.edit(
                f"🔒 Теперь я слушаю сообщения **{'только из лс' if not settings.pm_filter else 'из всех источников'}**",
                buttons=settings_buttons(await get_user_settings())
            )

        case b"sw_mode_menu":
            await event.edit(
                f"Настройки фильтрации сообщений:",
                buttons=settings_buttons(await get_user_settings())
            )

        case b"toggle_bot":
            new_state = not settings.bot_active
            await activate_bot()
            await event.edit(
                f"{'✅ Бот активен' if new_state else '⛔ Бот отключён'}",
                buttons=back_to_main_menu_button()
            )
        
        case b"update_list":
            await event.edit("Ах, обновить список? Ну давай, я обновлю его для тебя😎\nВведи список `username'ов` через запятую:",
                              buttons=back_to_main_menu_button())
            await set_user_state(States.PENDING_LIST_UPDATE)

        case b"show_list":
            list = await get_victims_list()
            await event.edit(
                f"**{'Список слежки:' if settings.is_whitelist_mode else 'Все, кроме:'}**\n" + "\n> ".join([f"{user['user_full_name']} (@{user['username']})" for user in list]) if list else "Список пуст :(",
                buttons=back_to_main_menu_button()
            )

        case b"back_to_main_menu":
            if States(settings.state) == States.LIST_UPDATED:
                await handle_start_message(event, True, "**Список обновлён!**\nВыбери действие:")
                return
            
            await handle_start_message(event, True)

        case _:
            await event.answer("Неизвестная команда", alert=True)