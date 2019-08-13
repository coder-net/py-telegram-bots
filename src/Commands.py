class Commands:
    def __init__(self):
        self.commands = {}
        self.system_commands = {}

    def command(self, func):
        self.commands['/' + func.__name__] = func
        return func

    def system_command(self, func):
        self.system_commands[func.__name__] = func

    def find_command(self, command):
        if command in self.commands:
            return self.commands[command]
        return

    def find_system_command(self, command):
        if command in self.system_commands:
            return self.system_commands[command]
        return
