import sqlite3, pathlib


class TodoDB:
    def __init__(self):
        file_path:str = str(pathlib.Path(__file__).parent.resolve())
        file_path += "/../Tasks.sqlite"

        self.connection = sqlite3.connect(file_path)
        self.init_tables()


    def init_tables(self):
        cursor = self.connection.cursor()

        sql:str = (
            "CREATE TABLE IF NOT EXISTS tblTaskList ("
            "TaskListID INTEGER PRIMARY KEY AUTOINCREMENT, "
            "TaskListName TEXT NOT NULL)"
        )

        cursor.execute(sql)


        sql = (
            "CREATE TABLE IF NOT EXISTS tblTask ("
            "TaskID INTEGER PRIMARY KEY AUTOINCREMENT, "
            "TaskListID INTEGER, "
            "ParentTaskID INTEGER, "
            "TaskName TEXT NOT NULL, "
            "TaskDate TEXT NOT NULL, "
            "TaskStatus INTEGER NOT NULL, "
            "TaskPriority INTEGER NOT NULL, "
            "TaskDesc TEXT)"
        )

        cursor.execute(sql)


        sql = (
            "CREATE TABLE IF NOT EXISTS tblComment ("
            "CommentID INTEGER PRIMARY KEY AUTOINCREMENT, "
            "TaskID INTEGER NOT NULL, "
            "CommentDate TEXT NOT NULL, "
            "CommentBody TEXT NOT NULL)"
        )

        cursor.execute(sql)
        self.connection.commit()


    def load_all_records(self, table_name:str) -> list[tuple]:
        cursor = self.connection.cursor()

        sql:str = f"SELECT * FROM {table_name}"
        cursor.execute(sql)

        return cursor.fetchall()


    def remove_record(self, table_name:str, uid_field:str, uid:int):
        cursor = self.connection.cursor()

        sql:str = (
            f"DELETE FROM {table_name} WHERE {uid_field} = {uid}"
        )

        cursor.execute(sql)
        self.connection.commit()


    # new_value should be str or int
    def update_record(
        self, table_name:str, uid_field:str, uid:int,
        target_field:str, new_value
    ):
        cursor = self.connection.cursor()

        sql:str = (
            f"UPDATE {table_name} "
            f"SET {target_field} = ? "
            f"WHERE {uid_field} = ?"
        )

        cursor.execute(sql, (new_value, uid))
        self.connection.commit()


    # Returns the uid of the new record
    def submit_record(self, table_name:str, record:tuple) -> int:
        cursor = self.connection.cursor()

        sql:str = f"INSERT INTO {table_name} VALUES (?, "
        sql += "?, " * len(record)
        sql = sql[:-2] + ')'

        cursor.execute(sql, tuple([None] + list(record)))
        self.connection.commit()

        sql = f"SELECT * FROM {table_name}"
        cursor.execute(sql)

        return max([row[0] for row in cursor.fetchall()])

