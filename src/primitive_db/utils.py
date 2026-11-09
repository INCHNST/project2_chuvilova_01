import json


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
