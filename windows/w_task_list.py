from enum import Enum

from lib.helpers import Helpers

from objects.task import Task

from windows.window import Window
from windows.w_task import W_Task
from widgets.helper_bar import HelperBar
from widgets.scroll_list import ScrollList
from widgets.text_input import TextInput


class ListMode(Enum):
    NAVIGATE = 0
    CREATE = 1
    DELETE = 2
    RENAME = 3


class W_TaskList(Window):
    def __init__(self, app:'TodoApp', parent_list:'TaskList'):
        super().__init__(app)
        self.parent:'TaskList' = parent_list
        self.mode:int = ListMode.NAVIGATE

        self.options:dict[str,str] = {
            'a' : "Create Task",
            'd' : "Delete Task",
            'r' : "Rename Task",
            'c' : "Toggle Closed Tasks",
            'h' : "Go Back",
            'l' : "View Task",
            'q' : "Quit"
        }

        self.input_buffer:str = ""

        self.tasks:list[Task] = []
        self.show_closed_tasks:bool = False
        self.load_tasks()
        self.task_selected:int = 0


    def load_tasks(self):
        self.tasks = self.app.service.get_tasks(
            parent_uid = self.parent.uid,
            parent_is_task = False,
            show_closed_tasks = self.show_closed_tasks
        )


    def get_selected_task(self) -> Task | None:
        if len(self.tasks) == 0:
            return None

        return self.tasks[self.task_selected]


    def render_task_columns(self, screen) -> list[str]:
        columns:list[str] = []
        render:str
        width:int = screen.getmaxyx()[1]

        for task in self.tasks:
            render = Helpers.limit_text(task.name, width // 2 - 3)

            while len(render) < (width // 2 - 2):
                render += ' '

            render += task.status_string()

            while len(render) < (width - 16):
                render += ' '

            render += task.priority_string()

            columns.append(render)

        return columns


    def render(self, screen):
        height:int
        width:int
        height, width = screen.getmaxyx()

        parent_text:str = f"{self.parent.name} - Closed Tasks: "
        parent_text += ("Show" if self.show_closed_tasks else "Hide")
        parent_text = Helpers.limit_text(parent_text, (width - 1))

        screen.addstr(0, 0, parent_text)

        screen.addstr(2, 0, "Task Name")
        screen.addstr(2, width // 2, "Task Status")
        screen.addstr(2, width - 14, "Task Priority")

        task_columns:list[str] = self.render_task_columns(screen)

        ScrollList.render_list(
            screen, 4, len(self.options),
            task_columns, self.task_selected
        )

        match(self.mode):
            case ListMode.NAVIGATE:
                HelperBar.render_options(screen, self.options)

            case ListMode.CREATE:
                HelperBar.render_input(
                    screen,
                    prompt = "Task Name",
                    buffer = self.input_buffer
                )

            case ListMode.DELETE:
                task_name:str = self.get_selected_task().name

                prompt_text:str = (
                    "Are you sure you want to delete "
                    f"Task \"{task_name}\"? (y/n)"
                )

                HelperBar.render_confirm(screen, prompt = prompt_text)

            case ListMode.RENAME:
                HelperBar.render_input(
                    screen,
                    prompt = "Task Name",
                    buffer = self.input_buffer
                )


    def _handle_navigate(self, key:str):
        match(key):
            case 'q':
                self.app.running = False

            case 'j':
                self.task_selected = min(
                    self.task_selected + 1, len(self.tasks) - 1
                )

            case 'k':
                self.task_selected = max(
                    self.task_selected - 1, 0
                )

            case 'a':
                self.mode = ListMode.CREATE

            case 'd':
                if len(self.tasks) != 0:
                    self.mode = ListMode.DELETE

            case 'r':
                if len(self.tasks) != 0:
                    self.mode = ListMode.RENAME

            case 'c':
                self.show_closed_tasks = not self.show_closed_tasks
                self.load_tasks()

            case 'h':
                self.app.pop_window_stack()

            case 'l':
                if len(self.tasks) != 0:
                    self.app.window_stack.append(
                        W_Task(self.app, self.get_selected_task())
                    )


    def _handle_text_input(self, key):
        response:tuple[str,bool] = TextInput.handle_input(
            self.input_buffer, key
        )

        new_buffer:str = response[0]
        submit:bool = response[1]

        if submit:
            if new_buffer != "":
                if self.mode == ListMode.CREATE:
                    new_task:Task = self.app.service.create_task(
                        task = Task(new_buffer),
                        parent_uid = self.parent.uid,
                        parent_is_task = False
                    )

                    self.load_tasks()
                elif self.mode == ListMode.RENAME:
                    self.app.service.rename_task(
                        uid = self.get_selected_task().uid,
                        name = new_buffer
                    )

                    self.tasks[self.task_selected].name = new_buffer

            self.input_buffer = ""
            self.mode = ListMode.NAVIGATE
        else:
            self.input_buffer = new_buffer


    def _handle_deletion(self, key):
        if key in "nq\\":
            self.mode = ListMode.NAVIGATE

        if key == 'y':
            self.app.service.delete_task(self.get_selected_task())

            del self.tasks[self.task_selected]

            self.task_selected = max(
                self.task_selected, len(self.tasks) - 1
            )

            self.mode = ListMode.NAVIGATE


    def handle_input(self, key:str):
        match(self.mode):
            case ListMode.NAVIGATE: self._handle_navigate(key)
            case ListMode.CREATE: self._handle_text_input(key)
            case ListMode.DELETE: self._handle_deletion(key)
            case ListMode.RENAME: self._handle_text_input(key)

