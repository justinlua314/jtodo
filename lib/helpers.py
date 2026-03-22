import datetime as dt


class Helpers:
    def limit_text(text:str, limit:int) -> str:
        if len(text) >= limit:
            return text[:(limit - 3)] + "..."

        return text


    def wrap_text(text:str, limit:int) -> str:
        if text == "":
            return text

        render:str = ""
        words:list[str] = text.split(' ')
        newline:bool = True
        x:int = 0

        for word in words:
            if len(word) + x > limit and not newline:
                render += '\n'
                x = 0
                newline = True

            while len(word) > limit:
                render += word[:(limit - 1)] + '\n'
                word = word[limit:]

            render += word
            x += len(word)
            newline = False

            if x + 2 >= limit:
                render += '\n'
                x = 0
                newline = True
            else:
                render += ' '
                x += 1

        return render


    def date_to_string(date:dt.datetime) -> str:
        return dt.datetime.strftime(date, "%m-%d-%Y %H:%M %p")


    def string_to_date(date:str) -> dt.datetime:
        return dt.datetime.strptime(date, "%m-%d-%Y %H:%M %p")

