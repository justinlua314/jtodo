from curses import wrapper

from objects.todo_app import TodoApp


def main(screen):
    app = TodoApp()
    app.run(screen)


if __name__ == "__main__":
    wrapper(main)

