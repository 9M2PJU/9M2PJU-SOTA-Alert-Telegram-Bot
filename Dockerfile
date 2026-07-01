FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system sota && adduser --system --ingroup sota sota

COPY pyproject.toml README.md ./
COPY sota_telegram_bot ./sota_telegram_bot
COPY tests ./tests

RUN pip install --no-cache-dir .

RUN mkdir -p /app/data && chown -R sota:sota /app

USER sota

VOLUME ["/app/data"]

CMD ["sota-telegram-bot"]
