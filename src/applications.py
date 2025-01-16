from abc import ABCMeta, abstractmethod
import fnmatch
import os
import re
import readline


class Applications(metaclass=ABCMeta):
    @abstractmethod
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        pass

    def handle_exception(self, e, custom_message):
        raise Exception(f"{custom_message}: {str(e)}")

    def handle_io_exception(self, e, operation, file_name):
        message = f"{operation} failed for file '{file_name}': {str(e)}"
        raise IOError(message)


class Pwd(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        if len(args) == 0:
            output_queue.append(os.getcwd()+'\n')
        else:
            raise ValueError("Expected format: pwd")


class Cd(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        if len(args) != 1:
            raise ValueError("Expected format :cd PATH")
        try:
            os.chdir(args[0])
        except FileNotFoundError as e:
            self.handle_io_exception(e, "Changing directory", args[0])
        except PermissionError as e:
            self.handle_io_exception(e, "Permission Error", args[0])


class Echo(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        try:
            output_queue.append(" ".join(args) + "\n")
        except Exception as e:
            self.handle_exception(e, "Echo Error")


class Ls(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        if len(args) > 1:
            raise ValueError("Expected format: ls or ls [PATH]")
        ls_dir = args[0] if args else os.getcwd()
        try:
            lst_dir = os.listdir(ls_dir)
            for file in lst_dir:
                if not file.startswith("."):
                    output_queue.append(file + "\n")
        except FileNotFoundError as e:
            dir_name = args[0] if args else "current directory"
            self.handle_io_exception(e, "Listing directory contents", dir_name)
        except PermissionError as e:
            dir_name = args[0] if args else "current directory"
            self.handle_io_exception(e, "Permission Error", dir_name)


class Cat(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        file_names = args if args else ([input_redirection]
                                        if input_redirection else [])
        if file_names is None:
            raise ValueError("No files specified for cat command")
        for file_name in file_names:
            try:
                with open(file_name, 'r') as file:
                    output_queue.append(file.read())
            except FileNotFoundError as e:
                self.handle_io_exception(e, "Reading file", file_name)
            except IOError as e:
                self.handle_io_exception(e, "IO Error in file", file_name)


class Head(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        num_lines = 10
        if args and args[0] == "-n":
            try:
                num_lines = int(args[1])
                args = args[2:]
            except IndexError:
                raise ValueError("Missing argument after -n option")
            except ValueError:
                raise ValueError("Invalid argument after -n option")
        self.process_lines(args, num_lines, output_queue,
                           input_data, input_redirection)

    def process_lines(self, args, num_lines, output_queue,
                      input_data, input_redirection):
        try:
            if input_redirection:
                file_name = input_redirection
                with open(file_name) as f:
                    lines = f.readlines()
                    num_lines = min(num_lines, len(lines))
                    for line in lines[:num_lines]:
                        output_queue.append(line)
            elif input_data:
                lines = input_data.splitlines()
                num_lines = min(num_lines, len(lines))
                for line in lines[:num_lines]:
                    line = line + '\n'
                    output_queue.append(line)
            elif args:
                file_name = args[0]
                with open(file_name) as f:
                    lines = f.readlines()
                    num_lines = min(num_lines, len(lines))
                    for line in lines[:num_lines]:
                        output_queue.append(line)
            else:
                raise ValueError("No input data provided for head command")
        except FileNotFoundError as e:
            self.handle_io_exception(e, "Reading file", file_name)
        except IOError as e:
            self.handle_io_exception(e, "IO Error in file", file_name)


class Tail(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        num_lines = 10
        if args and args[0] == "-n":
            try:
                num_lines = int(args[1])
                args = args[2:]
            except IndexError:
                raise ValueError("Missing argument after -n option")
            except ValueError:
                raise ValueError("Invalid argument after -n option")
        self.process_lines(args, num_lines, output_queue,
                           input_data, input_redirection)

    def process_lines(self, args, num_lines, output_queue,
                      input_data, input_redirection):
        try:
            if num_lines == 0:
                return
            elif input_redirection:
                file_name = input_redirection
                with open(file_name) as f:
                    lines = f.readlines()
                    lines = lines[-num_lines:]
                    for line in lines:
                        output_queue.append(line)
            elif input_data:
                lines = input_data.splitlines()
                lines = lines[-num_lines:]
                for line in lines:
                    line = line + '\n'
                    output_queue.append(line)
            elif args:
                file_name = args[0]
                with open(file_name) as f:
                    lines = f.readlines()
                    lines = lines[-num_lines:]
                    for line in lines:
                        output_queue.append(line)
            else:
                raise ValueError("No input data provided for tail command")
        except FileNotFoundError as e:
            self.handle_io_exception(e, "Reading file", file_name)
        except IOError as e:
            self.handle_io_exception(e, "IO Error in File", file_name)


class Grep(Applications):
    def process_file(self, file, pattern, output_queue, is_multiple_files):
        try:
            with open(file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if re.search(pattern, line):
                        output_queue.append(f"{file}:{line}" if
                                            is_multiple_files else line)
        except FileNotFoundError as e:
            self.handle_io_exception(e, "Reading", file)
        except IOError as e:
            self.handle_io_exception(e, "IO Error in file", file)

    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        if len(args) < 1:
            raise ValueError("Expected format: grep PATTERN [FILE]...")

        pattern = args[0]
        files = args[1:] if len(args) > 1 else []
        if os.path.isfile(pattern):
            raise ValueError("Pattern required for first command, not a file")
        if files:
            for file in files:
                self.process_file(file, pattern, output_queue, len(files) > 1)
        elif input_data:
            for line in input_data.splitlines():
                if re.search(pattern, line):
                    line = line + '\n'
                    output_queue.append(line)
        else:
            raise ValueError("No input data or file provided for grep command")


class Cut(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        if not args or args[0] != '-b':
            raise ValueError("Expected '-b' argument in cut command")

        byte_ranges = []
        parts = args[1].split(',')

        for part in parts:
            if part.startswith('-'):
                # Handle negative ranges
                start = 0
                end = int(part[1:])
            elif part.endswith('-'):
                # Handle negative ranges at the end
                start = int(part[:-1]) - 1
                end = len((self.get_input_lines(args,
                                                input_data,
                                                input_redirection))[0])
            elif '-' in part:
                start, end = part.split('-')
                start = int(start) - 1
                end = int(end) if end else None
            else:
                byte = int(part) - 1
                start, end = byte, byte + 1

            # Check for and merge overlapping ranges
            merged = False
            if end is None:
                end = len(self.get_input_lines(args,
                                               input_data, input_redirection))

            for i, (existing_start, existing_end) in enumerate(byte_ranges):
                if (start <= existing_end and end >=
                    existing_start) or (existing_start
                                        <= end and existing_end >= start):
                    start = min(start, existing_start)
                    end = max(end, existing_end)
                    byte_ranges[i] = (start, end)
                    merged = True
                    break

            if not merged:
                byte_ranges.append((start, end))

        input_lines = self.get_input_lines(args, input_data, input_redirection)

        for line in input_lines:
            line_output = self.process_line(line, byte_ranges)
            output_queue.append(line_output + '\n')

    def get_input_lines(self, args, input_data, input_redirection):
        try:
            if input_data:
                input_lines = input_data.splitlines()
            else:
                file_to_read = args[-1] if args else input_redirection
                if file_to_read is None:
                    raise ValueError("No input data provided for Cut command.")
                with open(file_to_read, 'r') as file:
                    input_lines = [line.rstrip('\n') for
                                   line in file.readlines()]
            return input_lines
        except IOError as e:
            self.handle_io_exception(e, "Reading file", file_to_read)

    def process_line(self, line, byte_ranges):
        line_output = ''
        for start, end in byte_ranges:
            if start < len(line):
                if end is None or end > len(line):
                    end = len(line)
                partial_output = line[start:end]
                if partial_output:
                    line_output += partial_output
        return line_output


class Find(Applications):

    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        try:
            if len(args) not in (2, 3):
                raise ValueError("Expected Format:find [PATH] -name [PATTERN]")

            if "-name" not in args:
                raise ValueError("Expected '-name' in the command")

            path = args[0] if len(args) == 3 else "."
            pattern = args[-1]

            if len(args) == 3 and not os.path.isdir(path):
                raise ValueError(f"The specified path '{path}' is not valid.")

            if pattern is None or pattern.strip() == '':
                raise ValueError("A search pattern must be provided.")

            matches = self.find_files(path, pattern)
            for match in matches:
                output_queue.append(match + "\n")

        except FileNotFoundError as e:
            self.handle_io_exception(e, "Finding files in", path)
        except PermissionError as e:
            self.handle_io_exception(e, "Accessing directory", path)

    def find_files(self, root, pattern):
        try:
            matches = []
            for root_dir, _, filenames in os.walk(root):
                for filename in fnmatch.filter(filenames, pattern):
                    full_path = os.path.join(root_dir, filename)
                    relative_path = os.path.relpath(full_path, start=root)
                    if not relative_path.startswith('.'):
                        relative_path = f"{root}/{relative_path}"
                    matches.append(relative_path)
            return matches
        except FileNotFoundError as e:
            self.handle_io_exception(e, "Reading file", filename)


class Uniq(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        try:
            if len(args) > 2:
                raise ValueError("Expected Format: uniq [-i] [FILE]")

            ignore_case = '-i' in args
            file_to_read = None

            if ignore_case:
                args.remove('-i')

            file_to_read = args[0] if args else input_redirection

            last_line = ''
            if file_to_read:
                with open(file_to_read, 'r') as f:
                    for line in f:
                        last_line, output_line = self.process_line(line,
                                                                   last_line,
                                                                   ignore_case)
                        if output_line is not None:
                            output_queue.append(output_line)
            elif input_data:
                for line in input_data.splitlines(True):
                    last_line, output_line = self.process_line(line,
                                                               last_line,
                                                               ignore_case)
                    if output_line is not None:
                        output_queue.append(output_line)

            if not file_to_read and not input_data:
                raise ValueError("No input data provided for Uniq")

        except FileNotFoundError as e:
            self.handle_io_exception(e, "Reading file", file_to_read)
        except IOError as e:
            self.handle_io_exception(e, "IO error in file", file_to_read)

    def process_line(self, line, last_line, ignore_case):
        comparison_line = (line.lower().strip()
                           if ignore_case else line.strip())
        comparison_last_line = (last_line.lower().strip()
                                if ignore_case else last_line.strip())
        if comparison_line != comparison_last_line:
            return line.strip(), line
        return last_line, None


class Sort(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        try:
            reverse_flag = '-r' in args
            file_to_read = args[-1] if args else input_redirection
            if not file_to_read and not input_data:
                raise ValueError("No input data provided for sort command")
            elif input_data:
                lines = sorted(input_data.strip().splitlines(),
                               reverse=reverse_flag)
                lines = [line + '\n' for line in lines]
            else:
                with open(file_to_read, 'r') as f:
                    lines = sorted(f.readlines(), reverse=reverse_flag)

            output_queue.extend(lines)

        except FileNotFoundError as e:
            self.handle_io_exception(e, "Sorting file", file_to_read)
        except IOError as e:
            self.handle_io_exception(e, "IO error in file", file_to_read)


class History(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        # Retrieve and display the history
        history_length = readline.get_current_history_length()
        for i in range(1, history_length + 1):
            command = readline.get_history_item(i)
            output_queue.append(f"{i}: {command}\n")


class Mkdir(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):

        if not args:
            raise ValueError("No directory path specified.")
        try:
            for directory_path in args:
                os.makedirs(directory_path, exist_ok=True)

        except Exception as e:
            self.handle_exception(e, "Error creating directory")


class Rmdir(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):

        if not args:
            raise ValueError("No directory path specified.")
        try:
            for directory_path in args:
                os.rmdir(directory_path)

        except Exception as e:
            self.handle_exception(e, "Error removing directory")


class Remove(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        try:
            if not args:
                raise ValueError("No arguments provided."
                                 "Please specify files or"
                                 "directories to remove.")

            for file_name in args:
                os.remove(file_name)

        except Exception as e:
            self.handle_exception(e, "Error while removing file")


class WordCount(Applications):
    def exec(self, args, output_queue, input_data,
             input_redirection, output_redirection):
        try:
            if not args:
                raise ValueError("No files or options specified."
                                 "Please provide files or options to count.")

            options = []
            files = []

            for arg in args:
                if arg in {'-l', '-w', '-c'}:
                    options.append(arg)
                else:
                    files.append(arg)

            for file_name in files:
                result = self.process_file(file_name, options)
                output_queue.append(result)

        except Exception as e:
            self.handle_exception(e, "Error while counting")

    def process_file(self, file_name, options):
        counts = {'-l': 0, '-w': 0, '-c': 0}

        try:
            if file_name.startswith('-'):
                raise FileNotFoundError(f"No such file or directory:"
                                        f"'{file_name}'")

            with open(file_name, 'r') as file:
                for line in file:
                    counts['-l'] += 1
                    counts['-w'] += len(line.split())
                    counts['-c'] += len(line.encode('utf-8'))

            result = " ".join(f"{counts[option]}" for option in options)
            result += f" {file_name}\n"

            if not options:
                result = (f"{counts['-l']} {counts['-w']} "
                          f"{counts['-c']} {file_name}\n")

            return result

        except Exception as file_exception:
            self.handle_io_exception(file_exception, "Counting", file_name)
