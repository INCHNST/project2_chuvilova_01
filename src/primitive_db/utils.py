import json
import os

from primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """Загрузить метаданные или вернуть пустой словарь."""
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
    """Сохранить метаданные в JSON файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_table_path(table_name):
    """Сформировать путь к файлу таблицы с допустимым именем."""
    if not table_name.isidentifier():
        raise ValueError(f"Некорректное имя таблицы: {table_name}")

    return os.path.join(DATA_DIR, f"{table_name}.json")


def load_table_data(table_name):
    """Загрузить записи таблицы или вернуть пустой список."""
    try:
        with open(
            get_table_path(table_name),
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except FileNotFoundError:
        return []

    if not isinstance(data, list):
        raise ValueError("Данные таблицы должны быть списком.")

    if not all(isinstance(row, dict) for row in data):
        raise ValueError("Каждая запись должна быть словарём.")

    return data


def save_table_data(table_name, data):
    """Сохранить записи, при необходимости создав каталог."""
    filepath = get_table_path(table_name)
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def remove_table_data(table_name):
    """Удалить файл таблицы, если он существует."""
    try:
        os.remove(get_table_path(table_name))
    except FileNotFoundError:
        pass
