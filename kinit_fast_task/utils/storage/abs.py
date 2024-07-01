# @Version        : 1.0
# @Create Time    : 2024/7/1
# @File           : abs.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息

from abc import ABC, abstractmethod


class AbstractStorage(ABC):
    """
    数据库操作抽象类
    """

    @abstractmethod
    def upload(self):
        """
        文件上传
        """