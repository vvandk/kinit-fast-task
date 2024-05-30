# @Version        : 1.0
# @Create Time    : 2023/7/16 12:42
# @File           : types.py
# @IDE            : PyCharm
# @Desc           : 自定义数据类型

"""
自定义数据类型 - 官方文档：https://docs.pydantic.dev/dev/concepts/types/#adding-validation-and-serialization
"""

from typing import Annotated, Any
from pydantic import AfterValidator, PlainSerializer, WithJsonSchema
from kinit_fast_task.utils.validator import (
    vali_email,
    vali_telephone,
    date_str_vali,
    datetime_str_vali,
    object_id_str_vali,
    dict_str_vali,
)
import datetime


# -----------------------------------------------
# 实现自定义一个日期时间字符串的数据类型
# 输入类型：str | datetime.datetime | int | float | dict
# 输出类型：str
# -----------------------------------------------
DatetimeStr = Annotated[
    str | datetime.datetime | int | float | dict,
    AfterValidator(datetime_str_vali),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]


# -----------------------------------------------
# 实现自定义一个手机号验证类型
# 输入类型：str
# 输出类型：str
# -----------------------------------------------
Telephone = Annotated[
    str,
    AfterValidator(lambda x: vali_telephone(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]


# -----------------------------------------------
# 实现自定义一个邮箱验证类型
# 输入类型：str
# 输出类型：str
# -----------------------------------------------
Email = Annotated[
    str,
    AfterValidator(lambda x: vali_email(x)),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]


# -----------------------------------------------
# 实现自定义一个日期字符串的数据类型
# 输入类型：str | datetime.date | int | float
# 输出类型：str
# -----------------------------------------------
DateStr = Annotated[
    str | datetime.date | int | float,
    AfterValidator(date_str_vali),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]


# -----------------------------------------------
# 实现自定义一个ObjectId字符串的数据类型
# 输入类型：str | dict | ObjectId
# 输出类型：str
# -----------------------------------------------
ObjectIdStr = Annotated[
    Any,
    AfterValidator(object_id_str_vali),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]


# -----------------------------------------------
# 实现自定义一个字典字符串的数据类型
# 输入类型：str | dict
# 输出类型：str
# -----------------------------------------------
DictStr = Annotated[
    str | dict,
    AfterValidator(dict_str_vali),
    PlainSerializer(lambda x: x, return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
]
