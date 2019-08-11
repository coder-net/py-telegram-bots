class Commands:
    def __init__(self, unknown):
        self.commands = {}
        self.unknown = unknown  # for handling don't existing command

    def command(self, func):
        self.commands['/' + func.__name__] = func
        return func

    def find_command(self, command):
        if command in self.commands:
            return self.commands[command]
        return self.unknown
