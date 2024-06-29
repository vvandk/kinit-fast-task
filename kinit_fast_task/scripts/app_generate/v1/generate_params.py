# ruff: noqa: E501
from pathlib import Path
from kinit_fast_task.config import settings
from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase
from kinit_fast_task.scripts.app_generate.v1.json_config_schema import JSONConfigSchema
from kinit_fast_task.utils.logger import TaskLogger


class ParamsGenerate(GenerateBase):
    def __init__(self, json_config: JSONConfigSchema, task_log: TaskLogger):
        """
        初始化工作

        :param json_config:
        """
        self.json_config = json_config
        self.file_path = Path(settings.router.APPS_PATH) / json_config.app_name / self.json_config.params.filename
        self.project_name = settings.system.PROJECT_NAME
        self.task_log = task_log
        self.task_log.info("开始生成 Params 代码, Params 文件地址为：", self.file_path, is_verbose=True)

    def write_generate_code(self):
        """
        生成 params 文件，以及代码内容
        """
        if self.file_path.exists():
            self.task_log.warning("Params 文件已存在，正在删除重新写入")
            self.file_path.unlink()

        self.create_pag(self.file_path.parent)
        self.file_path.touch()

        code = self.generate_code()
        self.file_path.write_text(code, "utf-8")
        self.task_log.success("Params 代码创建完成")

    def generate_code(self) -> str:
        """
        生成 schema 代码内容
        """
        code = self.generate_file_desc(self.file_path.name, "1.0", self.json_config.app_desc)

        modules = {
            "fastapi": ["Depends"],
            f"{self.project_name}.app.depends.Paging": ["Paging", "QueryParams"],
        }
        code += self.generate_modules_code(modules)

        base_code = f"\n\nclass {self.json_config.params.class_name}(QueryParams):"
        base_code += "\n\tdef __init__(self, params: Paging = Depends()):"
        base_code += "\n\t\tsuper().__init__(params)"
        base_code += "\n"
        code += base_code
        return code.replace("\t", "    ")
