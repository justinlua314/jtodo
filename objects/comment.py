import datetime as dt


class Comment:
    def __init__(self, body:str):
        self.date:dt.datetime = dt.datetime.now()
        self.body:str = body
        self.uid:int = -1
        self.task_uid:int = -1

