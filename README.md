# TG Media Preview Bot

This repository contains the Telegram media preview bot in the `tg-media-preview-bot` subdirectory.

## Railway deployment

If Railway builds from the repository root, it will use the `Dockerfile` at the root and copy the `tg-media-preview-bot` directory.

### Railway environment variable

Add the following variable in Railway under `Variables`:

- `BOT_TOKEN` = your Telegram bot token from BotFather

### Root .env example

The repository root also includes `.env.example` for local development.

## Notes

- The actual bot code lives in `tg-media-preview-bot/`
- Use the root `Dockerfile` for deployment platforms that require the project root to contain a Dockerfile.
