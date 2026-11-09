import time
from copy import deepcopy
from functools import wraps


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден. Возможно, база не инициализирована.")
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except OSError as error:
            print(f"Ошибка работы с файлами: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")

        return None

    return wrapper


def confirm_action(action_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                answer = input(
                    f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
                )
            except (EOFError, KeyboardInterrupt):
                print("\nОперация отменена.")
                return None

            if answer.strip() != "y":
                print("Операция отменена.")
                return None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            duration = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд")

    return wrapper


def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            print("Результат получен из кэша.")
        else:
            cache[key] = deepcopy(value_func())

        return deepcopy(cache[key])

    cache_result.clear = cache.clear
    return cache_result
