# @Version        : 1.0
# @Create Time    : 2021/10/18 22:19
# @File           : validator.py
# @IDE            : PyCharm
# @Desc           : pydantic 模型重用验证器

"""
官方文档：https://pydantic-docs.helpmanual.io/usage/validators/#reuse-validators
"""

import json
import re
import datetime
from bson import ObjectId


def vali_telephone(value: str) -> str:
    """
    手机号验证器
    :param value: 手机号
    :return: 手机号
    """
    if not value or len(value) != 11 or not value.isdigit():
        raise ValueError("请输入正确手机号")

    regex = r"^1(3\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8[0-9]|9[0-9])\d{8}$"

    if not re.match(regex, value):
        raise ValueError("请输入正确手机号")

    return value


def vali_email(value: str) -> str:
    """
    邮箱地址验证器
    :param value: 邮箱
    :return: 邮箱
    """
    if not value:
        raise ValueError("请输入邮箱地址")

    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(regex, value):
        raise ValueError("请输入正确邮箱地址")

    return value


def datetime_str_vali(value: str | datetime.datetime | int | float | dict):
    """
    日期时间字符串验证 日期时间类型转字符串
    如果我传入的是字符串，那么直接返回，如果我传入的是一个日期类型，那么会转为字符串格式后返回
    因为在 pydantic 2.0 中是支持 int 或 float 自动转换类型的，所以我这里添加进去，但是在处理时会使这两种类型报错

    官方文档：https://docs.pydantic.dev/dev-v2/usage/types/datetime/
    """
    if isinstance(value, str):
        pattern = "%Y-%m-%d %H:%M:%S"
        try:
            datetime.datetime.strptime(value, pattern)
            return value
        except ValueError:
            pass
    elif isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(value, dict):
        # 用于处理 mongodb 日期时间数据类型
        date_str = value.get("$date")
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        # 将字符串转换为datetime.datetime类型
        datetime_obj = datetime.datetime.strptime(date_str, date_format)
        # 将datetime.datetime对象转换为指定的字符串格式
        return datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    raise ValueError("无效的日期时间或字符串数据")


def date_str_vali(value: str | datetime.date | int | float):
    """
    日期字符串验证 日期类型转字符串
    如果我传入的是字符串，那么直接返回，如果我传入的是一个日期类型，那么会转为字符串格式后返回
    因为在 pydantic 2.0 中是支持 int 或 float 自动转换类型的，所以我这里添加进去，但是在处理时会使这两种类型报错

    官方文档：https://docs.pydantic.dev/dev-v2/usage/types/datetime/
    """
    if isinstance(value, str):
        pattern = "%Y-%m-%d"
        try:
            datetime.datetime.strptime(value, pattern)
            return value
        except ValueError:
            pass
    elif isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    raise ValueError("无效的日期时间或字符串数据")


def object_id_str_vali(value: str | dict | ObjectId):
    """
    官方文档：https://docs.pydantic.dev/dev-v2/usage/types/datetime/
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        return value.get("$oid")
    elif isinstance(value, ObjectId):
        return str(value)
    raise ValueError("无效的 ObjectId 数据类型")


def dict_str_vali(value: str | dict):
    """
    dict字符串验证 dict类型转字符串
    如果我传入的是字符串，那么直接返回，如果我传入的是一个dict类型，那么会通过json序列化转为字符串格式后返回
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        return json.dumps(value)
    raise ValueError("无效的 Dict 数据或字符串数据")


def str_dict_vali(value: str | dict):
    """
    dict str 验证 字符串 转 dict类型
    """
    if isinstance(value, str):
        return json.loads(value)
    elif isinstance(value, dict):
        return value
    raise ValueError("无效的 Dict 数据或字符串数据")


def str_list_vali(value: str | list):
    """
    list str 验证 字符串 转 list 类型
    """
    if isinstance(value, str):
        return json.loads(value)
    elif isinstance(value, list):
        return value
    raise ValueError("无效的 list 数据或 str 数据")
