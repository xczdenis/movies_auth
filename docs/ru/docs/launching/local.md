# Запуск приложения локально
Ты можешь запустить приложение локально, не используя docker.

!!!warning
    Для запуска приложения локально у тебя должна быть запущена база данных и redis:
    === "Make"

        ```bash
        $ make dev s="postgres redis"
        ```

    === "Native"

        ```bash
        $ docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build postgres redis
        ```

!!! success "Action"
    Для запуска приложения локально требуется установить переменную среды `FLASK_APP`
    в значение `manage.py`:
    ```bash
    export FLASK_APP=manage.py
    ```

Проверь, что у тебя не запущен контейнер `nginx` т.к. он запускается на порту 5000 и приложение
тоже запускается на порту 5000. Если контейнер nginx будет запущен, то приложение локально
уже не запустится т.к. порт 5000 будет занят. Также не должен быть запущен контейнер `app`.

Для запуска приложения локально перейди в каталог `src`:
```bash
cd src
```
Выполни миграции:
```bash
python -m flask db upgrade
```
Запусти приложение:
```bash
python manage.py
```
