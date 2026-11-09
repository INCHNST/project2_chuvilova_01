"""Общие настройки хранения данных и поддерживаемых команд."""

META_FILE = "db_meta.json"
DATA_DIR = "data"

VALID_TYPES = {"int", "str", "bool"}

PYTHON_TYPES = {
    "int": int,
    "str": str,
    "bool": bool,
}

DATA_COMMANDS = {
    "insert",
    "select",
    "update",
    "delete",
    "info",
}
