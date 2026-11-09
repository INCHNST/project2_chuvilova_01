import time


def preserve_metadata(func, wrapper):
    """Сохранить имя и описание обёрнутой функции."""
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__wrapped__ = func
    return wrapper


def handle_db_errors(func):
    """Обработать ошибки операции базы данных."""

    def wrapper(*args, **kwargs):
        """Выполнить функцию и вывести сообщение об ошибке."""
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

    return preserve_metadata(func, wrapper)


def confirm_action(action_name):
    """Создать декоратор подтверждения указанного действия."""

    def decorator(func):
        """Обернуть функцию запросом подтверждения."""

        def wrapper(*args, **kwargs):
            """Выполнить действие только после ответа y."""
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

        return preserve_metadata(func, wrapper)

    return decorator


def log_time(func):
    """Вывести длительность вызова обёрнутой функции."""

    def wrapper(*args, **kwargs):
        """Измерить вызов функции монотонными часами."""
        start = time.monotonic()

        try:
            return func(*args, **kwargs)
        finally:
            duration = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд")

    return preserve_metadata(func, wrapper)


def create_cacher():
    """Создать функцию кэширования со словарём в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Вернуть сохранённый результат или вычислить новый."""
        if key in cache:
            print("Результат получен из кэша.")
        else:
            cache[key] = value_func()

        return cache[key]

    cache_result.clear = cache.clear
    return cache_result
