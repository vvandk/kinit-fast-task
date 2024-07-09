# @Version        : 1.0
# @Create Time    : 2024/3/28 16:00
# @File           : base.py
# @IDE            : PyCharm
# @Desc           : 描述信息

from typing import Any
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field


def add_schema_extra(schema: dict[str, Any]) -> None:
    """
    自定义 JSON Schema 的输出，主要功能包括在自动生成的接口文档中添加示例数据、隐藏特定字段等操作

    在接口文档中默认不展示 hidden=True 的字段

    并不会影响序列化操作

    :param schema: 该参数是一个字典，表示生成的JSON Schema。你可以通过修改这个字典来定制最终生成的JSON Schema。例如，可以从中删除或修改字段属性，添加自定义属性等。
    :return:
    """  # noqa E501
    if "properties" in schema:
        # 收集需要删除的键
        keys_to_delete = [key for key, value in schema["properties"].items() if value.get("hidden") is True]

        # 删除包含 hidden=True 的项
        for key in keys_to_delete:
            del schema["properties"][key]


class BaseSchema(BaseModel):
    """
    from_attributes：允许将非字典格式的数据（例如，具有属性的对象）转化为 Pydantic 模型实例，例如：ORM Model
    """  # noqa E501

    model_config = ConfigDict(from_attributes=True, json_schema_extra=add_schema_extra)

    def serializable_dict(self, **kwargs) -> dict:
        """
        返回一个仅包含可序列化字段的字典
        :param kwargs:
        :return: 返回 JSON 可序列化的字典
        """
        default_dict = self.model_dump()
        return jsonable_encoder(default_dict)


class DeleteSchema(BaseSchema):
    data_ids: list[int] = Field(..., description="需要删除的数据编号列表")
