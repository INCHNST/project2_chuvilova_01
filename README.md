# project2_chuvilova_01

primitive_db — учебное консольное приложение.
На подготовительном этапе доступны команды help и exit.

## Требования

Python 3.12 или новее и установленный uv.

## Установка

Из корня клонированного репозитория выполните:

    uv sync

## Запуск

    uv run project

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
