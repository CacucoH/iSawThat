import logging
from telethon import TelegramClient
from telethon.events.callbackquery import CallbackQuery

from events.handlers.message_handler import handle_start_message
from events.user_interaction.gui_settings import back_to_main_menu_button, settings_buttons, autoremove_settings
from db.operations import (get_victims_list, set_user_state, toggle_pm_filter,
                           update_whitelist_mode, get_user_settings, activate_bot, update_time_delta)
from db.schema import UserSettings
from events.user_interaction.states import States
from logic.logic import owner_only


@owner_only
async def callbacks_handler(event: CallbackQuery.Event):
    callback = event.data
    callback_data = callback.split(b':')
    callback_method_invoke = callback_data[0]
    
    settings: UserSettings = await get_user_settings()

    match callback_method_invoke:
        case b"update_autoremove":
            await update_delta_ui(event, settings.message_deletion_delta)
        
        case b"update_autoremove_time":
            func = callback_data[1]
            new_delta = await update_time_delta(func)
            await update_delta_ui(event, settings.message_deletion_delta)

        case b"sw_mode":
            await update_whitelist_mode()
            await event.edit(
                f"🔧 Режим изменен на **{'Whitelist ✅' if not settings.is_whitelist_mode else 'Blacklist ❌'}**",
                buttons=settings_buttons(settings)
            )

        case b"sw_pm_filter":
            await toggle_pm_filter()
            await event.edit(
                f"🔒 Теперь я слушаю сообщения **{'только из лс' if not settings.pm_filter else 'из всех источников'}**",
                buttons=settings_buttons(settings)
            )

        case b"sw_mode_menu":
            await event.edit(
                f"Настройки фильтрации сообщений:",
                buttons=settings_buttons(settings)
            )

        case b"toggle_bot":
            new_state = not settings.bot_active
            await activate_bot()
            await event.edit(
                f"{'✅ Бот активен' if new_state else '⛔ Бот отключён'}",
                buttons=back_to_main_menu_button()
            )
        
        case b"update_list":
            await event.edit("Обновить список? Ну давай, я обновлю его для тебя😎\nВведи список `username'ов` через запятую:",
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

    
async def update_delta_ui(event, time_delta: str):
    # TG sometimes does not edit message. This is a fix
    dumbass_graphics = {
        '1':'🚨',
        '3':'⚠️',
        '7': '✅',
        '14': '🛡'
    }
    await event.edit(
        f"{dumbass_graphics[time_delta]} Удаление сообщений старше:",
        buttons=autoremove_settings(time_delta)
    )