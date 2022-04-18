# demo-pizza-bot
Демонстрация Telegram-бота для заказа пиццы.
Хранит заказы в Google Таблицах.
Пример документа: https://docs.google.com/spreadsheets/d/1KvldMGQbLdQa6ASr4vSfjxteX88sJtJOpC8jvlK6XF0/edit?usp=sharing

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
git clone https://github.com/poofeg/demo-pizza-bot.git
cd demo-pizza-bot
cp example.env .env
editor .env
poetry install
poetry run python -m main
```

## Запуск в Docker
* Установить Docker: https://docs.docker.com/desktop/
* Выполнить команды:
```shell
git clone https://github.com/poofeg/demo-pizza-bot.git
cd demo-pizza-bot
cp example.env .env
editor .env
docker build -t demo-pizza-bot .
docker run -it --rm --env-file=.env -v `pwd`/var:/app/var demo-pizza-bot
```

## Хостинг в Yandex Cloud Functions
Можно воспользоваться руководством
[Как создать бота в Telegram](https://cloud.yandex.ru/docs/functions/tutorials/telegram-bot-serverless)
из документации, с поправкой на язык Python.
Для подготовки zip-архива можно использовать скрипт `make_dist`.
