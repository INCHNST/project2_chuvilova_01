import json


def read_assignment(text):
    """Разобрать присваивание и вернуть словарь и остаток текста."""
    column_name, separator, value_text = text.strip().partition("=")
    column_name = column_name.strip()

    if not separator or not column_name.isidentifier():
        raise ValueError("Ожидается условие вида: столбец = значение.")

    value_text = value_text.lstrip()

    try:
        value, position = json.JSONDecoder().raw_decode(value_text)
    except json.JSONDecodeError as error:
        raise ValueError("Строки заключайте в двойные кавычки.") from error

    if type(value) not in (int, str, bool):
        raise ValueError("Поддерживаются только int, str и bool.")

    return {column_name: value}, value_text[position:].strip()


def parse_where(text):
    """Преобразовать одно условие равенства в словарь."""
    clause, remainder = read_assignment(text)

    if remainder:
        raise ValueError("После условия обнаружен лишний текст.")

    return clause


def parse_set(text):
    """Преобразовать присваивание одного поля в словарь."""
    return parse_where(text)


def parse_insert_values(text):
    """Преобразовать список JSON значений в список Python."""
    try:
        values = json.loads(f"[{text}]")
    except json.JSONDecodeError as error:
        raise ValueError('Пример значений: ("Sergei", 28, true).') from error

    if not all(type(value) in (int, str, bool) for value in values):
        raise ValueError("Поддерживаются только int, str и bool.")

    return values


def parse_data_command(text):
    """Разобрать CRUD команду, сохранив кавычки в значениях."""
    text = text.strip()

    if not text:
        raise ValueError("Введите команду.")

    command = text.split(maxsplit=1)[0]

    if command == "insert":
        parts = text.split(maxsplit=4)

        if len(parts) == 5 and parts[1] == "into" and parts[3] == "values":
            values_text = parts[4].strip()

            if values_text.startswith("(") and values_text.endswith(")"):
                return {
                    "command": "insert",
                    "table": parts[2],
                    "values": parse_insert_values(values_text[1:-1]),
                }

    elif command == "select":
        parts = text.split(maxsplit=3)

        if len(parts) >= 3 and parts[1] == "from":
            condition = None

            if len(parts) == 4:
                tail = parts[3].split(maxsplit=1)

                if len(tail) != 2 or tail[0] != "where":
                    raise ValueError("Ожидается where и условие.")

                condition = parse_where(tail[1])

            return {
                "command": "select",
                "table": parts[2],
                "where": condition,
            }

    elif command == "update":
        parts = text.split(maxsplit=3)

        if len(parts) == 4 and parts[2] == "set":
            assignment_text = parts[3]
            _, remainder = read_assignment(assignment_text)
            tail = remainder.split(maxsplit=1)

            if len(tail) != 2 or tail[0] != "where":
                raise ValueError("Для update требуется условие where.")

            set_text = assignment_text[: len(assignment_text) - len(remainder)]

            return {
                "command": "update",
                "table": parts[1],
                "set": parse_set(set_text),
                "where": parse_where(tail[1]),
            }

    elif command == "delete":
        parts = text.split(maxsplit=4)

        if len(parts) == 5 and parts[1] == "from" and parts[3] == "where":
            return {
                "command": "delete",
                "table": parts[2],
                "where": parse_where(parts[4]),
            }

    elif command == "info":
        parts = text.split()

        if len(parts) == 2:
            return {
                "command": "info",
                "table": parts[1],
            }

    raise ValueError("Некорректный синтаксис команды.")
