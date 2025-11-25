from telethon.tl.custom import Button
from db.schema import UserSettings
from db.operations import get_user_settings
from logic.helper_funcs import correct_word_spell


async def main_menu_buttons():
    settings: UserSettings = await get_user_settings()

    return [
        [Button.inline("⚙️ Настройка режима", data="sw_mode_menu")],
        [Button.inline("👁️ Показать список слежки", data="show_list")],
        [Button.inline("📝 Обновить список слежки", data="update_list")],
        [Button.inline("🧹 Время очистки БД", data="update_autoremove")],
        [Button.inline("🔌 Выключить бота" if settings.bot_active else "🔋 Включить бота", data="toggle_bot")],
    ]


def change_mode_menu_button():
    return [Button.inline('🔧 Изменить режим', data='sw_mode_menu')]


def back_to_main_menu_button():
    return [Button.inline('⬅️ Назад', data='back_to_main_menu')]


def change_mode_button(whitelist: bool = True):
    return [Button.inline('📄 Whitelist' if whitelist else '🗑️ Blacklist', data='sw_mode')]


def enable_pm_filtration_button(only_pm: bool = False):
    return [Button.inline('🔒 Слушаю только ЛС' if only_pm else '🔓 Слушаю все сообщения', data='sw_pm_filter')]


def autoremove_settings(timedelta_days: str):
    return [
        [
            Button.inline(f'{timedelta_days} {correct_word_spell(timedelta_days)}')
        ],  
        [
            Button.inline('<<', data="update_autoremove_time:decrease"),
            Button.inline('>>', data="update_autoremove_time:increase")
        ],
        back_to_main_menu_button()
    ]


def settings_buttons(settings):
    return [
        enable_pm_filtration_button(settings.pm_filter),
        change_mode_button(settings.is_whitelist_mode),
        back_to_main_menu_button()
    ]