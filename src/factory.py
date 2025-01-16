from applications import (Pwd, Cd, Echo, Ls, Cat, Head, Tail,
                          Grep, Cut, Find, Uniq, Sort, Mkdir,
                          Rmdir, WordCount, Remove, History)
from decorators import unsafe_application


def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]

    return inner


class ApplicationFactory:
    applications_classes = {
        'pwd': singleton(Pwd),
        'cd': Cd,
        'echo': Echo,
        'ls': Ls,
        'cat': Cat,
        'head': Head,
        'tail': Tail,
        'grep': Grep,
        'cut': Cut,
        'find': Find,
        'uniq': Uniq,
        'sort': Sort,
        'mkdir': Mkdir,
        'rmdir': Rmdir,
        'wc': WordCount,
        'rm': Remove,
        'history': History,
    }

    @staticmethod
    def create_application(app_name):
        is_unsafe = app_name.startswith('_')
        if is_unsafe:
            app_name = app_name[1:]

        app_class = ApplicationFactory.applications_classes.get(app_name)
        if app_class:
            app_instance = app_class()
            if is_unsafe:
                app_instance.exec = unsafe_application(app_instance.exec)
            return app_instance
        else:
            raise ValueError(f"Unknown application: {app_name}")
