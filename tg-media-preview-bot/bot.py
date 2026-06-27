import asyncio
import logging
import os
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ContentType
from aiogram.filters import Text
from aiogram.types import Message
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is required. Create .env file from .env.example and set BOT_TOKEN there.")

BOT = Bot(token=BOT_TOKEN)
DP = Dispatcher()

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 45 * 1024 * 1024  # 45 MB

YTDLP_OPTIONS = {
    "format": "mp4",
    "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
    "quiet": True,
    "no_warnings": True,
    "merge_output_format": "mp4",
}

URL_KEYWORDS = ["tiktok.com", "vm.tiktok.com", "instagram.com", "reels"]


def extract_media_url(text: str) -> str | None:
    """Return a supported TikTok or Instagram URL from the incoming text."""
    if not text:
        return None

    for token in text.split():
        normalized = token.strip("<>\n\r\t")
        if any(keyword in normalized for keyword in URL_KEYWORDS):
            return normalized
    return None


async def download_media(url: str) -> Path:
    """Download video using yt-dlp and return path to downloaded file."""
    loop = asyncio.get_running_loop()

    def run_download() -> Path:
        with YoutubeDL(YTDLP_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not Path(filename).exists():
                raise FileNotFoundError("Downloaded file not found.")
            return Path(filename)

    downloaded_path = await loop.run_in_executor(None, run_download)
    return downloaded_path


async def handle_media_message(message: Message) -> None:
    """Process an incoming message with supported media links."""
    text = message.text or message.caption or ""
    media_url = extract_media_url(text)
    if not media_url:
        return

    try:
        loading_message = await message.reply("⏳ Загружаю...", quote=True)
        downloaded_file = await download_media(media_url)

        file_size = downloaded_file.stat().st_size
        if file_size > MAX_FILE_SIZE:
            await loading_message.edit_text(
                "⚠️ Файл більше 45 МБ. Спробуйте інший пост або скоротіть якість.")
            return

        await message.reply_video(video=downloaded_file.open("rb"), quote=True)
        await loading_message.delete()
    except Exception as exc:
        logger.exception("Failed to download or send media")
        error_text = (
            "❌ Не вдалося завантажити контент. "
            "Перевірте посилання або спробуйте пізніше."
        )
        if 'HTTP Error' in str(exc) or '404' in str(exc):
            error_text = "❌ Контент не знайдено або посилання недійсне."
        await message.reply(error_text, quote=True)
    finally:
        for file_path in DOWNLOAD_DIR.iterdir():
            if file_path.is_file():
                try:
                    file_path.unlink()
                except OSError:
                    logger.warning("Could not remove temporary file %s", file_path)


@DP.message(F.text & Text(contains=URL_KEYWORDS))
@DP.message(F.caption & Text(contains=URL_KEYWORDS))
async def media_handler(message: Message) -> None:
    await handle_media_message(message)


async def main() -> None:
    """Run the bot polling loop."""
    try:
        await DP.start_polling(BOT)
    finally:
        await BOT.session.close()


if __name__ == "__main__":
    asyncio.run(main())
