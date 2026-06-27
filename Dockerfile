FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY tg-media-preview-bot/requirements.txt ./
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

COPY tg-media-preview-bot/ ./

CMD ["python", "bot.py"]
