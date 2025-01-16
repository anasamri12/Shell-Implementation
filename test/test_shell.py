import unittest
from unittest.mock import patch, mock_open
from collections import deque
from src.shell import execute_command_line, CommandExecutor, main


class TestShell(unittest.TestCase):

    def setUp(self):
        self.output_queue = deque()

    def eval(self, cmdline):
        execute_command_line(cmdline, self.output_queue)
        output = "".join(list(self.output_queue))
        self.output_queue.clear()
        return output

    def test_execute_command_line(self):
        stdout = self.eval('echo "Hello, World!"')
        self.assertEqual(stdout, 'Hello, World!\n')

    def test_execute_piped_commands(self):
        stdout = self.eval('echo "Hello, World!" | grep "World"')
        self.assertEqual(stdout, 'Hello, World!\n')

    def test_execute_command_substitution(self):
        stdout = self.eval('echo `echo "Hello, World!"`')
        self.assertEqual(stdout, 'Hello, World!\n')

    @patch('builtins.open', new_callable=mock_open,
           read_data='Hello, World!\n')
    def test_input_redirection(self, mock_file):
        stdout = self.eval('cat < test.txt')
        self.assertEqual(stdout, 'Hello, World!\n')

    @patch('builtins.open', new_callable=mock_open)
    def test_output_redirection(self, mock_file):
        self.eval('echo "Hello, World!" > test.txt')
        mock_file().write.assert_called_once_with('Hello, World!\n')

    def test_command_executor(self):
        executor = CommandExecutor()
        with patch('src.shell.execute_command_line') as mock_execute:
            executor.execute_and_notify('echo "Hello, World!"')
            mock_execute.assert_called_once_with('echo "Hello, World!"',
                                                 executor.output_queue)

    def test_multiple_input_redirection(self):
        with self.assertRaises(ValueError):
            self.eval('< input1.txt < input2.txt')

    def test_multiple_output_redirection(self):
        with self.assertRaises(ValueError):
            self.eval('> output1.txt > output2.txt')

    def test_invalid_command(self):
        with self.assertRaises(ValueError):
            self.eval('invalid_command')

    def test_empty_command(self):
        stdout = self.eval('')
        self.assertEqual(stdout, '')

    def test_piped_commands_with_no_output(self):
        stdout = self.eval('echo "Hello, World!" | grep "Universe"')
        self.assertEqual(stdout, '')

    def test_command_substitution_with_multiple_commands(self):
        stdout = self.eval('echo `echo "Hello,"; echo " World!"`')
        self.assertEqual(stdout, 'Hello, World!\n')

    def test_input_redirection_with_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            self.eval('cat < nonexistent.txt')

    def test_output_redirection_with_protected_file(self):
        with self.assertRaises(PermissionError):
            self.eval('echo "Hello, World!" > /root/protected.txt')

    def test_command_line_with_multiple_semicolons(self):
        stdout = self.eval('echo "Hello,"; echo " World!";')
        self.assertEqual(stdout, 'Hello,\n World!\n')

    def test_command_line_with_unmatched_quote(self):
        with self.assertRaises(ValueError):
            self.eval('echo "Hello, World!')

    def test_execute_invalid_command(self):
        with self.assertRaises(ValueError):
            self.eval('invalid_command')

    def test_execute_command_with_syntax_error(self):
        with self.assertRaises(ValueError):
            self.eval('echo "Hello, World!')

    def test_execute_command_with_file_not_found_error(self):
        with self.assertRaises(FileNotFoundError):
            self.eval('cat nonexistent.txt')

    def test_execute_command_line_with_value_error(self):
        with self.assertRaises(ValueError):
            self.eval('invalid_command')

    def test_execute_command_line_with_output_redirection_error(self):
        with patch('builtins.open',
                   side_effect=IOError('Error writing to file')):
            with self.assertRaises(IOError):
                self.eval('echo "Hello, World!" > nonexistent.txt')

    def test_execute_command_line_with_unknown_command(self):
        with self.assertRaises(ValueError):
            self.eval('unknown_command')

    def test_load_history_with_existing_history_file(self):
        with patch('os.path.exists', return_value=True):
            with patch('readline.read_history_file') as mock_read_history:
                main()
                mock_read_history.assert_called_once()

    def test_command_executor_with_value_error(self):
        executor = CommandExecutor()
        with patch('src.shell.execute_command_line',
                   side_effect=ValueError('Syntax error')):
            with self.assertRaises(ValueError):
                executor.execute_and_notify('invalid_command')

    def test_command_executor_with_file_not_found_error(self):
        executor = CommandExecutor()
        with patch('src.shell.execute_command_line',
                   side_effect=FileNotFoundError('File not found')):
            with self.assertRaises(FileNotFoundError):
                executor.execute_and_notify('cat nonexistent.txt')

    def test_execute_and_notify_with_unknown_command(self):
        executor = CommandExecutor()
        with self.assertRaises(ValueError) as context:
            executor.execute_and_notify('unknown_command')
        self.assertTrue('Command not found: unknown_command'
                        in str(context.exception))

    def test_execute_and_notify_with_history_command(self):
        executor = CommandExecutor()
        with patch('src.shell.History') as mock_history:
            mock_history_instance = mock_history.return_value
            executor.execute_and_notify('history')
            mock_history_instance.exec.assert_called_once_with(
                [], executor.output_queue, None, None, None)

    def test_execute_and_notify_with_value_error(self):
        executor = CommandExecutor()
        with patch('src.shell.execute_command_line',
                   side_effect=ValueError('Syntax error')):
            with self.assertRaises(ValueError) as context:
                executor.execute_and_notify('invalid_command')
            self.assertTrue('Error: Syntax error' in str(context.exception))

    def test_execute_and_notify_prints_output(self):
        executor = CommandExecutor()
        with patch('src.shell.print') as mock_print:
            executor.execute_and_notify('echo "Hello, World!"')
            mock_print.assert_called_once_with('Hello, World!\n', end='')

    def test_main_loop_with_exit_command(self):
        with patch('src.shell.input', return_value='exit'):
            with patch('src.shell.CommandExecutor') as mock_executor:
                main()
                mock_executor.return_value.execute_and_notify\
                    .assert_not_called()

    def test_main_loop_with_history_command(self):
        with patch('src.shell.input', side_effect=['history', 'exit']):
            with patch('src.shell.History') as mock_history:
                main()
                mock_history.return_value.exec.assert_called_once_with(
                    [], None, None, None, None)

    def test_main_loop_with_value_error(self):
        with patch('src.shell.input', side_effect=['invalid_command', 'exit']):
            with patch('src.shell.print') as mock_print:
                main()
                mock_print.assert_called_with('Error: Syntax error')

    @patch('src.shell.input', return_value='exit')
    @patch('src.shell.sys.argv', ['shell.py'])
    def test_main_without_arguments(self, mock_input):
        with patch('src.shell.print') as mock_print:
            main()
            mock_print.assert_called()

    @patch('src.shell.sys.argv', ['shell.py', '-c', 'echo "Hello, World!"'])
    def test_main_with_arguments(self):
        with patch('src.shell.print') as mock_print:
            main()
            mock_print.assert_called_with('Hello, World!\n', end='')

    @patch('src.shell.sys.argv', ['shell.py', '-c'])
    def test_main_with_invalid_arguments(self):
        with self.assertRaises(ValueError):
            main()


if __name__ == '__main__':
    unittest.main()
