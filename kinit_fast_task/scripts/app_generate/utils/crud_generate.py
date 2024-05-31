# ruff: noqa: E501
from pathlib import Path

from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.core.logger import log
from .generate_base import GenerateBase


class CrudGenerate(GenerateBase):
    def __init__(
        self,
        *,
        model: type[AbstractORMModel],
        en_name: str,
        crud_class_name: str,
        schema_simple_out_class_name: str,
        crud_file_path: Path,
        **kwargs,
    ):
        """
        初始化工作
        :param model: 提前定义好的 ORM 模型
        :param en_name: 功能英文名称，主要用于 Schema, Params, CRUD, URL 命名，默认使用 model class
            en_name 例子：
                如果 en_name 由多个单词组成那么请使用 _ 下划线拼接
                在命名文件名称时，会执行使用 _ 下划线名称
                在命名 class 名称时，会将下划线名称转换为大驼峰命名（CamelCase）
                在命名 url 时，会将下划线转换为 /
        :param crud_class_name:
        :param schema_simple_out_class_name:
        :param crud_file_path:
        """  # noqa E501
        self.model = model
        self.crud_class_name = crud_class_name
        self.schema_simple_out_class_name = schema_simple_out_class_name
        self.en_name = en_name
        self.crud_file_path = crud_file_path

    def write_generate_code(self):
        """
        生成 crud 文件，以及代码内容
        :return:
        """
        if self.crud_file_path.exists():
            log.info("CRUD 文件已存在，正在删除重新写入")
            self.crud_file_path.unlink()

        self.crud_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.crud_file_path.touch()

        code = self.generate_code()
        self.crud_file_path.write_text(code, "utf-8")
        log.info("CRUD 代码创建完成")

    def generate_code(self):
        """
        代码生成
        :return:
        """
        code = self.generate_file_desc(self.crud_file_path.name, "1.0", "数据操作")
        code += self.generate_modules_code(self.get_base_module_config())
        code += self.get_base_code_content()
        return code

    def get_base_module_config(self):
        """
        获取基础模块导入配置
        :return:
        """
        modules = {
            "sqlalchemy.ext.asyncio": ["AsyncSession"],
            "kinit_fast_task.app.cruds.base.orm": ["ORMCrud"],
            f"kinit_fast_task.app.schemas.{self.en_name}": [self.schema_simple_out_class_name],
            f"kinit_fast_task.app.models.{self.en_name}": [self.model.__name__],
        }
        return modules

    def get_base_code_content(self):
        """
        获取基础代码内容
        :return:
        """
        base_code = (
            f"\n\nclass {self.crud_class_name}(ORMCrud[{self.model.__name__}, {self.schema_simple_out_class_name}]):\n"
        )
        base_code += "\n\tdef __init__(self, db: AsyncSession):"
        base_code += "\n\t\tsuper().__init__()"
        base_code += "\n\t\tself.db = db"
        base_code += f"\n\t\tself.model = {self.model.__name__}"
        base_code += f"\n\t\tself.simple_out_schema = {self.schema_simple_out_class_name}"
        base_code += "\n"
        return base_code.replace("\t", "    ")
