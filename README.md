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
python src/bot.py
```

`python-dotenv` подгружает переменные из `.env` автоматически.

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

## Если возник конфликт на GitHub

Локально конфликтов быть не должно: перед пушем проверьте, что в файлах нет маркеров `<<<<<<<`, `=======`, `>>>>>>>`.

```bash
rg -n "^(<<<<<<<|=======|>>>>>>>)"
```

Если в PR есть конфликт с `main`, выполните:

```bash
git fetch origin
git rebase origin/main
# исправьте конфликтные файлы
git add <исправленные_файлы>
git rebase --continue
```

После успешного ребейза отправьте ветку:

```bash
git push --force-with-lease
```


### Автосценарий для вашей ветки

Для этого репозитория можно использовать готовый скрипт (например, для ветки `work`):

```bash
bash scripts/sync_with_main.sh origin main
```

Что делает скрипт:

1. Проверяет, что нет незакоммиченных изменений.
2. Делает `git fetch origin`.
3. Делает `git rebase origin/main` для текущей ветки.
4. Проверяет маркеры конфликтов через `rg`.
5. Выполняет `git push --force-with-lease` в текущую ветку.

Если в процессе ребейза возник конфликт, исправьте файлы и продолжите:

```bash
git add <исправленные_файлы>
git rebase --continue
```


## Перенос проекта в другой репозиторий

Добавлен скрипт миграции:

```bash
bash scripts/migrate_to_new_repo.sh <NEW_REPO_URL> [TARGET_BRANCH] [REMOTE_NAME]
```

Пример:

```bash
bash scripts/migrate_to_new_repo.sh git@github.com:your-org/new-tgbot.git main new-origin
```

Что делает скрипт:

1. Проверяет, что нет незакоммиченных изменений.
2. Добавляет (или обновляет) remote с именем `new-origin` (или вашим именем).
3. Пушит текущую ветку в целевую ветку нового репозитория и ставит upstream.

После переноса можно сделать новый remote основным:

```bash
git remote rename new-origin origin
```
