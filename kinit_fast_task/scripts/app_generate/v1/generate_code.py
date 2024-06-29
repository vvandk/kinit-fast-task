# @Version        : 1.0
# @Create Time    : 2024/6/14 下午6:58
# @File           : generate_code.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息

from kinit_fast_task.scripts.app_generate.v1.json_config_schema import JSONConfigSchema
from kinit_fast_task.scripts.app_generate.v1.generate_schema import SchemaGenerate
from kinit_fast_task.scripts.app_generate.v1.generate_crud import CrudGenerate
from kinit_fast_task.scripts.app_generate.v1.generate_params import ParamsGenerate
from kinit_fast_task.scripts.app_generate.v1.generate_view import ViewGenerate
from kinit_fast_task.utils.logger import TaskLogger


class GenerateCode:

    def __init__(self, json_config: dict, task_log: TaskLogger):
        self.json_config = JSONConfigSchema(**json_config)
        self.task_log = task_log

    def generate(self):
        """
        代码生成
        """

        schema = SchemaGenerate(self.json_config, self.task_log)
        schema_code = schema.generate_code()
        self.task_log.info(f"\n{schema_code}", is_verbose=False)
        self.task_log.success("Schema 代码生成完成")

        crud = CrudGenerate(self.json_config, self.task_log)
        crud_code = crud.generate_code()
        self.task_log.info(f"\n{crud_code}", is_verbose=False)
        self.task_log.success("CRUD 代码生成完成")

        params = ParamsGenerate(self.json_config, self.task_log)
        params_code = params.generate_code()
        self.task_log.info(f"\n{params_code}", is_verbose=False)
        self.task_log.success("Params 代码生成完成")

        views = ViewGenerate(self.json_config, self.task_log)
        views_code = views.generate_code()
        self.task_log.info(f"\n{views_code}", is_verbose=False)
        self.task_log.success("Views 代码生成完成")

    def write_generate(self):
        """
        写入生成代码
        """
        schema = SchemaGenerate(self.json_config, self.task_log)
        schema.write_generate_code()
        self.task_log.success("Schema 代码写入完成")

        crud = CrudGenerate(self.json_config, self.task_log)
        crud.write_generate_code()
        self.task_log.success("CRUD 代码写入完成")

        params = ParamsGenerate(self.json_config, self.task_log)
        params.write_generate_code()
        self.task_log.success("Params 代码写入完成")

        views = ViewGenerate(self.json_config, self.task_log)
        views.write_generate_code()
        self.task_log.success("Views 代码写入完成")

