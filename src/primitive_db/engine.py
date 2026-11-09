import shlex

import prompt

from primitive_db.core import create_table, drop_table
from primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print_help()

    while True:
        try:
            metadata = load_metadata(METADATA_FILE)
        except (OSError, ValueError) as error:
            print(f"Ошибка чтения метаданных: {error}")
            return

        try:
            user_input = prompt.string(">>>Введите команду: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]

        if command == "exit":
            if len(args) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            break

        if command == "help":
            if len(args) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            print_help()
            continue

        if command == "list_tables":
            if len(args) != 1:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            if not metadata:
                print("Таблиц пока нет.")
            else:
                for table_name in sorted(metadata):
                    print(f"- {table_name}")

            continue

        previous_metadata = metadata.copy()

        if command == "create_table":
            if len(args) < 3:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = args[1]
            columns = args[2:]
            metadata = create_table(metadata, table_name, columns)

        elif command == "drop_table":
            if len(args) != 2:
                print(f"Некорректное значение: {user_input}. Попробуйте снова.")
                continue

            table_name = args[1]
            metadata = drop_table(metadata, table_name)

        else:
            print(f"Функции {command} нет. Попробуйте снова.")
            continue

        if metadata == previous_metadata:
            continue

        try:
            save_metadata(METADATA_FILE, metadata)
        except OSError as error:
            print(f"Ошибка сохранения метаданных: {error}")
            continue

        if command == "create_table":
            columns_text = ", ".join(metadata[table_name])
            print(
                f'Таблица "{table_name}" успешно создана со столбцами: {columns_text}'
            )
        else:
            print(f'Таблица "{table_name}" успешно удалена.')
