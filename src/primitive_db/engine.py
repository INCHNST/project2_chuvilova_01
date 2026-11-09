import shlex

import prompt
from prettytable import PrettyTable

from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    get_schema,
    insert,
    select,
    update,
    validate_clause,
    validate_table_data,
)
from primitive_db.parser import parse_data_command
from primitive_db.utils import (
    load_metadata,
    load_table_data,
    remove_table_data,
    save_metadata,
    save_table_data,
)

METADATA_FILE = "db_meta.json"
DATA_COMMANDS = {"insert", "select", "update", "delete", "info"}


def print_help():
    print("\n***Операции с данными***")
    print("Функции:")
    print("insert into <таблица> values (<значение1>, ...) - добавить запись")
    print(
        "select from <таблица> where <столбец> = <значение> "
        "- прочитать записи по условию"
    )
    print("select from <таблица> - прочитать все записи")
    print(
        "update <таблица> set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить записи"
    )
    print("delete from <таблица> where <столбец> = <значение> - удалить записи")
    print("info <таблица> - информация о таблице")

    print("\nУправление таблицами:")
    print("create_table <таблица> <столбец:тип> ...")
    print("list_tables")
    print("drop_table <таблица>")

    print("\nОбщие команды:")
    print("help - справочная информация")
    print("exit - выход из программы")
    print('Строки: "текст". Логические значения: true и false.\n')


def print_rows(schema, rows):
    table = PrettyTable()
    table.field_names = list(schema)

    for row in rows:
        table.add_row([row[column] for column in schema])

    print(table)

    if not rows:
        print("Подходящих записей нет.")


def handle_data_command(metadata, parsed):
    command = parsed["command"]
    table_name = parsed["table"]
    schema = get_schema(metadata, table_name)

    table_data = load_table_data(table_name)
    validate_table_data(schema, table_data)

    where_clause = parsed.get("where")

    if where_clause is not None:
        validate_clause(schema, where_clause)

    if command == "info":
        columns_text = ", ".join(metadata[table_name])
        print(f"Таблица: {table_name}")
        print(f"Столбцы: {columns_text}")
        print(f"Количество записей: {len(table_data)}")
        return

    if command == "select":
        rows = select(table_data, where_clause)
        print_rows(schema, rows)
        return

    if command == "insert":
        table_data = insert(
            metadata,
            table_name,
            parsed["values"],
        )
        save_table_data(table_name, table_data)

        new_id = table_data[-1]["ID"]
        print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
        return

    matched_rows = select(table_data, where_clause)
    matched_ids = [row["ID"] for row in matched_rows]

    if command == "update":
        set_clause = parsed["set"]
        validate_clause(schema, set_clause)

        table_data = update(
            table_data,
            set_clause,
            where_clause,
        )
    else:
        table_data = delete(table_data, where_clause)

    if not matched_ids:
        print("Подходящих записей нет.")
        return

    save_table_data(table_name, table_data)

    for row_id in matched_ids:
        if command == "update":
            print(f'Запись с ID={row_id} в таблице "{table_name}" успешно обновлена.')
        else:
            print(f'Запись с ID={row_id} успешно удалена из таблицы "{table_name}".')


def handle_table_command(metadata, args):
    command = args[0]

    if command == "list_tables":
        if len(args) != 1:
            raise ValueError("У list_tables нет аргументов.")

        if not metadata:
            print("Таблиц пока нет.")
        else:
            for table_name in sorted(metadata):
                print(f"- {table_name}")

        return

    previous_metadata = metadata.copy()

    if command == "create_table":
        if len(args) < 3:
            raise ValueError("Укажите имя таблицы и хотя бы один столбец.")

        table_name = args[1]
        metadata = create_table(metadata, table_name, args[2:])

    elif command == "drop_table":
        if len(args) != 2:
            raise ValueError("Укажите одно имя таблицы.")

        table_name = args[1]
        metadata = drop_table(metadata, table_name)

    else:
        print(f"Функции {command} нет. Попробуйте снова.")
        return

    if metadata == previous_metadata:
        return

    if command == "create_table":
        save_table_data(table_name, [])

    save_metadata(METADATA_FILE, metadata)

    if command == "create_table":
        columns_text = ", ".join(metadata[table_name])
        print(f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}')
    else:
        remove_table_data(table_name)
        print(f'Таблица "{table_name}" успешно удалена.')


def run():
    print_help()

    while True:
        try:
            user_input = prompt.string(">>>Введите команду: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        text = user_input.strip()

        if not text:
            continue

        try:
            command = text.split(maxsplit=1)[0]

            if command in {"help", "exit"}:
                if text != command:
                    raise ValueError(f"У команды {command} нет аргументов.")

                if command == "exit":
                    break

                print_help()
                continue

            metadata = load_metadata(METADATA_FILE)

            if command in DATA_COMMANDS:
                parsed = parse_data_command(text)
                handle_data_command(metadata, parsed)
            else:
                args = shlex.split(text)
                handle_table_command(metadata, args)

        except ValueError as error:
            print(f"Некорректное значение: {error} Попробуйте снова.")
        except OSError as error:
            print(f"Ошибка работы с файлами: {error}")
