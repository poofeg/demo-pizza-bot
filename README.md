# demo-pizza-bot

## Настройка бота
Настройки включаются в себя:
* Переменные окружения описанные в файле example.env, которые могут быть размещены
  в файле .env;
* Сервисный аккаунт Google в формате json

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
