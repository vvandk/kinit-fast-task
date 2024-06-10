# @Version        : 1.0
# @Create Time    : 2024/6/7 下午1:45
# @File           : model_to_json.py
# @IDE            : PyCharm
# @Desc           : model to json
import inspect
from pathlib import Path

from alembic.ddl.base import ColumnType
from sqlalchemy import inspect as sa_inspect, Column
from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.scripts.app_generate.utils import json_config_1_0


class ModelToJson:

    def __init__(self, model: type(AbstractORMModel), app_name: str, app_desc: str):
        """
        基于单个 model 输出 JSON 配置文件

        :param model: Model 类
        :param app_name: app 名称, 示例：auth_user
        :param app_desc: app 描述, 示例：AuthUserModel
        """
        self.model = model
        self.app_name = app_name
        self.app_desc = app_desc

    def to_json_1_0(self) -> dict:
        """
        转为 1.0 JSON 配置文件

        :return:
        """
        fields = []
        mapper = sa_inspect(self.model)
        for column in mapper.columns:
            assert isinstance(column, Column)
            print(column)
            print(column.__dict__)
            print(type(column))
            print(column.name)
            print(column.type, column.type.python_type, type(column.type))
            print(column.nullable)
            print(column.default)
            print(column.comment)
        # for attr_name, column_property in mapper.column_attrs.items():
        #     # 假设它是单列属性
        #     column: ColumnType = column_property.columns[0]
        #     print(column)
        #     print(type(column))
        #     print(attr_name)
        #     print(column_property)
        #     item = json_config_1_0.ModelFieldSchema(
        #         name=attr_name,
        #         field_type=column.type,
        #         nullable=column.nullable,
        #         default=column.default.__dict__.get("arg", None) if column.default else None,
        #         title=column.comment,
        #         max_length=column.type.__dict__.get("length", None),
        #     )
        #     fields.append(item)
        #     print(item)
        # json_config = {
        #     "version": "1.0",
        #     "app_name": self.app_name,
        #     "app_desc": self.app_desc,
        #     "model": {
        #         "filename": Path(inspect.getfile(self.model)).name,
        #         "class_name": self.model.__class__.__name__,
        #         "table_args": self.model.__table_args__,
        #     }
        # }
        return {}

