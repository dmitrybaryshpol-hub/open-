import logging
import os
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
LOGGER = logging.getLogger(__name__)

SOCIAL_DOMAINS = ["instagram.com", "twitter.com", "x.com", "tiktok.com"]
URL_RE = re.compile(r"https?://[^"]+")


def extract_social_url(text: str) -> Optional[str]:
    if not text:
        return None

    urls = URL_RE.findall(text)
    for raw_url in urls:
        url = raw_url.strip("()[]<>,.!?")
        if any(domain in url.lower() for domain in SOCIAL_DOMAINS):
            return url
    return None


def fetch_preview(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    metadata = {}

    for key in ["og:title", "og:description", "og:image", "og:url", "twitter:title", "twitter:description", "twitter:image"]:
        tag = soup.find("meta", property=key) or soup.find("meta", attrs={"name": key})
        if tag and tag.has_attr("content"):
            metadata[key] = tag["content"]

    title = metadata.get("og:title") or metadata.get("twitter:title") or "Соціальний пост"
    description = metadata.get("og:description") or metadata.get("twitter:description") or "Пост успішно знайдено."
    image_url = metadata.get("og:image") or metadata.get("twitter:image")
    canonical_url = metadata.get("og:url") or url

    return {
        "title": title,
        "description": description,
        "image": image_url,
        "url": canonical_url,
    }


def make_caption(preview: dict) -> str:
    caption = f"*{preview['title']}*\n\n{preview['description']}\n\n[Відкрити пост]({preview['url']})"
    return caption


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привіт! Надішли мені посилання з Instagram, Twitter/X або TikTok, і я покажу попередній перегляд посту."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Надішли мені посилання на Instagram, Twitter/X або TikTok."
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or update.message.caption or ""
    social_url = extract_social_url(text)
    if not social_url:
        await update.message.reply_text(
            "Будь ласка, надішли посилання на Instagram, Twitter/X або TikTok.",
        )
        return

    try:
        preview = fetch_preview(social_url)
        caption = make_caption(preview)
        if preview["image"]:
            await update.message.reply_photo(
                photo=preview["image"],
                caption=caption,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        else:
            await update.message.reply_text(
                caption,
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
    except Exception as exc:
        LOGGER.exception("Preview failed")
        await update.message.reply_text(
            f"Не вдалося завантажити пост. Перевірте посилання або спробуйте пізніше.\n\nПомилка: {exc}"
        )


def build_application() -> object:
    token = os.getenv("TELEGRAM_TOKEN") or os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Будь ласка, встановіть змінну середовища TELEGRAM_TOKEN або BOT_TOKEN."
        )

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.CAPTION, message_handler))
    return app


def main() -> None:
    application = build_application()
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
