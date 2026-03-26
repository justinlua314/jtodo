from lib.helpers import Helpers


class HelperBar:
    def render_options(screen, options:dict[str,str]):
        height:int = screen.getmaxyx()[0]
        line:int = height - len(options)

        for key, opt in options.items():
            screen.addstr(line, 0, f"{key} : {opt}")
            line += 1


    # {column_header : {option_key : option_meaning}}
    def render_multicolumn_options(
        screen, options:dict[str,dict[str,str]]
    ):
        height:int = screen.getmaxyx()[0]

        # Get which column has the most options
        largest_column:int = max(len(col) for col in options.values())
        y:int = height - largest_column - 2

        # Get the width of each column
        column_sizes:list[int] = []
        col_width:int
        opt_render:str

        for col in options.values():
            col_width = 0

            for opt_key, opt_meaning in col.items():
                opt_render = f"{opt_key} : {opt_meaning}"
                col_width = max(col_width, len(opt_render))

            column_sizes.append(col_width + 1)

        index:int = 0
        x:int = 0
        text:str

        while index <= largest_column + 1:
            if index == 0:
                for col_index, header in enumerate(options):
                    col_width = column_sizes[col_index]
                    text = Helpers.add_tail_space(header, col_width)
                    screen.addstr(y, x, text)
                    x += col_width
            else:
                for col_index, column in enumerate(options.values()):
                    col_width = column_sizes[col_index]

                    if index - 1 >= len(column):
                        x += col_width
                        continue

                    opt_key = list(column)[index - 1]
                    opt_meaning = column[opt_key]

                    text = Helpers.add_tail_space(
                        f"{opt_key} : {opt_meaning}", col_width
                    )

                    screen.addstr(y, x, text)
                    x += col_width

            x = 0
            y += 1
            index += 1


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

