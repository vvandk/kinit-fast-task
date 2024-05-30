# @Version        : 1.0
# @Create Time    : 2023/02/12 22:18
# @File           : enum.py
# @IDE            : PyCharm
# @Desc           : 增加枚举类方法

from enum import Enum


class SuperEnum(Enum):
    @classmethod
    def to_dict(cls):
        """
        返回枚举的字典表示形式
        :return:
        """
        return {e.name: e.value for e in cls}

    @classmethod
    def keys(cls):
        """
        返回所有枚举键的列表
        :return:
        """
        return cls._member_names_

    @classmethod
    def values(cls):
        """
        返回所有枚举值的列表
        :return:
        """
        return list(cls._value2member_map_.keys())
