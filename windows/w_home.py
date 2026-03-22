from enum import Enum

from objects.task_list import TaskList

from windows.window import Window
from windows.w_task_list import W_TaskList
from widgets.helper_bar import HelperBar
from widgets.scroll_list import ScrollList
from widgets.text_input import TextInput


class ListMode(Enum):
    NAVIGATE = 0
    CREATE = 1
    DELETE = 2
    RENAME = 3


class W_Home(Window):
    def __init__(self, app:'TodoApp'):
        super().__init__(app)
        self.mode:int = ListMode.NAVIGATE

        self.options:dict[str,str] = {
            'a' : "Create Task List",
            'd' : "Delete Task List",
            'r' : "Rename Task List",
            'l' : "View Task List",
            'q' : "Quit"
        }

        self.input_buffer:str = ""

        self.task_lists:list[TaskList] = []
        self.load_task_lists()
        self.task_list_selected:int = 0


    def load_task_lists(self):
        self.task_lists = self.app.service.get_task_lists()


    def get_selected_list(self) -> TaskList | None:
        if len(self.task_lists) == 0:
            return None

        return self.task_lists[self.task_list_selected]


    def render(self, screen):
        screen.addstr(0, 0, "Task Lists")

        task_list_names:list[str] = [
            tl.name for tl in self.task_lists
        ]

        ScrollList.render_list(
            screen, 2, len(self.options),
            task_list_names, self.task_list_selected
        )

        match(self.mode):
            case ListMode.NAVIGATE:
                HelperBar.render_options(screen, self.options)

            case ListMode.CREATE:
                HelperBar.render_input(
                    screen,
                    prompt = "Task List Name",
                    buffer = self.input_buffer
                )

            case ListMode.DELETE:
                list_name:str = self.get_selected_list().name

                prompt_text:str = (
                    "Are you sure you want to delete "
                    f"Task List \"{list_name}\"? (y/n)"
                )

                HelperBar.render_confirm(screen, prompt = prompt_text)

            case ListMode.RENAME:
                HelperBar.render_input(
                    screen,
                    prompt = "Task List Name",
                    buffer = self.input_buffer
                )


    def _handle_navigate(self, key:str):
        match(key):
            case 'q':
                self.app.running = False

            case 'j':
                self.task_list_selected = min(
                    self.task_list_selected + 1,
                    len(self.task_lists) - 1
                )

            case 'k':
                self.task_list_selected = max(
                    self.task_list_selected - 1, 0
                )

            case 'a':
                self.mode = ListMode.CREATE

            case 'd':
                if len(self.task_lists) != 0:
                    self.mode = ListMode.DELETE

            case 'r':
                if len(self.task_lists) != 0:
                    self.mode = ListMode.RENAME

            case 'l':
                if len(self.task_lists) != 0:
                    self.app.window_stack.append(
                        W_TaskList(self.app, self.get_selected_list())
                    )


    def _handle_text_input(self, key):
        response:tuple[str,bool] = TextInput.handle_input(
            self.input_buffer, key
        )

        new_buffer:str = response[0]
        submit:bool = response[1]

        if submit:
            if new_buffer != "":
                new_tl:TaskList = self.app.service.create_task_list(
                    TaskList(new_buffer)
                )

                self.task_lists.append(new_tl)
                self.load_task_lists()

            self.input_buffer = ""
            self.mode = ListMode.NAVIGATE
        else:
            self.input_buffer = new_buffer


    def _handle_deletion(self, key):
        if key in "nq\\":
            self.mode = ListMode.NAVIGATE

        if key == 'y':
            self.app.service.delete_task_list(
                self.get_selected_list()
            )

            del self.task_lists[self.task_list_selected]

            self.task_list_selected = max(
                self.task_list_selected, len(self.task_lists) - 1
            )

            self.mode = ListMode.NAVIGATE


    def handle_input(self, key:str):
        match(self.mode):
            case ListMode.NAVIGATE: self._handle_navigate(key)
            case ListMode.CREATE: self._handle_text_input(key)
            case ListMode.DELETE: self._handle_deletion(key)
            case ListMode.RENAME: self._handle_text_input(key)

