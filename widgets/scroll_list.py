from lib.helpers import Helpers


class ScrollList:
    def render_list(
        screen, header_space:int, footer_space:int,
        options:list[str], selected:int, x_align:int=0,
        line_separated:bool=False
    ):
        height:int
        width:int
        height, width = screen.getmaxyx()

        top:int = header_space

        bottom:int = height - footer_space - 1
        visible_height:int = bottom - top + 1

        start:int = selected - visible_height // 2

        start = max(start, 0)

        if start + visible_height > len(options):
            start = max(len(options) - visible_height, 0)

        end:int = start + visible_height
        visible:list[str] = options[start:end]

        y:int = top
        lines:list[str] = []
        actual_index:int = start

        for index, opt in enumerate(visible):
            lines = opt.split('\n')

            for line_index, line in enumerate(lines):
                line = Helpers.limit_text(line, (width - 3))

                if actual_index == selected and line_index == 0:
                    screen.addstr(y, x_align, f"> {line}")
                else:
                    screen.addstr(y, x_align, f"  {line}")

                y += 1

            actual_index += 1

            if line_separated:
                y += 1

