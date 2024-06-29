from pathlib import Path

from kinit_fast_task.config import settings
from kinit_fast_task.core import log
from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase
from kinit_fast_task.scripts.app_generate.v1.json_config_schema import JSONConfigSchema


class CrudGenerate(GenerateBase):

    def __init__(self, json_config: JSONConfigSchema):
        """
        初始化工作

        :param json_config:
        """
        self.json_config = json_config
        self.file_path = settings.BASE_PATH / "app" / "cruds" / self.json_config.crud.filename

    def write_generate_code(self):
        """
        生成 crud 文件，以及代码内容
        """
        if self.file_path.exists():
            log.info("CRUD 文件已存在，正在删除重新写入")
            self.file_path.unlink()

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch()

        code = self.generate_code()
        self.file_path.write_text(code, "utf-8")
        log.info("CRUD 代码创建完成")

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

        modules = {
            "sqlalchemy.ext.asyncio": ["AsyncSession"],
            "kinit_fast_task.app.cruds.base.orm": ["ORMCrud"],
            f"kinit_fast_task.app.schemas.{schema_file_name}": [self.json_config.schemas.simple_out_class_name],
            f"kinit_fast_task.app.models.{schema_file_name}": [self.json_config.model.class_name],
        }
        return modules

    def get_base_code_content(self):
        """
        获取基础代码内容
        """
        base_code = (
            f"\n\nclass {self.json_config.crud.class_name}(ORMCrud[{self.json_config.model.class_name}]):\n"
        )
        base_code += "\n\tdef __init__(self, session: AsyncSession):"
        base_code += "\n\t\tsuper().__init__()"
        base_code += "\n\t\tself.session = session"
        base_code += f"\n\t\tself.model = {self.json_config.model.__name__}"
        base_code += f"\n\t\tself.simple_out_schema = {self.json_config.schemas.simple_out_class_name}"
        base_code += "\n"
        return base_code.replace("\t", "    ")
