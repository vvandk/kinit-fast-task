# @Version        : 1.0
# @Create Time    : 2024/6/7 下午1:45
# @File           : model_to_json.py
# @IDE            : PyCharm
# @Desc           : model to json
import inspect
from pathlib import Path

from sqlalchemy import inspect as sa_inspect, Column
from sqlalchemy.sql.schema import ScalarElementColumnDefault

from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.scripts.app_generate.utils import json_config_schema_1_0
from kinit_fast_task.scripts.app_generate.utils import json_config_schema
from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase


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

    def parse_model_fields(self) -> list[json_config_schema.ModelFieldSchema]:
        """
        解析模型字段

        :return:
        """
        fields = []
        mapper = sa_inspect(self.model)
        for column in mapper.columns:
            assert isinstance(column, Column)
            default = column.default
            if default is not None:
                assert isinstance(default, ScalarElementColumnDefault)
                default = default.arg
            field_type = type(column.type).__name__
            params = column.type.__dict__
            if field_type == "String":
                keys = ['length']
            elif field_type == "DECIMAL":
                keys = ['precision', "scale"]
            else:
                keys = []
            field_kwargs = {key: params[key] for key in keys}
            item = json_config_schema.ModelFieldSchema(
                name=column.name,
                field_type=field_type,
                field_kwargs=field_kwargs,
                nullable=column.nullable,
                default=default,
                comment=column.comment
            )
            fields.append(item)
        return fields

    def to_json_1_0(self) -> dict:
        """
        转为 1.0 JSON 配置文件

        :return:
        """
        fields = self.parse_model_fields()
        json_config = json_config_schema_1_0.JSONConfigSchema(
            **{
                "version": "1.0",
                "app_name": self.app_name,
                "app_desc": self.app_desc,
                "model": {
                    "filename": Path(inspect.getfile(self.model)).name,
                    "class_name": self.model.__name__,
                    "table_args": self.model.__table_args__,
                    "fields": fields
                },
                "schemas": {
                    "filename": f"{self.app_name}_schema.py",
                    "base": f"{GenerateBase.snake_to_camel(self.app_name)}Schema",
                    "create": f"{GenerateBase.snake_to_camel(self.app_name)}CreateSchema",
                    "update": f"{GenerateBase.snake_to_camel(self.app_name)}UpdateSchema",
                    "simple_out": f"{GenerateBase.snake_to_camel(self.app_name)}SimpleOutSchema"
                },
                "crud": {
                    "filename": f"{self.app_name}_crud.py",
                    "class_name": f"{GenerateBase.snake_to_camel(self.app_name)}CRUD",
                },
                "routers": ["create", "update", "delete", "list_query", "one_query"]
            }
        )
        return json_config.model_dump()
