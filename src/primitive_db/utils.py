import json
from pathlib import Path


def load_metadata(filepath):
    try:
        with open(filepath, encoding="utf-8") as file:
            metadata = json.load(file)
    except FileNotFoundError:
        return {}

    if not isinstance(metadata, dict):
        raise ValueError("Метаданные должны быть словарём.")

    for columns in metadata.values():
        if not isinstance(columns, list):
            raise ValueError("Столбцы должны храниться в списке.")

        if not all(isinstance(column, str) for column in columns):
            raise ValueError("Описание столбца должно быть строкой.")

    return metadata


def save_metadata(filepath, data):
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_table_path(table_name):
    if not table_name.isidentifier():
        raise ValueError(f"Некорректное имя таблицы: {table_name}")

    return Path("data") / f"{table_name}.json"


def load_table_data(table_name):
    filepath = get_table_path(table_name)

    try:
        with filepath.open(encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return []

    if not isinstance(data, list):
        raise ValueError("Данные таблицы должны быть списком.")

    if not all(isinstance(row, dict) for row in data):
        raise ValueError("Каждая запись должна быть словарём.")

    return data


def save_table_data(table_name, data):
    filepath = get_table_path(table_name)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with filepath.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def remove_table_data(table_name):
    filepath = get_table_path(table_name)
    filepath.unlink(missing_ok=True)
