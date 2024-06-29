from pathlib import Path

from kinit_fast_task.config import settings
from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase
from kinit_fast_task.scripts.app_generate.v1.json_config_schema import JSONConfigSchema
from kinit_fast_task.utils.logger import TaskLogger


class CrudGenerate(GenerateBase):

    def __init__(self, json_config: JSONConfigSchema, task_log: TaskLogger):
        """
        初始化工作

        :param json_config:
        :param task_log:
        """
        self.json_config = json_config
        self.file_path = settings.BASE_PATH / "app" / "cruds" / self.json_config.crud.filename
        self.project_name = settings.system.PROJECT_NAME
        self.task_log = task_log
        self.task_log.info("开始生成 CRUD 代码, CRUD 文件地址为：", self.file_path, is_verbose=True)

    def write_generate_code(self):
        """
        生成 crud 文件，以及代码内容
        """
        if self.file_path.exists():
            self.task_log.warning("CRUD 文件已存在，正在删除重新写入")
            self.file_path.unlink()

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch()

        code = self.generate_code()
        self.file_path.write_text(code, "utf-8")
        self.task_log.success("CRUD 代码创建完成")

    def generate_code(self):
        """
        代码生成
        """
        code = self.generate_file_desc(self.file_path.name, "1.0", "数据操作")
        code += self.generate_modules_code(self.get_base_module_config())
        code += self.get_base_code_content()
        return code

    def get_base_module_config(self):
        """
        获取基础模块导入配置
        """
        schema_file_name = Path(self.json_config.schemas.filename).name
        model_file_name = Path(self.json_config.model.filename).name

        modules = {
            "sqlalchemy.ext.asyncio": ["AsyncSession"],
            f"{self.project_name}.app.cruds.base": ["ORMCrud"],
            f"{self.project_name}.app.schemas": [schema_file_name],
            f"{self.project_name}.app.models.{model_file_name}": [self.json_config.model.class_name],
        }
        return modules

    def get_base_code_content(self):
        """
        获取基础代码内容
        """
        schema_file_name = Path(self.json_config.schemas.filename).stem
        schema_out_class_name = self.json_config.schemas.simple_out_class_name

        base_code = (
            f"\n\nclass {self.json_config.crud.class_name}(ORMCrud[{self.json_config.model.class_name}]):\n"
        )
        base_code += "\n\tdef __init__(self, session: AsyncSession):"
        base_code += "\n\t\tsuper().__init__()"
        base_code += "\n\t\tself.session = session"
        base_code += f"\n\t\tself.model = {self.json_config.model.class_name}"
        base_code += f"\n\t\tself.simple_out_schema = {schema_file_name}.{schema_out_class_name}"
        base_code += "\n"
        return base_code.replace("\t", "    ")
