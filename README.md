# project2_chuvilova_01

primitive_db — учебное консольное приложение.
На подготовительном этапе доступны команды help и exit.

## Требования

Python 3.12 или новее и установленный uv.

## Установка

Из корня клонированного репозитория выполните:

    uv sync

## Запуск

    uv run database

## Команды приложения

help — показать справку.
exit — завершить программу.

## Качество кода

    uv run ruff check .
    uv run ruff format --check .

## Сборка и проверка метаданных

    uv build
    uvx twine check dist/*

## Установка собранного пакета

    uv tool install dist/*.whl

После установки команда запуска — project.

## Управление таблицами

Запуск приложения из корня проекта:

    uv run database

После установки собранного пакета:

    database

Доступные команды:

- create_table <имя_таблицы> <столбец1:тип> ... — создать таблицу.
- list_tables — показать список таблиц.
- drop_table <имя_таблицы> — удалить таблицу.
- help — показать справку.
- exit — завершить программу.

Поддерживаемые типы: int, str, bool.

Столбец ID:int автоматически добавляется первым.
Если пользователь указал ID:int, он не дублируется.

Пример использования:

    create_table users name:str age:int is_active:bool
    list_tables
    drop_table users
    exit

Структура таблиц сохраняется в db_meta.json
в текущей рабочей папке и загружается при следующем запуске.

Для работы с теми же таблицами запускайте приложение
из той же папки.

## Демонстрация

[![asciicast](https://asciinema.org/a/NpX1GDxBLilDerWh.svg)](https://asciinema.org/a/NpX1GDxBLilDerWh)

## CRUD-операции

Запуск:

    uv run database

Добавление записи:

    insert into users values ("Sergei", 28, true)

Чтение всех записей:

    select from users

Чтение по условию:

    select from users where age = 28

Обновление:

    update users set age = 29 where name = "Sergei"

Удаление:

    delete from users where ID = 1

Информация о таблице:

    info users

Перед использованием примеров создайте таблицу:

    create_table users name:str age:int is_active:bool

Строки вводятся в двойных кавычках.
Логические значения записываются как true и false.

Все поля обязательны.
ID генерируется автоматически и не передаётся в insert.
Изменять ID через update нельзя.

where поддерживает одно условие равенства.
set изменяет один столбец.

Метаданные хранятся в db_meta.json.
Записи таблиц хранятся в data/<имя_таблицы>.json.

Файлы создаются относительно текущей папки запуска.
Для работы с прежними данными запускайте приложение
из той же папки.

## Демонстрация CRUD

[![asciicast](https://asciinema.org/a/IjeSH6rr20GLQOGL.svg)](https://asciinema.org/a/IjeSH6rr20GLQOGL)
