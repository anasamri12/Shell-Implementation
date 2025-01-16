import unittest
from unittest.mock import Mock
from shell import CommandLogger
from observer import Observer, Subject


class TestObserverPattern(unittest.TestCase):
    def test_observer_initialization(self):
        observer = Observer(verbose=True)
        self.assertTrue(observer.verbose)

    def test_subject_initialization(self):
        subject = Subject()
        self.assertEqual(len(subject._observers), 0)

    def test_attach_detach_observer(self):
        subject = Subject()
        observer = Observer()
        subject.attach(observer)
        self.assertIn(observer, subject._observers)
        subject.detach(observer)
        self.assertNotIn(observer, subject._observers)

    def test_detach_nonexistent_observer(self):
        subject = Subject()
        observer = Observer()
        # Should not raise an exception
        subject.detach(observer)

    def test_notify_observers(self):
        subject = Subject()
        observer1 = Mock(spec=Observer)
        observer2 = Mock(spec=Observer)
        subject.attach(observer1)
        subject.attach(observer2)
        subject.notify()
        observer1.update.assert_called_once_with(subject)
        observer2.update.assert_called_once_with(subject)

    def test_command_logger_update(self):
        subject = Subject()
        command_logger = CommandLogger(verbose=True)
        subject.attach(command_logger)
        subject.error = "Sample Error"
        with self.assertLogs(level='INFO') as log:
            subject.notify()
            self.assertIn("Error: Sample Error", log.output)


if __name__ == '__main__':
    unittest.main()
