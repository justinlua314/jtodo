import datetime as dt

from lib.helpers import Helpers

from objects.todo_db import TodoDB
from objects.task_list import TaskList
from objects.task import Task
from objects.comment import Comment


# Handles communication between app and the database
class TaskService:
    def __init__(self, app:'TodoApp'):
        self.db = TodoDB()


    def get_task_lists(self) -> list[TaskList]:
        records:tuple = self.db.load_all_records("tblTaskList")

        task_lists:list[TaskList] = []
        uid:int
        name:str
        task_list:TaskList

        for record in records:
            uid = record[0]
            name = record[1]

            task_list = TaskList(name)
            task_list.uid = uid

            task_lists.append(task_list)

        return task_lists


    def create_task_list(self, task_list:TaskList) -> TaskList:
        uid:int = self.db.submit_record(
            "tblTaskList", (task_list.name, )
        )

        task_list.uid = uid
        return task_list


    def delete_task_list(self, task_list:TaskList):
        # TODO:
        # Delete all records orphaned by the deletion of these Tasks
        self.db.remove_record("tblTask", "TaskListID", task_list.uid)

        self.db.remove_record(
            "tblTaskList", "TaskListID", task_list.uid
        )


    def get_tasks(
        self, parent_uid:int, parent_is_task:bool,
        show_closed_tasks:bool
    ) -> list[Task]:
        records:list[tuple] = self.db.load_all_records("tblTask")

        tasks:list[Task] = []
        db_parent_uid:int
        task:Task

        for record in records:
            if parent_is_task:
                db_parent_uid = record[2]
            else:
                db_parent_uid = record[1]

            if db_parent_uid != parent_uid:
                continue

            if (not show_closed_tasks) and record[5] == 2:
                continue

            task = Task(record[3])
            task.uid = record[0]
            task.parent_uid = parent_uid
            task.date = Helpers.string_to_date(record[4])
            task.status = record[5]
            task.priority = record[6]
            task.description = record[7]

            tasks.append(task)

        return tasks


    def create_task(
        self, task:Task, parent_uid:int, parent_is_task:bool
    ) -> Task:
        tl_uid:int = (None if parent_is_task else parent_uid)
        pt_uid:int = (parent_uid if parent_is_task else None)

        payload:tuple = (
            tl_uid,
            pt_uid,
            task.name,
            Helpers.date_to_string(task.date),
            task.status,
            task.priority,
            task.description
        )

        uid:int = self.db.submit_record("tblTask", payload)

        task.uid = uid
        task.parent_uid = parent_uid
        return task


    def delete_task(self, task:Task):
        # TODO:
        # Delete all records orphaned by the deletion of these Tasks
        self.db.remove_record("tblTask", "TaskID", task.uid)


    def rename_task(self, task_uid:int, name:str):
        self.db.update_record(
            "tblTask", "TaskID", task_uid, "TaskName", name
        )


    def set_task_status(self, task_uid:int, status:int):
        self.db.update_record(
            "tblTask", "TaskID", task_uid, "TaskStatus", status
        )


    def set_task_priority(self, task_uid:int, priority:int):
        self.db.update_record(
            "tblTask", "TaskID", task_uid, "TaskPriority", priority
        )


    def set_task_description(self, task_uid:int, description:str):
        self.db.update_record(
            "tblTask", "TaskID", task_uid, "TaskDesc", description
        )


    def get_comments(self, task_uid:int) -> list[Comment]:
        records:list[tuple] = self.db.load_all_records("tblComment")

        comments:list[Comment] = []
        db_task_uid:int
        comment:Comment

        for record in records:
            db_task_uid = record[1]

            if db_task_uid != task_uid:
                continue

            comment = Comment(record[3])
            comment.uid = record[0]
            comment.task_uid = task_uid
            comment.date = Helpers.string_to_date(record[2])

            comments.append(comment)

        return comments


    def create_comment(
        self, comment:Comment, task_uid:int
    ) -> Comment:
        payload:tuple = (
            task_uid,
            Helpers.date_to_string(comment.date),
            comment.body
        )

        uid:int = self.db.submit_record("tblComment", payload)

        comment.uid = uid
        comment.task_uid = task_uid
        return comment


    def delete_comment(self, comment:Comment):
        self.db.remove_record("tblComment", "CommentID", comment.uid)


    def update_comment(self, uid:int, body:str):
        self.db.update_record(
            "tblComment", "CommentID", uid, "CommentBody", body
        )

