# @Version        : 1.0
# @Create Time    : 2024/6/7
# @File           : model_to_json.py
# @IDE            : PyCharm
# @Desc           : model to json

import inspect
from pathlib import Path
from kinit_fast_task.scripts.app_generate.v1 import json_config_schema
from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase
from kinit_fast_task.scripts.app_generate.utils.model_to_json_base import ModelToJsonBase


class ModelToJson(ModelToJsonBase):
    def to_json(self) -> dict:
        """
        转为 1.0 JSON 配置文件
        """
        fields = self.parse_model_fields()
        json_config = json_config_schema.JSONConfigSchema(**{
            "version": "1.0",
            "app_name": self.app_name,
            "app_desc": self.app_desc,
            "model": {
                "filename": Path(inspect.getfile(self.model)).name,
                "class_name": self.model.__name__,
                "table_args": self.model.__table_args__,
                "fields": fields,
            },
            "schemas": {
                "filename": f"{self.app_name}_schema.py",
                "base_class_name": f"{GenerateBase.snake_to_camel(self.app_name)}Schema",
                "create_class_name": f"{GenerateBase.snake_to_camel(self.app_name)}CreateSchema",
                "update_class_name": f"{GenerateBase.snake_to_camel(self.app_name)}UpdateSchema",
                "simple_out_class_name": f"{GenerateBase.snake_to_camel(self.app_name)}SimpleOutSchema",
            },
            "crud": {
                "filename": f"{self.app_name}_crud.py",
                "class_name": f"{GenerateBase.snake_to_camel(self.app_name)}CRUD",
            },
            "params": {
                "filename": "params.py",
                "class_name": "PageParams",
            },
            "views": {"filename": "views.py", "routers": ["create", "update", "delete", "list_query", "one_query"]},
        })
        return json_config.model_dump()
