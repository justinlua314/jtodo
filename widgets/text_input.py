class TextInput:
    # Returns the new buffer and a bool
    # bool is True if the text input should be submitted
    def handle_input(buffer:str, key:str) -> tuple[str,bool]:
        if key == '\n':
            return (buffer, True)

        if key == '\\':
            return ("", (buffer == ""))

        if key in ("KEY_BACKSPACE", '\b', '\x7f'):
            return (buffer[:-1], False)

        if key.startswith("KEY_"):
            return (buffer, False)

        if key.isprintable():
            return (buffer + key, False)

        return (buffer, False)

