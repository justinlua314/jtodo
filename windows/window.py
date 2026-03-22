# Virtual class for Windows
class Window:
    def __init__(self, app:'TodoApp'):
        self.app:'TodoApp' = app


    def render(self, screen):
        pass


    def handle_input(self, key:str):
        pass

