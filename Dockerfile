FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN addgroup -S sota && adduser -S -G sota sota

RUN pip install --no-cache-dir --root-user-action=ignore "python-telegram-bot>=21.0,<23.0"

COPY sota_telegram_bot ./sota_telegram_bot
COPY tests ./tests

RUN mkdir -p /app/data && chown -R sota:sota /app

USER sota

VOLUME ["/app/data"]

CMD ["python", "-m", "sota_telegram_bot.bot"]
