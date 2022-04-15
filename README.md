# demo-pizza-bot

## Настройка бота
Настройки включаются в себя:
* Переменные окружения описанные в файле example.env, которые могут быть размещены
  в файле .env;
* Сервисный аккаунт Google в формате json:
  https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account

## Запуск
* Установить Poetry: https://python-poetry.org/docs/#installation
* Выполнить команды:
```shell
poetry install
poetry run python -m main
```

## Запуск в Docker
* Установить Docker: https://docs.docker.com/desktop/
* Выполнить команды:
```shell
docker build -t demo-pizza-bot .
docker run -it --rm --env-file=.env -v `pwd`/var:/app/var  demo-pizza-bot
```

## Хостинг в Yandex Cloud Functions
Можно воспользоваться руководством
[Как создать бота в Telegram](https://cloud.yandex.ru/docs/functions/tutorials/telegram-bot-serverless)
из документации, с поправкой на язык Python.
