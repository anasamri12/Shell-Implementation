class Observer:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def update(self, subject):
        pass


class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self):
        for observer in self._observers:
            observer.update(self)


class CommandLogger(Observer):
    def update(self, subject):
        if self.verbose:
            pass
        if subject.error:
            print(f"Error: {subject.error}")
