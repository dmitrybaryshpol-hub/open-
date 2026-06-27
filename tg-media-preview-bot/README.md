# Telegram Media Preview Bot MVP

Простий Telegram-бот на Python 3.13, який обробляє посилання на TikTok та Instagram у групових чатах.

## Можливості

- Працює через polling
- Повертає відео із TikTok та Instagram
- Повідомляє користувача про процес завантаження
- Обмеження на розмір файла: 45 МБ
- Використовує `aiogram 3.x`, `yt-dlp`, `python-dotenv`

## Структура проекту

```text
tg-media-preview-bot/
├── bot.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── README.md
└── .gitignore
```

## Запуск локально

1. Скопіюйте `.env.example` у `.env`:

```bash
copy .env.example .env
```

2. Додайте в `.env` ваш `BOT_TOKEN`.

3. Встановіть залежності:

```bash
python -m pip install -r requirements.txt
```

4. Запустіть бота:

```bash
python bot.py
```

## Запуск через Docker

1. Побудуйте образ:

```bash
docker build -t tg-media-preview-bot .
```

2. Запустіть контейнер з токеном:

```bash
docker run --env BOT_TOKEN=your_telegram_bot_token -it tg-media-preview-bot
```

## Privacy Mode

1. В BotFather відкрийте налаштування бота.
2. Перейдіть у `Bot Settings` → `Group Privacy`.
3. Вимкніть privacy mode, щоб бот бачив всі повідомлення у групі.

## Примітки

- Бот обробляє лише повідомлення, що містять TikTok/Instagram посилання.
- Якщо відео більше 45 МБ, бот відправляє попередження.
