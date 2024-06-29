# @Version        : 1.0
# @Create Time    : 2024/6/14 下午6:58
# @File           : generate_code.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息
from pathlib import Path

from kinit_fast_task.scripts.app_generate.v1.json_config_schema import JSONConfigSchema
from kinit_fast_task.scripts.app_generate.v1.generate_schema import SchemaGenerate
from kinit_fast_task.scripts.app_generate.v1.generate_crud import CrudGenerate
from kinit_fast_task.scripts.app_generate.v1.generate_params import ParamsGenerate
from kinit_fast_task.scripts.app_generate.v1.generate_view import ViewGenerate


class GenerateCode:

    def __init__(self, json_config: dict):
        self.json_config = JSONConfigSchema(**json_config)

    def generate(self):
        """
        代码生成
        """
        schema = SchemaGenerate(self.json_config)
        schema.generate_code()
        crud = CrudGenerate(self.json_config)
        crud.generate_code()
        params = ParamsGenerate(self.json_config)
        params.generate_code()
        views = ViewGenerate(self.json_config)
        views.generate_code()

