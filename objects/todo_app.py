from objects.task_service import TaskService
from windows.window import Window
from windows.w_home import W_Home
from windows.w_task_list import W_TaskList
from windows.w_task import W_Task


class TodoApp:
    def __init__(self):
        self.service = TaskService(self)
        self.window_stack:list[Window] = [W_Home(self)]
        self.running:bool = True


    def pop_window_stack(self):
        self.window_stack.pop()

        if len(self.window_stack) == 0:
            exit()

        cur_window:Window = self.window_stack[-1]

        # Refresh cur_window to auto hide closed tasks/subtasks
        # if necessary
        if type(cur_window) == W_TaskList:
            cur_window.load_tasks()
        elif type(cur_window) == W_Task:
            cur_window.load_subtasks()


    def run(self, screen):
        cur_window:Window
        key:str

        while self.running:
            cur_window = self.window_stack[-1]

            screen.erase()
            cur_window.render(screen)
            screen.refresh()

            key = screen.getkey()
            cur_window.handle_input(key)

