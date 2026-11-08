import prompt


def welcome():
    help_text = (
        "<command> exit - выйти из программы\n"
        "<command> help - справочная информация"
    )

    print("Первая попытка запустить проект!")
    print()
    print("***")
    print(help_text)

    while True:
        command = prompt.string("Введите команду: ").strip()

        if command == "exit":
            break

        if command == "help":
            print()
            print(help_text)
        else:
            print("Неизвестная команда. Введите help.")
