# @Version        : 1.0
# @Create Time    : 2024/5/27 上午11:29
# @File           : singleton.py
# @IDE            : PyCharm
# @Desc           : 单例模式


import threading


def singleton(cls):
    """
    单例模式函数
    可通过装饰器使用，不支持单例类
    """
    _instance = {}
    lock = threading.Lock()

    def inner(*args, **kwargs):
        with lock:
            if cls not in _instance:
                _instance[cls] = cls(*args, **kwargs)

        return _instance[cls]

    return inner


class Singleton(type):
    """
    单例模式基类
    可通过指定类 metaclass 实现单例模式

    使用例子：

    >>> class DBFactory(metaclass=Singleton):
        ...

    实现类时指定元类为单例类即可实现单例模式
    """

    _instances = {}
    lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        with cls.lock:
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
