from enum import Enum

from lib.helpers import Helpers
from lib.order_enums import TaskOrderKey, TaskOrderValue

from objects.task import Task
from objects.comment import Comment

from windows.window import Window
from widgets.helper_bar import HelperBar
from widgets.scroll_list import ScrollList
from widgets.text_input import TextInput
from widgets.text_box import TextBox


class TaskMode(Enum):
    DESCRIPTION_NAV     = 0
    TASK_RENAME         = 1
    TASK_STATUS         = 2
    TASK_PRIORITY       = 3
    DESCRIPTION_EDIT    = 4
    SUBTASK_NAV         = 5
    SUBTASK_CREATE      = 6
    SUBTASK_DELETE      = 7
    SUBTASK_RENAME      = 8
    SUBTASK_STATUS      = 9
    SUBTASK_PRIORITY    = 10
    COMMENT_NAV         = 11
    COMMENT_CREATE      = 12
    COMMENT_DELETE      = 13
    COMMENT_EDIT        = 14
    SUBTASK_ORDER       = 15


class W_Task(Window):
    def __init__(self, app:'TodoApp', parent_task:Task):
        super().__init__(app)
        self.parent:Task = parent_task
        self.mode:int = TaskMode.DESCRIPTION_NAV
        self.last_mode:int = -1

        self.options_description:dict[str,str] = {
            'r' : "Rename Task",
            's' : "Change Task Status",
            'p' : "Change Task Priority",
            'e' : "Edit Description",
            'c' : "Toggle Closed SubTasks",
            'o' : "Change SubTask Order",
            '2' : "Navigate SubTasks",
            '3' : "Nagivate Comments",
            'h' : "Go Back",
            'q' : "Quit"
        }

        self.options_subtasks:dict[str,str] = {
            'a' : "Create SubTask",
            'd' : "Delete SubTask",
            'r' : "Rename SubTask",
            's' : "Change SubTask Status",
            'p' : "Change SubTask Priority",
            'c' : "Toggle Closed SubTasks",
            'o' : "Change SubTask Order",
            '1' : "Navigate Description",
            '3' : "Navigate Comments",
            'h' : "Go Back",
            'l' : "View SubTask",
            'q' : "Quit"
        }

        self.options_comments:dict[str,str] = {
            'r' : "Rename Task",
            's' : "Change Task Status",
            'p' : "Change Task Priority",
            'a' : "Create Comment",
            'd' : "Delete Comment",
            'e' : "Edit Comment",
            'c' : "Toggle Closed SubTasks",
            'o' : "Change SubTask Order",
            '1' : "Navigate Description",
            '2' : "Navigate SubTasks",
            'h' : "Go Back",
            'q' : "Quit"
        }

        self.orders:dict[str,str] = {
            'e' : "Default",
            'a' : "Ascending",
            'd' : "Descending",
            'r' : "Random"
        }

        self.input_buffer:str = ""

        self.description_scroll:int = 0

        self.subtasks:list[Task] = []
        self.show_closed_subtasks:bool = False
        self.subtasks_order = TaskOrderValue.DEFAULT
        self.load_subtasks()
        self.subtask_selected:int = 0

        self.comment_selected:int = 0


    def load_subtasks(self):
        self.subtasks = self.app.service.get_tasks(
            parent_uid = self.parent.uid,
            parent_is_task = True,
            show_closed_tasks = self.show_closed_subtasks,
            order_key = TaskOrderKey.NAME,
            order_value = self.subtasks_order
        )


    def get_selected_subtask(self) -> Task | None:
        if len(self.subtasks) == 0:
            return None

        return self.subtasks[self.subtask_selected]


    def get_selected_comment(self) -> Comment | None:
        if len(self.parent.comments) == 0:
            return None

        return self.parent.comments[self.comment_selected]


    def stringify_comments(self, width:int) -> list[str]:
        string_comments:list[str] = []
        render:str = ""

        for comment in self.parent.comments:
            render = Helpers.date_to_string(comment.date) + '\n'
            render += Helpers.wrap_text(
                text = comment.body, limit = width
            )

            string_comments.append(render)

        return string_comments


    def render(self, screen):
        height:int
        width:int
        height, width = screen.getmaxyx()

        task_text:str = f"{self.parent.name} - Closed SubTasks: "
        task_text += ("Show" if self.show_closed_subtasks else "Hide")
        task_text = Helpers.limit_text(task_text, (width - 1))

        screen.addstr(0, 0, task_text)

        date_label:str = (
            f"Created on: {Helpers.date_to_string(self.parent.date)}"
        )

        screen.addstr(1, 0, date_label)

        screen.addstr(2, 0, f"Status: {self.parent.status_string()}")
        screen.addstr(
            3, 0, f"Priority: {self.parent.priority_string()}"
        )
        screen.addstr(5, 0, "Description:")

        header_space:int = 6
        footer_space:int = max(
            len(self.options_description),
            len(self.options_subtasks),
            len(self.options_comments)
        )
        usable_space:int = height - header_space - footer_space - 1

        description_space:int = usable_space // 2
        subtask_space:int = usable_space - description_space

        left_panel_width:int = int(width * 0.6)
        right_panel_width:int = width - left_panel_width - 2

        # Approximate what an appropriate amount of scrolling is
        scroll_limit:int = len(self.parent.description)
        scroll_limit //= left_panel_width
        modifier:int = scroll_limit // 5
        scroll_limit -= description_space
        scroll_limit += modifier

        self.description_scroll = min(
            self.description_scroll, scroll_limit
        )

        TextBox.render_box(
            screen, header_space + 1, 0,
            description_space + header_space, left_panel_width,
            self.description_scroll,
            self.parent.description
        )

        screen.addstr(
            header_space + description_space + 1, 0, "SubTasks:"
        )

        subtask_names:list[str] = [
            task.name for task in self.subtasks
        ]

        ScrollList.render_list(
            screen, header_space + description_space + 2,
            footer_space, subtask_names, self.subtask_selected
        )

        screen.addstr(0, left_panel_width + 1, "Comments:")

        string_comments:list[str] = self.stringify_comments(
            width = right_panel_width
        )

        ScrollList.render_list(
            screen, 2, footer_space,
            string_comments, self.comment_selected,
            x_align = left_panel_width + 1,
            line_separated = True
        )

        help_prompt:str

        match(self.mode):
            case TaskMode.DESCRIPTION_NAV:
                HelperBar.render_options(
                    screen, self.options_description
                )

            case TaskMode.TASK_RENAME:
                HelperBar.render_input(
                    screen,
                    prompt = "Task Name",
                    buffer = self.input_buffer
                )


            case TaskMode.TASK_STATUS:
                help_prompt = (
                    "Select new Task Status (0 : Open) "
                    "(1 : In Progress) (2 : Closed) ; Task Status"
                )

                HelperBar.render_input(
                    screen,
                    prompt = help_prompt,
                    buffer = self.input_buffer
                )

            case TaskMode.TASK_PRIORITY:
                help_prompt = (
                    "Select new Task Priority (0 : Low) (1 : Medium) "
                    "(2 : High) (3 : Urgent) ; Task Priority"
                )

                HelperBar.render_input(
                    screen,
                    prompt = help_prompt,
                    buffer = self.input_buffer
                )

            case TaskMode.DESCRIPTION_EDIT:
                HelperBar.render_input(
                    screen,
                    prompt = "Description",
                    buffer = self.input_buffer
                )

            case TaskMode.SUBTASK_NAV:
                HelperBar.render_options(
                    screen, self.options_subtasks
                )

            case TaskMode.SUBTASK_CREATE:
                HelperBar.render_input(
                    screen,
                    prompt = "SubTask Name",
                    buffer = self.input_buffer
                )

            case TaskMode.SUBTASK_DELETE:
                subtask_name:str = self.get_selected_subtask().name

                prompt_text:str = (
                    "Are you sure you want to delete "
                    f"SubTask \"{subtask_name}\"? (y/n)"
                )

                HelperBar.render_confirm(screen, prompt = prompt_text)

            case TaskMode.SUBTASK_RENAME:
                HelperBar.render_input(
                    screen,
                    prompt = "SubTask Name",
                    buffer = self.input_buffer
                )
        
            case TaskMode.SUBTASK_STATUS:
                help_prompt = (
                    "Select new SubTask Status (0 : Open) "
                    "(1 : In Progress) (2 : Closed) ; Task Status"
                )

                HelperBar.render_input(
                    screen,
                    prompt = help_prompt,
                    buffer = self.input_buffer
                )

            case TaskMode.SUBTASK_PRIORITY:
                help_prompt = (
                    "Select new SubTask Priority (0 : Low) "
                    "(1 : Medium) (2 : High) (3 : Urgent) "
                    "; SubTask Priority"
                )

                HelperBar.render_input(
                    screen,
                    prompt = help_prompt,
                    buffer = self.input_buffer
                )

            case TaskMode.COMMENT_NAV:
                HelperBar.render_options(
                    screen, self.options_comments
                )

            case TaskMode.COMMENT_CREATE:
                HelperBar.render_input(
                    screen,
                    prompt = "Comment",
                    buffer = self.input_buffer
                )

            case TaskMode.COMMENT_DELETE:
                prompt_text:str = (
                    "Are you sure you want to "
                    "delete this comment? (y/n)"
                )

                HelperBar.render_confirm(screen, prompt = prompt_text)

            case TaskMode.COMMENT_EDIT:
                HelperBar.render_input(
                    screen,
                    prompt = "Comment",
                    buffer = self.input_buffer
                )

            case TaskMode.SUBTASK_ORDER:
                HelperBar.render_multicolumn_options(
                    screen, {"Order" : self.orders}
                )

                HelperBar.render_input(
                    screen,
                    prompt = "Ordering",
                    buffer = self.input_buffer
                )


    def _handle_desc_nav(self, key):
        match(key):
            case 'q': self.app.running = False

            case 'j':
                if self.parent.description != "":
                    self.description_scroll += 1

            case 'k':
                if self.parent.description != "":
                    self.description_scroll = max(
                        self.description_scroll - 1, 0
                    )

            case 'r': self.mode = TaskMode.TASK_RENAME
            case 's': self.mode = TaskMode.TASK_STATUS
            case 'p': self.mode = TaskMode.TASK_PRIORITY
            case 'e': self.mode = TaskMode.DESCRIPTION_EDIT

            case 'c':
                self.show_closed_subtasks = (
                    not self.show_closed_subtasks
                )
                self.load_subtasks()

            case 'o': self.mode = TaskMode.SUBTASK_ORDER

            case '2': self.mode = TaskMode.SUBTASK_NAV
            case '3': self.mode = TaskMode.COMMENT_NAV
            case 'h': self.app.pop_window_stack()

        if self.mode != TaskMode.DESCRIPTION_NAV:
            self.last_mode = TaskMode.DESCRIPTION_NAV


    def _handle_subtask_nav(self, key:str):
        match(key):
            case 'q': self.app.running = False
            case 'j':
                self.subtask_selected = min(
                    self.subtask_selected + 1, len(self.subtasks) - 1
                )

            case 'k':
                self.subtask_selected = max(
                    self.subtask_selected - 1, 0
                )

            case 'a': self.mode = TaskMode.SUBTASK_CREATE
            case 'd': self.mode = TaskMode.SUBTASK_DELETE
            case 'r': self.mode = TaskMode.SUBTASK_RENAME
            case 's': self.mode = TaskMode.SUBTASK_STATUS
            case 'p': self.mode = TaskMode.SUBTASK_PRIORITY

            case 'c':
                self.show_closed_subtasks = (
                    not self.show_closed_subtasks
                )
                self.load_subtasks()

            case 'o': self.mode = TaskMode.SUBTASK_ORDER

            case '1': self.mode = TaskMode.DESCRIPTION_NAV
            case '3': self.mode = TaskMode.COMMENT_NAV
            case 'h': self.app.pop_window_stack()

            case 'l':
                if len(self.subtasks) != 0:
                    self.app.window_stack.append(
                        W_Task(self.app, self.get_selected_subtask())
                    )

        if self.mode != TaskMode.SUBTASK_NAV:
            self.last_mode = TaskMode.SUBTASK_NAV


    def _handle_comment_nav(self, key:str):
        match(key):
            case 'q': self.app.running = False

            case 'j':
                self.comment_selected = min(
                    self.comment_selected + 1,
                    len(self.parent.comments) - 1
                )

            case 'k':
                self.comment_selected = max(
                    self.comment_selected - 1, 0
                )

            case 'r': self.mode = TaskMode.TASK_RENAME
            case 's': self.mode = TaskMode.TASK_STATUS
            case 'p': self.mode = TaskMode.TASK_PRIORITY
            case 'a': self.mode = TaskMode.COMMENT_CREATE
            case 'd': self.mode = TaskMode.COMMENT_DELETE
            case 'e': self.mode = TaskMode.COMMENT_EDIT

            case 'c':
                self.show_closed_subtasks = (
                    not self.show_closed_subtasks
                )
                self.load_subtasks()

            case 'o': self.mode = TaskMode.SUBTASK_ORDER
            case '1': self.mode = TaskMode.DESCRIPTION_NAV
            case '2': self.mode = TaskMode.SUBTASK_NAV
            case 'h': self.app.pop_window_stack()

        if self.mode != TaskMode.COMMENT_NAV:
            self.last_mode = TaskMode.COMMENT_NAV


    def scrub_status(self, status:str) -> int:
        status = status.lower()

        if status in ['0', 'r', 'o', "not started", "reset", "open"]:
            return 0

        if status in ['1', 'p', "in progress", "start", "started"]:
            return 1

        if status in ['2', 'c', "closed", "close"]:
            return 2

        return -1

    
    def scrub_priority(self, priority:str) -> int:
        priority = priority.lower()

        if priority in ['0', 'l', "low"]:
            return 0

        if priority in ['1', 'm', "mid", "med", "medium"]:
            return 1

        if priority in ['2', 'h', "high", "hi"]:
            return 2

        if priority in ['3', 'u', "urgent", "mayday", "red alert"]:
            return 3

        return -1


    def _parse_ordering_mode(self, new_buffer:str):
        key:str = new_buffer[0]

        match(key):
            case 'e':
                self.subtasks_order = TaskOrderValue.DEFAULT

            case 'a':
                self.subtasks_order = TaskOrderValue.ASCENDING

            case 'd':
                self.subtasks_order = TaskOrderValue.DESCENDING

            case 'r':
                self.subtasks_order = TaskOrderValue.RANDOM

        self.load_subtasks()


    def _submit_text_buffer(self, new_buffer:str):
        match(self.mode):
            case TaskMode.TASK_RENAME:
                self.parent.name = new_buffer
                self.app.service.rename_task(
                    task_uid = self.parent.uid,
                    name = new_buffer
                )

            case TaskMode.TASK_STATUS:
                new_status:int = self.scrub_status(new_buffer)

                if new_status != -1:
                    self.parent.change_status(
                        status = new_status,
                        service = self.app.service
                    )

                    s_string:str = self.parent.status_string()
                    self.parent.post_comment(
                        f"Status changed to {s_string}",
                        self.app.service
                    )

            case TaskMode.TASK_PRIORITY:
                new_priority:int = self.scrub_priority(
                    new_buffer
                )

                if new_priority != -1:
                    self.parent.change_priority(
                        priority = new_priority,
                        service = self.app.service
                    )

                    p_string:str = self.parent.priority_string()
                    self.parent.post_comment(
                        f"Priority changed to {p_string}",
                        self.app.service
                    )

            case TaskMode.DESCRIPTION_EDIT:
                self.parent.description = new_buffer
                self.app.service.set_task_description(
                    task_uid = self.parent.uid,
                    description = new_buffer
                )

            case TaskMode.SUBTASK_CREATE:
                new_task:Task = self.app.service.create_task(
                    task = Task(new_buffer),
                    parent_uid = self.parent.uid,
                    parent_is_task = True
                )

                self.load_subtasks()

            case TaskMode.SUBTASK_RENAME:
                self.app.service.rename_task(
                    uid = self.get_selected_subtask().uid,
                    name = new_buffer
                )

                self.subtasks[self.subtask_selected].name = (
                    new_buffer
                )

            case TaskMode.SUBTASK_STATUS:
                new_status:int = self.scrub_status(new_buffer)

                if new_status != -1:
                    subtask:Task = self.get_selected_subtask()

                    subtask.change_status(
                        status = new_status,
                        service = self.app.service
                    )

                    s_string:str = subtask.status_string()
                    subtask.post_comment(
                        f"Status changed to {s_string}",
                        self.app.service
                    )

            case TaskMode.SUBTASK_PRIORITY:
                new_priority:int = self.scrub_priority(
                    new_buffer
                )

                if new_priority != -1:
                    subtask:Task = self.get_selected_subtask()

                    subtask.change_priority(
                        priority = new_priority,
                        service = self.app.service
                    )

                    p_string:str = subtask.priority_string()
                    subtask.post_comment(
                        f"Priority changed to {p_string}",
                        self.app.service
                    )

            case TaskMode.COMMENT_CREATE:
                self.parent.post_comment(new_buffer, self.app.service)

            case TaskMode.COMMENT_EDIT:
                self.app.service.update_comment(
                    uid = self.get_selected_comment().uid,
                    body = new_buffer
                )

            case TaskMode.SUBTASK_ORDER:
                self._parse_ordering_mode(new_buffer)


    def _handle_text_input(self, key):
        response:tuple[str,bool] = TextInput.handle_input(
            self.input_buffer, key
        )

        new_buffer:str = response[0]
        submit:bool = response[1]

        if submit:
            if new_buffer != "":
                self._submit_text_buffer(new_buffer)

            self.input_buffer = ""
            self.mode = self.last_mode
        else:
            self.input_buffer = new_buffer


    def _handle_subtask_deletion(self, key):
        if key in "nq\\":
            self.mode = TaskMode.SUBTASK_NAV

        if key == 'y':
            self.app.service.delete_task(self.get_selected_subtask())

            del self.subtasks[self.subtask_selected]

            self.subtask_selected = min(max(
                self.subtask_selected, len(self.subtasks) - 1
            ), 0)

            self.mode = TaskMode.SUBTASK_NAV


    def _handle_comment_deletion(self, key):
        if key in "nq\\":
            self.mode = TaskMode.COMMENT_NAV

        if key == 'y':
            self.app.service.delete_comment(
                self.get_selected_comment()
            )

            del self.parent.comments[self.comment_selected]

            self.comment_selected = min(max(
                self.comment_selected, len(self.parent.comments) - 1
            ), 0)

            self.mode = TaskMode.COMMENT_NAV


    def handle_input(self, key:str):
        match(self.mode):
            case TaskMode.DESCRIPTION_NAV: self._handle_desc_nav(key)
            case TaskMode.TASK_RENAME: self._handle_text_input(key)
            case TaskMode.TASK_STATUS: self._handle_text_input(key)
            case TaskMode.TASK_PRIORITY: self._handle_text_input(key)
            case TaskMode.DESCRIPTION_EDIT: self._handle_text_input(key)

            case TaskMode.SUBTASK_NAV: self._handle_subtask_nav(key)
            case TaskMode.SUBTASK_CREATE: self._handle_text_input(key)

            case TaskMode.SUBTASK_DELETE:
                self._handle_subtask_deletion(key)

            case TaskMode.SUBTASK_RENAME: self._handle_text_input(key)
            case TaskMode.SUBTASK_STATUS: self._handle_text_input(key)
            case TaskMode.SUBTASK_PRIORITY: self._handle_text_input(key)

            case TaskMode.COMMENT_NAV: self._handle_comment_nav(key)
            case TaskMode.COMMENT_CREATE: self._handle_text_input(key)

            case TaskMode.COMMENT_DELETE:
                self._handle_comment_deletion(key)

            case TaskMode.COMMENT_EDIT: self._handle_text_input(key)
            case TaskMode.SUBTASK_ORDER: self._handle_text_input(key)

