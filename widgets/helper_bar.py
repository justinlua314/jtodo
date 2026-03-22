class HelperBar:
    def render_options(screen, options:dict[str,str]):
        height:int = screen.getmaxyx()[0]
        line:int = height - len(options)

        for key, opt in options.items():
            screen.addstr(line, 0, f"{key} : {opt}")
            line += 1


    def render_input(screen, prompt:str, buffer:str):
        height:int
        width:int
        height, width = screen.getmaxyx()

        full_string = f"{prompt}: {buffer}"

        if len(full_string) >= width - 1:
            full_string = full_string[-(width-2):]

        screen.addstr(height - 1, 0, full_string)
        screen.move(height - 1, len(full_string))


    def render_confirm(screen, prompt:str):
        height:int = screen.getmaxyx()[0]
        screen.addstr(height - 1, 0, prompt)

