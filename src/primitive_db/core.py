import json

from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data

VALID_TYPES = {"int", "str", "bool"}
PYTHON_TYPES = {"int": int, "str": str, "bool": bool}
SELECT_CACHE = create_cacher()


def clear_select_cache():
    SELECT_CACHE.clear()


@handle_db_errors
def create_table(metadata, table_name, columns):
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    if not table_name.isidentifier():
        raise ValueError(f"Некорректное имя таблицы: {table_name}")

    if not columns:
        raise ValueError("Укажите хотя бы один столбец.")

    result_columns = ["ID:int"]
    column_names = set()

    for column in columns:
        parts = column.split(":")

        if len(parts) != 2:
            raise ValueError(f"Некорректное описание столбца: {column}")

        column_name, column_type = parts

        if not column_name.isidentifier() or column_type not in VALID_TYPES:
            raise ValueError(f"Некорректный столбец или тип: {column}")

        if column_name in column_names:
            raise ValueError(f"Повторяющийся столбец: {column_name}")

        column_names.add(column_name)

        if column_name == "ID":
            if column_type != "int":
                raise ValueError("Столбец ID должен иметь тип int.")
            continue

        result_columns.append(column)

    metadata[table_name] = result_columns
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(table_name)

    del metadata[table_name]
    return metadata


@handle_db_errors
def get_schema(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(table_name)

    schema = {}

    for column in metadata[table_name]:
        column_name, column_type = column.split(":")

        if column_type not in VALID_TYPES:
            raise ValueError(f"Неизвестный тип: {column_type}")

        schema[column_name] = column_type

    if schema.get("ID") != "int":
        raise ValueError("В схеме должен быть столбец ID:int.")

    return schema


@handle_db_errors
def validate_clause(schema, clause):
    for column_name, value in clause.items():
        if column_name not in schema:
            raise KeyError(column_name)

        expected_type = PYTHON_TYPES[schema[column_name]]

        if type(value) is not expected_type:
            raise ValueError(
                f'Столбец "{column_name}" ожидает тип {schema[column_name]}.'
            )

    return True


@handle_db_errors
def validate_table_data(schema, table_data):
    ids = set()

    for row in table_data:
        if set(row) != set(schema):
            raise ValueError("Структура записи не соответствует схеме.")

        if validate_clause(schema, row) is None:
            return None

        if row["ID"] <= 0 or row["ID"] in ids:
            raise ValueError("В данных обнаружен некорректный ID.")

        ids.add(row["ID"])

    return True


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    schema = get_schema(metadata, table_name)

    if schema is None:
        return None

    columns = [column for column in schema if column != "ID"]

    if len(values) != len(columns):
        raise ValueError(
            f"Ожидалось значений: {len(columns)}, получено: {len(values)}."
        )

    row = dict(zip(columns, values, strict=True))

    if validate_clause(schema, row) is None:
        return None

    table_data = load_table_data(table_name)

    if validate_table_data(schema, table_data) is None:
        return None

    new_id = (
        max(
            (item["ID"] for item in table_data),
            default=0,
        )
        + 1
    )

    table_data.append({"ID": new_id, **row})
    return table_data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    key = json.dumps(
        {
            "data": table_data,
            "where": where_clause,
        },
        sort_keys=True,
        ensure_ascii=False,
    )

    def calculate_result():
        if where_clause is None:
            return list(table_data)

        return [
            row
            for row in table_data
            if all(row.get(column) == value for column, value in where_clause.items())
        ]

    return SELECT_CACHE(key, calculate_result)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    if "ID" in set_clause:
        raise ValueError("Изменять ID нельзя.")

    for row in table_data:
        if all(row.get(column) == value for column, value in where_clause.items()):
            row.update(set_clause)

    return table_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    return [
        row
        for row in table_data
        if not all(row.get(column) == value for column, value in where_clause.items())
    ]
