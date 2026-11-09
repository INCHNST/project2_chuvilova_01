from primitive_db.utils import load_table_data

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


PYTHON_TYPES = {
    "int": int,
    "str": str,
    "bool": bool,
}


def get_schema(metadata, table_name):
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    schema = {}

    for column in metadata[table_name]:
        column_name, column_type = column.split(":")
        schema[column_name] = column_type

    if schema.get("ID") != "int":
        raise ValueError("В схеме должен быть столбец ID:int.")

    return schema


def validate_clause(schema, clause):
    for column_name, value in clause.items():
        if column_name not in schema:
            raise ValueError(f'Столбец "{column_name}" не существует.')

        expected_type = PYTHON_TYPES[schema[column_name]]

        if type(value) is not expected_type:
            raise ValueError(
                f'Столбец "{column_name}" ожидает тип {schema[column_name]}.'
            )


def validate_table_data(schema, table_data):
    ids = set()

    for row in table_data:
        if set(row) != set(schema):
            raise ValueError("Структура записи не соответствует схеме.")

        validate_clause(schema, row)

        if row["ID"] <= 0 or row["ID"] in ids:
            raise ValueError("В данных обнаружен некорректный ID.")

        ids.add(row["ID"])


def insert(metadata, table_name, values):
    schema = get_schema(metadata, table_name)
    columns = [column for column in schema if column != "ID"]

    if len(values) != len(columns):
        raise ValueError(
            f"Ожидалось значений: {len(columns)}, получено: {len(values)}."
        )

    row = dict(zip(columns, values, strict=True))
    validate_clause(schema, row)

    table_data = load_table_data(table_name)
    validate_table_data(schema, table_data)

    new_id = (
        max(
            (item["ID"] for item in table_data),
            default=0,
        )
        + 1
    )

    row = {"ID": new_id, **row}
    table_data.append(row)

    return table_data


def select(table_data, where_clause=None):
    if where_clause is None:
        return list(table_data)

    return [
        row
        for row in table_data
        if all(row.get(column) == value for column, value in where_clause.items())
    ]


def update(table_data, set_clause, where_clause):
    if "ID" in set_clause:
        raise ValueError("Изменять ID нельзя.")

    for row in select(table_data, where_clause):
        row.update(set_clause)

    return table_data


def delete(table_data, where_clause):
    return [
        row
        for row in table_data
        if not all(row.get(column) == value for column, value in where_clause.items())
    ]
