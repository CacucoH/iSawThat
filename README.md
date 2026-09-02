# iSawThat

Маленький Telegram-шпион для себя же. Состоит из двух клиентов:

- **userbot** — сидит на твоём личном аккаунте, ловит все сообщения (входящие/исходящие, по вкусу), пишет их в базу. Ещё замечает, когда сообщение отредачили или удалили
- **bot** — обычный Telegram-бот (через BotFather), который присылает тебе уведомления, когда что-то удалили/отредачили, шлёт сохранённые вложения, и рулит настройками через `/start`-меню

Зачем: если кто-то удалит сообщение у тебя в личке или в чате, где ты состоишь — бот покажет, что там было написано, до того как оно исчезло

## Фичи

- Сохранение всех сообщений в базу (с медиа-вложениями)
- Уведомление, если сообщение удалили — с текстом, отправителем, чатом
- Уведомление о редактировании сообщений
- Whitelist / Blacklist режим — следить либо только за списком людей, либо за всеми кроме списка
- Фильтр "только личка" — не писать в базу групповые чаты
- Автоочистка старой истории (1/3/7/14 дней)
- Кнопочное GUI-меню, никаких команд руками вбивать не надо

## Как поднять

### Docker (рекомендуется)

1. Заполни конфиги своими данными:
   ```bash
   cp misc/config/bot.env.example misc/config/bot.env
   cp misc/config/db.env.example misc/config/db.env
   ```
   - `bot.env` — `API_ID`/`API_HASH` с [my.telegram.org](https://my.telegram.org), `APP_NAME` — любое имя сессии, `BOT_TOKEN` — токен от [@BotFather](https://t.me/BotFather).
   - `db.env` — логин/пароль/порт для постгреса, любые свои.
   - `misc/config/settings` уже с адекватными дефолтами, трогать не обязательно.

2. Получи сессию юзербота (без этого шага бот не сможет достучаться до твоего аккаунта):
   ```bash
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   python3 session-initializer.py        # ввод номера телефона
   # или через QR-код, если лень вбивать номер:
   python3 session-initializer.py --qr
   ```

3. Далее:
   ```bash
   docker compose up --build -d
   ```

4. Пиши своему боту `/start` — должно появиться меню

### Локально

Можно через `install.sh`:

```bash
./install.sh
python3 src/main.py
```

В таком случае БД нужна своя. Либо локальный Postgres, либо менять `DATABASE_URL` под что-то попроще

## Troubleshooting

### Бот вообще не отвечает на `/start` и не шлёт уведомления, при этом userbot ловит сообщения нормально

Значит, скорее всего, файл сессии бота залогинен не как бот, а как обычный юзер. Это видно в логах:

```
UserWarning: the session already had an authorized user so it did not login to
the bot account using the provided bot_token; if you were expecting a different
user, check whether you are accidentally reusing an existing session
```

**Фикс:**
```bash
docker compose down
rm misc/session/<APP_NAME>_bot.session*
docker compose up --build
```
⚠️ Удаляйте файл с суффиксом `_bot`!!! `<APP_NAME>.session` (без `_bot`) это сессия личного аккаунта (userbot), её трогать не надо, иначе придётся заново проходить `session-initializer.py`

После пересоздания `bot` залогинится нормально через `BOT_TOKEN` как настоящий бот

## Структура конфигов

```
misc/config/
  bot.env      # API_ID, API_HASH, APP_NAME, BOT_TOKEN — секретное, в .gitignore
  db.env       # DB_USER, DB_PASSW, DB_PORT — тоже секретное
  settings     # MAX_MESSAGE_LEN, REPLY_UNKNOWN_USER, ATTACHEMENTS_DOWNLOAD_PATH, DEVMODE
misc/session/  # .session файлы Telethon (не коммитить!)
misc/logs/     # логи по дням
misc/data/     # скачанные вложения
```
