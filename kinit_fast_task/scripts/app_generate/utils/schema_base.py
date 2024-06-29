# @Version        : 1.0
# @Create Time    : 2024/6/14 下午5:12
# @File           : json_config_schema.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息
from typing import Any
from pydantic import BaseModel, Field


class ModelFieldSchema(BaseModel):
    name: str = Field(..., description="字段名称")
    field_type: str = Field(..., description="字段类型(SQLAlchemy 类型)")
    field_python_type: str = Field(..., description="字段类型(Python 类型)")
    field_kwargs: dict = Field(..., description="字段属性")
    nullable: bool = Field(False, description="是否可以为空")
    default: Any = Field(None, description="默认值")
    comment: str | None = Field(None, description="字段描述")
