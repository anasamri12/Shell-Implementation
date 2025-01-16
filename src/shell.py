from collections import deque
from factory import ApplicationFactory
from observer import Subject, CommandLogger
from glob import glob
import sys
import os
import re
import readline
from applications import History


class CommandExecutor(Subject):
    def __init__(self):
        super().__init__()
        self.command = None
        self.error = None

    def execute_and_notify(self, command_line):
        self.command = command_line
        output_queue = deque()
        try:
            execute_command_line(command_line, output_queue)
            self.error = None
            while output_queue:
                print(output_queue.popleft(), end="")
        except ValueError as e:
            self.error = f"Syntax error: {e}"
        except FileNotFoundError as e:
            self.error = f"File not found: {e}"
        finally:
            self.notify()


def save_history(history_path):
    readline.write_history_file(history_path)


def load_history(history_path):
    if os.path.exists(history_path):
        readline.read_history_file(history_path)


def process_command(tokens, output_queue, input_data,
                    input_redirection, output_redirection):
    try:
        app = tokens[0]
        args = tokens[1:]

        app_instance = ApplicationFactory.create_application(app)
        if app_instance is None:
            raise ValueError(f"Command not found: {app}")
        app_instance.exec(args, output_queue, input_data,
                          input_redirection, output_redirection)

        if output_redirection:
            try:
                with open(output_redirection, 'w') as file:
                    while output_queue:
                        file.write(output_queue.popleft())
            except IOError as e:
                print(f"Error writing to file '{output_redirection}': {e}")
    except ValueError as e:
        print(f"Error processing command '{app}': {e}")


def execute_command_line(command_line, output_queue, input_data=None):
    if '|' in command_line:
        piped_commands = command_line.split('|')
        execute_piped_commands(piped_commands, output_queue)
    elif '`' in command_line:
        execute_command_substitution(command_line, output_queue)
    else:
        raw_commands = split_command_line(command_line)
        input_file = None

        for command in raw_commands:
            execute_single_command(command, output_queue,
                                   input_data, input_file)


def execute_piped_commands(piped_commands, output_queue):

    output = None
    for command in piped_commands:
        sub_queue = deque()
        execute_command_line(command.strip(), sub_queue, input_data=output)
        output = ''.join(sub_queue)
    if output:
        output_queue.extend(output.splitlines(True))


def split_command_line(command_line):
    x = re.findall(r"(?:[^;\"']|\"[^\"]*\"|'[^']*')+", command_line)
    return x


def execute_command_substitution(command, output_queue):
    # Use regular expression to find commands inside backticks
    matches = re.findall("`([^`]+)`", command)

    for match in matches:
        sub_output = run_subcommand(match, output_queue)
        command = command.replace(f"`{match}`", sub_output.strip())
        execute_command_line(command, output_queue, input_data=None)


def run_subcommand(subcommand, sub_queue):
    sub_queue = deque()
    raw_commands = split_command_line(subcommand)
    for command in raw_commands:
        execute_single_command(command, sub_queue,
                               input_data=None, input_file=None)
    return ''.join(sub_queue)


def execute_single_command(command, output_queue, input_data, input_file):

    command, input_redirection, output_redirection = parse_command(command)
    tokens = split_into_tokens(command)
    process_command(tokens, output_queue, input_data,
                    input_redirection, output_redirection)


def split_into_tokens(command):

    tokens = []
    for match in re.finditer(r"[^\s\"']+|\"([^\"]*)\"|'([^']*)'", command):
        if match.group(1) or match.group(2):
            tokens.append(match.group(1) or match.group(2))
        else:
            tokens.extend(glob(match.group(0)) or [match.group(0)])
    return tokens


def parse_command(command):
    parts = command.split()
    input_redirection = output_redirection = None

    if len(parts) >= 3 and parts[0] == '<':
        input_redirection = parts[1]
        command = ' '.join(parts[2:])
    else:
        split_parts = [part.strip() for part in re.split('(<|>)', command)]
        if len(split_parts) > 1:
            command = split_parts[0]
            for i in range(1, len(split_parts), 2):
                symbol, file = split_parts[i], split_parts[i + 1]
                if symbol == "<":
                    if input_redirection is not None:
                        raise ValueError("More than one input redirection")
                    input_redirection = file.strip()
                elif symbol == ">":
                    if output_redirection is not None:
                        raise ValueError("More than one output redirection")
                    output_redirection = file.strip()
    if input_redirection and not os.path.exists(input_redirection):
        raise FileNotFoundError(f"Input file '{input_redirection}' not found")
    return command.strip(), input_redirection, output_redirection


def main():
    history_file = os.path.join(os.path.expanduser("~"), ".myshell_history")
    load_history(history_file)

    output_queue = deque()

    if len(sys.argv) > 1:
        if len(sys.argv) != 3 or sys.argv[1] != "-c":
            raise ValueError("Invalid command line arguments")
        execute_command_line(sys.argv[2], output_queue)
        while output_queue:
            print(output_queue.popleft(), end="")
    else:
        command_executor = CommandExecutor()
        logger = CommandLogger()
        command_executor.attach(logger)

        try:
            while True:
                print(os.getcwd() + "> ", end="")
                cmdline = input()
                if cmdline.strip() == "exit":
                    break
                elif cmdline.strip() == "history":
                    history_app = History()
                    history_app.exec([], output_queue, None, None, None)

                try:
                    command_executor.execute_and_notify(cmdline)
                except ValueError as e:
                    print(f"Error: {e}")
        finally:
            save_history(history_file)


if __name__ == "__main__":
    main()
