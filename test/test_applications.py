import unittest
import os
# from shell import eval
from collections import deque
from shell import execute_command_line
from src.applications import Find, Mkdir, History, Rmdir, Remove, WordCount
import re
import readline


class TestShell(unittest.TestCase):

    def setUp(self):
        self.out = deque()
        self.find = Find()
        self.mkdir = Mkdir()
        self.history = History()
        self.rmdir = Rmdir()
        self.remove = Remove()
        self.word_count = WordCount()
        # Create test_dir and change to it
        if not os.path.exists("test_dir"):
            os.mkdir("test_dir")
        os.chdir("test_dir")

        # Create dir1 and its files
        os.makedirs('dir1', exist_ok=True)  # Create dir1 within test_dir
        with open('dir1/file1.txt', 'w') as f1:
            f1.write('Content of file1.txt\n')
        with open('dir1/file2.txt', 'w') as f2:
            f2.write('Content of file2.txt\n')
        with open('dir1/file3.txt', 'w') as f3:
            f3.write('aaa\nccc\nbbb\naaa\n')
        with open('dir1/file4.txt', 'w') as f4:
            f4.write('ddd\neee\n')
        # Create more files in dir1 if needed

        # Create dir1 and its files
        os.makedirs('dir2', exist_ok=True)  # Create dir1 within test_dir
        with open('dir2/file.txt', 'w') as f1:
            f1.write('bbb\nAAA\naaa\n')

        # Create additional files directly in test_dir if necessary
        with open("file1.txt", "w") as f1:
            f1.write("abc\nadc\nabc\ndef")
        with open("file2.txt", "w") as f2:
            f2.write("file2\ncontent")

    def tearDown(self):
        # Change back to the original directory and remove test_dir
        os.chdir("..")
        if os.path.exists("test_dir"):
            for root, dirs, files in os.walk("test_dir", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir("test_dir")

    def eval(self, cmdline):
        execute_command_line(cmdline, self.out)
        output = "".join(list(self.out))
        self.out.clear()
        return output

    def test_echo(self):
        cmdline = "echo abc"
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "abc")

    def test_pwd(self):
        cmdline = "pwd"
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, os.getcwd())

    def test_cd(self):
        current_dir = os.getcwd()
        cmdline = (f'cd {current_dir}')
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertNotEqual(result, current_dir)

    def test_ls(self):
        cmdline = "ls"
        stdout = self.eval(cmdline)
        self.assertTrue(len(stdout) > 0)

    def test_cat(self):
        with open('test.txt', 'w') as f:
            f.write('test_content')
        cmdline = "cat test.txt"
        stdout = self.eval(cmdline)
        self.assertEqual(stdout.strip(), 'test_content')
        os.remove('test.txt')  # Cleanup

    def test_head(self):
        with open('test.txt', 'w') as f:
            for i in range(15):
                f.write(f"line{i}\n")
        cmdline = "head -n 5 test.txt"
        stdout = self.eval(cmdline)
        for i in range(5):
            line = stdout.splitlines()[i]
            self.assertEqual(line, f"line{i}")
        os.remove('test.txt')  # Cleanup

    def test_pipe_head(self):
        with open('test.txt', 'w') as f:
            for i in range(15):
                f.write(f"line{i}\n")
        cmdline = "cat test.txt | head -n 3"
        stdout = self.eval(cmdline)
        expected_lines = ["line0", "line1", "line2"]
        actual_lines = stdout.splitlines()
        for i in range(3):
            line = actual_lines[i]
            self.assertEqual(line, expected_lines[i])
        os.remove('test.txt')  # Cleanup

    def test_head_with_input_redirection(self):
        with open('test.txt', 'w') as f:
            for i in range(15):
                f.write(f"line{i}\n")
        cmdline = "head -n 5 < test.txt"
        stdout = self.eval(cmdline)
        expected_lines = ["line0", "line1", "line2", "line3", "line4"]
        actual_lines = stdout.splitlines()
        for i in range(5):
            line = actual_lines[i]
            self.assertEqual(line, expected_lines[i])
        os.remove('test.txt')  # Cleanup

    def test_tail(self):
        with open('test.txt', 'w') as f:
            for i in range(15):
                f.write(f"line{i}\n")
        cmdline = "tail -n 5 test.txt"
        stdout = self.eval(cmdline)
        for i, line in enumerate(stdout.splitlines(), 10):
            self.assertEqual(line, f"line{i}")
        os.remove('test.txt')  # Cleanup

    def test_pipe_tail(self):
        with open('test.txt', 'w') as f:
            for i in range(15):
                f.write(f"line{i}\n")
        cmdline = "cat test.txt | tail -n 5"
        stdout = self.eval(cmdline)
        expected_lines = ["line10", "line11", "line12", "line13", "line14"]
        actual_lines = stdout.splitlines()
        for i in range(5):
            line = actual_lines[i]
            self.assertEqual(line, expected_lines[i])
        os.remove('test.txt')  # Cleanup

    def test_tail_with_input_redirection(self):
        with open('test.txt', 'w') as f:
            for i in range(15):
                f.write(f"line{i}\n")
        cmdline = "tail -n 5 < test.txt"
        stdout = self.eval(cmdline)
        expected_lines = ["line10", "line11", "line12", "line13", "line14"]
        actual_lines = stdout.splitlines()
        for i in range(5):
            line = actual_lines[i]
            self.assertEqual(line, expected_lines[i])
        os.remove('test.txt')  # Cleanup

    def test_grep(self):
        with open('test.txt', 'w') as f:
            f.write('test_content1\n')
            f.write('other_content2\n')
            f.write('test_content3\n')
        cmdline = "grep test test.txt"
        stdout = self.eval(cmdline)
        lines = stdout.splitlines()
        self.assertEqual(lines[0], 'test_content1')
        self.assertEqual(lines[1], 'test_content3')
        os.remove('test.txt')  # Cleanup

    def test_cut(self):
        with open('test_cut.txt', 'w') as f:
            f.write('1234567890')
        cmdline = "cut -b 1-5 test_cut.txt"
        stdout = self.eval(cmdline)
        self.assertEqual(stdout.strip(), '12345')
        os.remove('test_cut.txt')  # Cleanup

    def test_find(self):
        with open('test_find.txt', 'w') as f:
            f.write('dummy content')
        cmdline = "find . -name 'test_find.txt'"
        stdout = self.eval(cmdline)
        self.assertTrue('test_find.txt' in stdout)
        os.remove('test_find.txt')  # Cleanup

    def test_uniq(self):
        with open('test_uniq.txt', 'w') as f:
            f.write('test\n')
            f.write('test\n')
            f.write('demo\n')
        cmdline = "uniq test_uniq.txt"
        stdout = self.eval(cmdline)
        lines = stdout.splitlines()
        self.assertEqual(lines[0], 'test')
        self.assertEqual(lines[1], 'demo')
        os.remove('test_uniq.txt')  # Cleanup

    def test_io_redirection(self):
        cmdline = "echo test > test.txt"
        self.eval(cmdline)
        with open('test.txt', 'r') as f:
            content = f.read()
        self.assertEqual(content, 'test\n')
        os.remove('test.txt')  # Cleanup

    def test_pipe_operator(self):
        with open('test.txt', 'w') as f:
            f.write('test_content1\n')
            f.write('other_content2\n')
            f.write('test_content3\n')
        cmdline = "cat test.txt | grep test"
        stdout = self.eval(cmdline)
        lines = stdout.splitlines()
        self.assertEqual(lines[0], 'test_content1')
        self.assertEqual(lines[1], 'test_content3')
        os.remove('test.txt')  # Cleanup

    def test_cut_stdin(self):
        cmdline = "echo abc | cut -b 1"
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "a")

    def test_cut_union(self):
        cmdline = "echo abc | cut -b -1,2-"
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "abc")

    def test_disabled_doublequotes(self):
        cmdline = "echo '\"\"'"
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, '""')

    def test_doublequotes(self):
        cmdline = 'echo "a  b"'
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "a  b")

    def test_find_dir(self):
        cmdline = "find dir1 -name '*.txt'"
        stdout = self.eval(cmdline)
        result = set(re.split("\n|\t", stdout.strip()))
        self.assertEqual(result, {"dir1/file1.txt", "dir1/file2.txt",
                         "dir1/file3.txt", "dir1/file4.txt"})

    def test_find_pattern(self):
        cmdline = "find -name '*.txt'"
        stdout = self.eval(cmdline)
        result = set(re.split("\n|\t", stdout.strip()))
        self.assertEqual(
            result,
            {
                "./file1.txt",
                "./file2.txt",
                "./dir1/file1.txt",
                "./dir1/file2.txt",
                "./dir1/file3.txt",
                "./dir1/file4.txt",
                "./dir2/file.txt"
            },
        )

    def test_grep_files(self):
        cmdline = "grep '...' dir1/file1.txt dir1/file2.txt"
        stdout = self.eval(cmdline)
        result = stdout.strip().split("\n")
        self.assertEqual(result, ["dir1/file1.txt:Content of file1.txt",
                         "dir1/file2.txt:Content of file2.txt"],)

    def test_grep_re(self):
        cmdline = "grep 'A..' dir1/file1.txt"
        stdout = self.eval(cmdline)
        result = stdout.strip().split("\n")
        self.assertEqual(result, [''])

    def test_grep_stdin(self):
        cmdline = "cat dir1/file1.txt dir1/file2.txt | grep '...'"
        stdout = self.eval(cmdline)
        result = stdout.strip().split("\n")
        self.assertEqual(result, ["Content of file1.txt",
                         "Content of file2.txt"])

    def test_nested_doublequotes(self):
        cmdline = 'echo "a `echo "b"`"'
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "a b")

    def test_pipe_chain_sort_uniq(self):
        cmdline = "cat dir1/file3.txt dir1/file4.txt | sort | uniq"
        stdout = self.eval(cmdline)
        result = stdout.strip().split("\n")
        self.assertEqual(result, ["aaa", "bbb", "ccc", "ddd", "eee"])

    def test_pipe_uniq(self):
        cmdline = (
                   "echo AAA > dir1/file4.txt; cat dir1/file4.txt | uniq -i")
        stdout = self.eval(cmdline)
        result = stdout.strip().split("\n")
        self.assertEqual(result, ["ccc", "ddd", "aaa"])

    def test_quote_keyword(self):
        cmdline = "echo ';'"
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, ";")

    def test_singlequotes(self):
        cmdline = "echo 'a  b'"
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "a  b")

    def test_sort(self):
        with open('test.txt', 'w') as f:
            f.write("line3\nline2\nline1\n")
        cmdline = "sort test.txt"
        stdout = self.eval(cmdline)
        expected_lines = ["line1", "line2", "line3"]
        actual_lines = stdout.splitlines()
        for i in range(3):
            line = actual_lines[i]
            self.assertEqual(line, expected_lines[i])
        os.remove('test.txt')  # Cleanup

    def test_splitting(self):
        cmdline = 'echo a"b"c'
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "abc")

    def test_substitution_doublequotes(self):
        cmdline = 'echo "`echo foo`"'
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "foo")

    def test_substitution_semicolon(self):
        cmdline = "echo `echo foo; echo bar`"
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "foo bar")

    def test_substitution_sort_find(self):
        cmdline = "cat `find dir2 -name '*.txt'` | sort"
        stdout = self.eval(cmdline)
        result = stdout.strip().split("\n")
        self.assertEqual(result, ["AAA", "aaa", "bbb"])

    def test_tail_n0(self):
        cmdline = "tail -n 0 dir1/longfile.txt"
        stdout = self.eval(cmdline)
        result = stdout.strip()
        self.assertEqual(result, "")

    def test_unsafe_ls(self):
        cmdline = "_ls dir3; echo AAA > newfile.txt"
        self.eval(cmdline)
        stdout = self.eval("cat newfile.txt")
        result = stdout.strip()
        self.assertEqual(result, "AAA")

    def test_mkdir(self):
        cmdline = "mkdir test_dir"
        self.eval(cmdline)
        self.assertTrue(os.path.isdir('test_dir'))
        os.rmdir('test_dir')

    def test_rmdir(self):
        cmdline = "mkdir dir3; rmdir dir3"
        self.eval(cmdline)
        self.assertFalse(os.path.exists("dir3"))

    def test_rm(self):
        cmdline = "rm file1.txt file2.txt"
        self.eval(cmdline)
        self.assertFalse(os.path.exists("file1.txt"))
        self.assertFalse(os.path.exists("file2.txt"))

    def test_wc(self):
        cmdline = "wc -l dir1/file3.txt"
        result = self.eval(cmdline).strip()
        expected_output = "4 dir1/file3.txt"
        self.assertEqual(result, expected_output)

    def test_wc_multiple_options(self):
        cmdline = "wc -l -w -c dir1/file3.txt"
        result = self.eval(cmdline).strip()
        expected_output = "4 4 16 dir1/file3.txt"
        self.assertEqual(result, expected_output)

    def test_wc_multiple_files(self):
        cmdline = "wc -l dir1/file3.txt dir2/file.txt"
        result = self.eval(cmdline).strip().split('\n')
        expected_output = ["4 dir1/file3.txt", "3 dir2/file.txt"]
        self.assertEqual(result, expected_output)

    def test_cd_nonexistent_directory(self):
        cmdline = "cd nonexistent_directory"
        with self.assertRaises(FileNotFoundError):
            self.eval(cmdline)

    def test_cd_invalid_format(self):
        cmdline = "cd dir1 dir2"
        with self.assertRaises(ValueError) as context:
            self.eval(cmdline)
        self.assertTrue("Expected format :cd PATH" in str(context.exception))

    def test_cd_permission_error(self):
        cmdline = "cd /root"
        with self.assertRaises(IOError) as context:
            self.eval(cmdline)
        self.assertTrue("Permission Error" in str(context.exception))

    def test_echo_exception(self):
        cmdline = 'echo "raise_exception"'
        with self.assertRaises(Exception) as context:
            self.eval(cmdline)
        self.assertTrue("Echo Error" in str(context.exception))

    def test_tail_missing_argument(self):
        cmdline = "tail -n"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_tail_invalid_argument(self):
        cmdline = "tail -n invalid_argument"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_ls_invalid_format(self):
        cmdline = "ls dir1 dir2"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_ls_permission_error(self):
        cmdline = "ls /root"
        with self.assertRaises(IOError) as context:
            self.eval(cmdline)
        self.assertTrue("Permission Error" in str(context.exception))

    def test_cat_no_files(self):
        cmdline = "cat"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_cat_file_not_found(self):
        cmdline = "cat nonexistent_file.txt"
        with self.assertRaises(FileNotFoundError):
            self.eval(cmdline)

    def test_head_no_input_data(self):
        cmdline = "head"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_head_file_not_found(self):
        cmdline = "head nonexistent_file.txt"
        with self.assertRaises(FileNotFoundError):
            self.eval(cmdline)

    def test_uniq_no_input_data(self):
        cmdline = "uniq"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_uniq_file_not_found(self):
        cmdline = "uniq nonexistent_file.txt"
        with self.assertRaises(FileNotFoundError):
            self.eval(cmdline)

    def test_uniq_io_error(self):
        cmdline = "uniq /root/file.txt"
        with self.assertRaises(IOError):
            self.eval(cmdline)

    def test_sort_reverse(self):
        with open('test.txt', 'w') as f:
            f.write("line1\nline2\nline3\n")
        cmdline = "sort -r test.txt"
        stdout = self.eval(cmdline)
        expected_lines = ["line3", "line2", "line1"]
        actual_lines = stdout.splitlines()
        for i in range(3):
            line = actual_lines[i]
            self.assertEqual(line, expected_lines[i])
        os.remove('test.txt')  # Cleanup

    def test_grep_complex_regex(self):
        with open('test_grep.txt', 'w') as f:
            f.write("apple\nbanana\n123\n")
        cmdline = "grep '[0-9]+' test_grep.txt"
        stdout = self.eval(cmdline)
        self.assertEqual(stdout.strip(), "123")
        os.remove('test_grep.txt')

    def test_find_no_match(self):
        cmdline = "find . -name 'nonexistent*.txt'"
        stdout = self.eval(cmdline)
        self.assertEqual(stdout.strip(), "")

    def test_unexpected_argument(self):
        cmdline = "ls -unexpected"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_cat_multiple_files(self):
        with open('file1.txt', 'w') as f1, open('file2.txt', 'w') as f2:
            f1.write("file1 content\n")
            f2.write("file2 content\n")
        cmdline = "cat file1.txt file2.txt"
        stdout = self.eval(cmdline)
        self.assertEqual(stdout.strip(), "file1 content\nfile2 content")
        os.remove('file1.txt')
        os.remove('file2.txt')

    def test_cat_binary_file(self):
        with open('binary.dat', 'wb') as f:
            f.write(b'\x00\x01\x02')
        cmdline = "cat binary.dat"
        stdout = self.eval(cmdline)
        self.assertEqual(stdout, '\x00\x01\x02')
        os.remove('binary.dat')

    def test_input_redirection_no_file(self):
        cmdline = "cat <"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_large_file_handling(self):
        large_content = "line\n" * 10000  # 10,000 lines
        with open('large_file.txt', 'w') as f:
            f.write(large_content)
        cmdline = "head -n 100 large_file.txt"
        stdout = self.eval(cmdline)
        self.assertTrue(len(stdout.splitlines()) == 100)
        os.remove('large_file.txt')

    def test_handling_symlinks(self):
        os.symlink('file1.txt', 'symlink_to_file1.txt')
        cmdline = "ls symlink_to_file1.txt"
        stdout = self.eval(cmdline)
        self.assertEqual(stdout.strip(), 'symlink_to_file1.txt')
        os.remove('symlink_to_file1.txt')

    def test_head_missing_argument(self):
        cmdline = "head -n"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_head_invalid_argument(self):
        cmdline = "head -n invalid_argument"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_tail_no_input_data(self):
        cmdline = "tail"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_tail_file_not_found(self):
        cmdline = "tail nonexistent_file.txt"
        with self.assertRaises(FileNotFoundError):
            self.eval(cmdline)

    def test_tail_io_error(self):
        cmdline = "tail /root/file.txt"
        with self.assertRaises(IOError):
            self.eval(cmdline)

    def test_grep_file_not_found(self):
        cmdline = "grep pattern nonexistent_file.txt"
        with self.assertRaises(FileNotFoundError):
            self.eval(cmdline)

    def test_grep_io_error(self):
        cmdline = "grep pattern /root/file.txt"
        with self.assertRaises(IOError):
            self.eval(cmdline)

    def test_grep_no_input_data_or_file(self):
        cmdline = "grep pattern"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_history(self):
        readline.add_history("echo hello")
        readline.add_history("ls -l")

        self.history.exec([], self.out, None, None, None)
        self.assertEqual(self.out.popleft(), "1: echo hello\n")
        self.assertEqual(self.out.popleft(), "2: ls -l\n")
        readline.clear_history()

    def test_find_invalid_args(self):
        with self.assertRaises(ValueError):
            self.find.exec([], [], None, None, None)
        with self.assertRaises(ValueError):
            self.find.exec(["-name"], [], None, None, None)
        with self.assertRaises(ValueError):
            self.find.exec(["path", "invalid", "*.txt"], [], None, None, None)
        with self.assertRaises(ValueError):
            self.find.exec(["invalid_path", "-name"
                            "*.txt"], [], None, None, None)
        with self.assertRaises(ValueError):
            self.find.exec([".", "-name", ""], [], None, None, None)

    def test_find_file_not_found(self):
        with self.assertRaises(IOError):
            self.find.exec(["non_existent_directory", "-name",
                            "*.txt"], [], None, None, None)

    def test_find_permission_error(self):
        with self.assertRaises(IOError):
            self.find.exec(["/root", "-name", "*.txt"], [], None, None, None)

    def test_sort_no_input_data(self):
        cmdline = "sort"
        with self.assertRaises(ValueError):
            self.eval(cmdline)

    def test_sort_file_not_found(self):
        cmdline = "sort nonexistent_file.txt"
        with self.assertRaises(FileNotFoundError):
            self.eval(cmdline)

    def test_sort_io_error(self):
        cmdline = "sort /root/file.txt"
        with self.assertRaises(IOError):
            self.eval(cmdline)

    def test_mkdir_no_args(self):
        with self.assertRaises(ValueError) as context:
            self.mkdir.exec([], self.out, None, None, None)
        self.assertTrue("No directory path specified."
                        in str(context.exception))

    def test_mkdir_error(self):
        with self.assertRaises(Exception) as context:
            self.mkdir.exec(["/root/test_dir"], self.out, None, None, None)
        self.assertTrue("Error creating directory" in str(context.exception))

    def test_rmdir_no_args(self):
        with self.assertRaises(ValueError) as context:
            self.rmdir.exec([], self.out, None, None, None)
        self.assertTrue("No directory path specified."
                        in str(context.exception))

    def test_rmdir_error(self):
        with self.assertRaises(Exception) as context:
            self.rmdir.exec(["/root/test_dir"], self.out, None, None, None)
        self.assertTrue("Error removing directory" in str(context.exception))

    def test_remove_no_args(self):
        with self.assertRaises(ValueError) as context:
            self.remove.exec([], self.out, None, None, None)
        self.assertTrue(
            "No arguments provided."
            "Please specify files or"
            "directories to remove."
            in str(context.exception))

    def test_remove_error(self):
        with self.assertRaises(Exception) as context:
            self.remove.exec(["nonexistent_file.txt"],
                             self.out, None, None, None)
        self.assertTrue("Error while removing file" in str(context.exception))

    def test_word_count_no_args(self):
        with self.assertRaises(ValueError):
            self.word_count.exec([], self.out, None, None, None)

    def test_word_count_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            self.word_count.exec(['-l', 'nonexistent_file.txt'],
                                 self.out, None, None, None)

    def test_word_count_file_with_hyphen(self):
        with self.assertRaises(FileNotFoundError):
            self.word_count.exec(['-l', '-nonexistent_file.txt'],
                                 self.out, None, None, None)

    def test_word_count_valid_file(self):
        with open('test_file.txt', 'w') as f:
            f.write('abc\ndef\nghi\n')
        self.word_count.exec(['-l', 'test_file.txt'],
                             self.out, None, None, None)
        self.assertEqual(self.out.popleft(), '3 test_file.txt\n')
        os.remove('test_file.txt')

    def test_word_count_valid_file_no_options(self):
        with open('test_file.txt', 'w') as f:
            f.write('abc\ndef\nghi\n')
        self.word_count.exec(['test_file.txt'], self.out, None, None, None)
        self.assertEqual(self.out.popleft(), '3 3 12 test_file.txt\n')
        os.remove('test_file.txt')

    def test_word_count_error_while_counting(self):
        with self.assertRaises(IOError):
            self.word_count.exec(['-l', '/root/file.txt'],
                                 self.out, None, None, None)


if __name__ == "__main__":

    unittest.main()
