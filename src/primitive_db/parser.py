import json
import re


def read_assignment(text):
    match = re.match(r"\s*(\w+)\s*=\s*", text)

    if match is None:
        raise ValueError("Ожидается условие вида: столбец = значение.")

    column_name = match.group(1)

    if not column_name.isidentifier():
        raise ValueError("Некорректное имя столбца.")

    value_text = text[match.end() :]

    try:
        value, position = json.JSONDecoder().raw_decode(value_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "Некорректное значение. Строки заключайте в двойные кавычки."
        ) from error

    if type(value) not in (int, str, bool):
        raise ValueError("Поддерживаются только int, str и bool.")

    remainder = value_text[position:].strip()
    return {column_name: value}, remainder


def parse_where(text):
    clause, remainder = read_assignment(text)

    if remainder:
        raise ValueError("После условия обнаружен лишний текст.")

    return clause


def parse_set(text):
    return parse_where(text)


def parse_insert_values(text):
    try:
        values = json.loads(f"[{text}]")
    except json.JSONDecodeError as error:
        raise ValueError(
            'Некорректные значения. Пример: ("Sergei", 28, true).'
        ) from error

    if not all(type(value) in (int, str, bool) for value in values):
        raise ValueError("Поддерживаются только int, str и bool.")

    return values


def parse_data_command(text):
    text = text.strip()

    match = re.fullmatch(
        r"insert\s+into\s+(\w+)\s+values\s*\((.*)\)",
        text,
    )
    if match:
        return {
            "command": "insert",
            "table": match.group(1),
            "values": parse_insert_values(match.group(2)),
        }

    match = re.fullmatch(
        r"select\s+from\s+(\w+)(?:\s+where\s+(.+))?",
        text,
    )
    if match:
        condition = match.group(2)

        return {
            "command": "select",
            "table": match.group(1),
            "where": parse_where(condition) if condition else None,
        }

    match = re.fullmatch(
        r"update\s+(\w+)\s+set\s+(.+)",
        text,
    )
    if match:
        assignment_text = match.group(2)
        _, remainder = read_assignment(assignment_text)

        where_match = re.fullmatch(r"where\s+(.+)", remainder)

        if where_match is None:
            raise ValueError("Для update требуется условие where.")

        set_text = assignment_text[: len(assignment_text) - len(remainder)].strip()

        return {
            "command": "update",
            "table": match.group(1),
            "set": parse_set(set_text),
            "where": parse_where(where_match.group(1)),
        }

    match = re.fullmatch(
        r"delete\s+from\s+(\w+)\s+where\s+(.+)",
        text,
    )
    if match:
        return {
            "command": "delete",
            "table": match.group(1),
            "where": parse_where(match.group(2)),
        }

    match = re.fullmatch(r"info\s+(\w+)", text)
    if match:
        return {
            "command": "info",
            "table": match.group(1),
        }

    raise ValueError("Некорректный синтаксис команды.")
