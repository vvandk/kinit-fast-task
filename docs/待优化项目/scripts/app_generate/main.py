import importlib
from pathlib import Path
from kinit_fast_task.config import settings
from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase
from kinit_fast_task.scripts.app_generate.utils.schema_generate import SchemaGenerate
from kinit_fast_task.scripts.app_generate.utils.params_generate import ParamsGenerate
from kinit_fast_task.scripts.app_generate.utils.crud_generate import CrudGenerate
from kinit_fast_task.scripts.app_generate.utils.view_generate import ViewGenerate
from kinit_fast_task.utils.tools import snake_to_camel, ruff_format_code
from kinit_fast_task.app.models.base.orm import AbstractORMModel


class AppGenerate(GenerateBase):
    """
    这里是 AppGenerate 的文档
    """

    SCRIPT_PATH = Path(settings.system.BASE_PATH) / "scripts" / "app_generate"

    def __init__(self, model_file_name: str, *, zh_name: str = None, en_name: str = None):
        """
        初始化 AppGenerate 类，设置模型文件名、中文名称和英文名称

        :param model_file_name: 提前定义好的 ORM Model 文件名称
        :param zh_name: 功能中文名称，主要用于描述和注释，默认使用表说明信息 comment
        :param en_name: 功能英文名称:，主要用于 Schema, Params, CRUD, URL 命名，默认使用 model class
            en_name 例子：
                1. 如果 en_name 由多个单词组成那么请使用 _ 下划线拼接
                2. 在命名文件名称时，会执行使用 _ 下划线名称
                3. 在命名 class 名称时，会将下划线名称转换为大驼峰命名（CamelCase）
                4. 在命名 url 时，会将下划线转换为 /
        """
        self.model_file_name = model_file_name
        self.model = self.model_mapping()

        self.en_name = en_name if en_name else model_file_name
        self.zh_name = zh_name if zh_name else self.get_model_comment()

        # 初始化 schemas、API、CRUD 文件的路径
        self.schema_file_path = None
        self.crud_file_path = None
        self.param_file_path = None
        self.view_file_path = None
        self.routers_init_file = None
        self.setup_paths()

        # 根据 en_name 设置类名和文件名
        self.base_class_name = None
        self.schema_simple_out_class_name = None
        self.crud_class_name = None
        self.param_class_name = None
        self.setup_names()

    def model_mapping(self) -> type[AbstractORMModel]:
        """
        映射 ORM Model

        :return: ORM Model 类
        """
        module = importlib.import_module(f"{settings.system.PROJECT_NAME}.app.models.{self.model_file_name}")
        class_name = snake_to_camel(self.model_file_name)
        return getattr(module, class_name)

    def get_model_comment(self) -> str:
        """
        获取模型的注释信息，并去掉其中的“表”字

        :return: 注释字符串
        """
        comment: str = self.model.__table_args__.get("comment", "")
        return comment.replace("表", "")

    def setup_paths(self):
        """
        初始化 schemas、API、CRUD 文件的路径
        """
        base_path = Path(settings.system.BASE_PATH) / "app"

        self.schema_file_path = base_path / "schemas" / f"{self.en_name}.py"
        self.crud_file_path = base_path / "cruds" / f"{self.en_name}.py"

        routers_dir_path = base_path / "routers" / self.en_name

        self.param_file_path = routers_dir_path / "params.py"
        self.view_file_path = routers_dir_path / "views.py"
        self.routers_init_file = routers_dir_path / "__init__.py"

    def setup_names(self):
        """
        根据 en_name 设置类名和文件名
        """
        self.base_class_name = snake_to_camel(self.en_name)
        self.schema_simple_out_class_name = f"{self.base_class_name}SimpleOut"
        self.crud_class_name = f"{self.base_class_name}CRUD"
        self.param_class_name = "PageParams"

    def generate_codes(self) -> str:
        """
        生成代码并记录输出，不执行实际操作，仅打印生成的代码
        """
        out_result = [f"{self.schema_file_path} 代码内容："]
        out_result.append(self.generate_and_log(SchemaGenerate))

        out_result.append(f"{self.crud_file_path} 代码内容：")
        out_result.append(self.generate_and_log(CrudGenerate))

        out_result.append(f"{self.param_file_path} 代码内容：")
        out_result.append(self.generate_and_log(ParamsGenerate))

        out_result.append(f"{self.view_file_path} 代码内容：")
        out_result.append(self.generate_and_log(ViewGenerate))
        return "\n".join(out_result)

    def generate_and_log(self, generator_class) -> str:
        """
        为给定的生成器类和文件路径生成并记录代码

        :param generator_class: 用于代码生成的类
        """
        generator = generator_class(
            model=self.model,
            en_name=self.en_name,
            base_class_name=self.base_class_name,
            schema_simple_out_class_name=self.schema_simple_out_class_name,
            crud_class_name=self.crud_class_name,
            param_class_name=self.param_class_name,
            zh_name=self.zh_name,
            schema_file_path=self.schema_file_path,
            crud_file_path=self.crud_file_path,
            param_file_path=self.param_file_path,
            view_file_path=self.view_file_path,
        )
        return generator.generate_code()

    def write_app_generate_code(self, format_code: bool = True):
        """
        开始生成应用程序代码并将其写入项目中

        :param format_code: 是否在生成后格式化代码
        """
        self.write_code(SchemaGenerate)
        self.write_code(CrudGenerate)
        self.write_code(ParamsGenerate)
        self.write_code(ViewGenerate)

        if not self.routers_init_file.exists():
            self.routers_init_file.touch()

        if format_code:
            ruff_format_code()

    def write_code(self, generator_class):
        """
        为给定的生成器类和文件路径写入生成的代码

        :param generator_class: 用于代码生成的类
        """
        generator = generator_class(
            model=self.model,
            en_name=self.en_name,
            base_class_name=self.base_class_name,
            schema_simple_out_class_name=self.schema_simple_out_class_name,
            crud_class_name=self.crud_class_name,
            param_class_name=self.param_class_name,
            zh_name=self.zh_name,
            schema_file_path=self.schema_file_path,
            crud_file_path=self.crud_file_path,
            param_file_path=self.param_file_path,
            view_file_path=self.view_file_path,
        )
        generator.write_generate_code()


if __name__ == "__main__":
    generate = AppGenerate("auth_user")
    print(generate.generate_codes())
    # generate.write_app_generate_code()
