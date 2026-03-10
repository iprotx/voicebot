# Telegram Voicebox Bot

Телеграм-бот для управления Voicebox через кнопки:

- создание голосовых профилей;
- автосоздание профиля из **пересланного** voice сообщения;
- добавление voice-сэмплов в активный профиль;
- выбор/просмотр/удаление профилей;
- генерация речи и отправка результата в Telegram.

## Требования

- Python 3.11+
- Запущенный Voicebox API (по умолчанию `http://localhost:17493`)
- Telegram bot token от `@BotFather`

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`, затем:

```bash
set -a; source .env; set +a
python src/bot.py
```

## Как это работает

1. Нажмите `➕ Создать профиль` и введите имя — бот создаст профиль в Voicebox.
2. Отправьте голосовое сообщение (`voice`) — оно добавится как сэмпл в активный профиль.
3. Можно переслать чужой voice: бот автоматически создаст новый профиль и добавит sample.
4. Нажмите `🗣 Сгенерировать речь`, отправьте текст — бот вернет озвучку.

## Поддерживаемые REST методы Voicebox

- `GET /profiles`
- `POST /profiles`
- `DELETE /profiles/{id}`
- `POST /profiles/{id}/samples`
- `POST /generate`

Если ваш сервер Voicebox работает на другом хосте/порту, измените `VOICEBOX_BASE_URL`.
