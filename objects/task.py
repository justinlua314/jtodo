import datetime as dt


class Task:
    def __init__(self, name:str):
        self.name:str = name
        self.uid:int = -1

        self.parent_uid:int = -1
        self.is_subtask:bool = False

        self.date:dt.datetime = dt.datetime.now()
        self.status:int = 0
        self.priority:int = 0

        self.description:str = ""

        self.comments:list['Comment'] = []


    def status_string(self) -> str:
        match(self.status):
            case 0: return "Open"
            case 1: return "In Progress"
            case 2: return "Closed"


    def priority_string(self) -> str:
        match(self.priority):
            case 0: return "Low"
            case 1: return "Medium"
            case 2: return "High"
            case 3: return "Urgent"


    def change_status(self, status:int, service:'TaskService'):
        service.set_task_status(self.uid, status)
        self.status = status


    def change_priority(self, priority:int, service:'TaskService'):
        service.set_task_priority(self.uid, priority)
        self.priority = priority


    def post_comment(self, body:str, service:'TaskService'):
        service.create_comment(body, self.uid)
        self.comments = service.get_comments(self.uid)

