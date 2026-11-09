VALID_TYPES = {"int", "str", "bool"}


def create_table(metadata, table_name, columns):
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    if not table_name.isidentifier():
        print(f"Некорректное значение: {table_name}. Попробуйте снова.")
        return metadata

    if not columns:
        print("Некорректное значение: список столбцов. Попробуйте снова.")
        return metadata

    result_columns = ["ID:int"]
    column_names = set()

    for column in columns:
        parts = column.split(":")

        if len(parts) != 2:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        column_name, column_type = parts

        if not column_name.isidentifier():
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        if column_type not in VALID_TYPES:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        if column_name in column_names:
            print(f"Некорректное значение: {column}. Попробуйте снова.")
            return metadata

        column_names.add(column_name)

        if column_name == "ID":
            if column_type != "int":
                print(f"Некорректное значение: {column}. Попробуйте снова.")
                return metadata

            continue

        result_columns.append(column)

    metadata[table_name] = result_columns
    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    return metadata
