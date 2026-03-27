class TextBox:
    def render_box(
        screen, y:int, x:int, h:int, w:int, scroll:int, text:str
    ):
        if text == "":
            return

        words:list[str] = text.split(' ')
        newline:bool = True
        scope_y:int = 0

        for word in words:
            if y >= h:
                break

            if len(word) + x > w and not newline:
                if scope_y >= scroll:
                    y += 1

                scope_y += 1
                x = 0
                newline = True

                if y >= h:
                    break

            if scope_y >= scroll:
                screen.addstr(y, x, word)

            x += len(word)
            newline = False

            if x + 2 >= w:
                if scope_y >= scroll:
                    y += 1

                scope_y += 1
                x = 0
                newline = True
            else:
                if scope_y >= scroll:
                    screen.addch(y, x, ' ')

                x += 1

