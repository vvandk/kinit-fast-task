# @version        : 1.0
# @Create Time    : 2024/1/12 17:28
# @File           : schema_generate.py
# @IDE            : PyCharm
# @desc           : schema 代码生成

from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase
from kinit_fast_task.scripts.app_generate.v1.json_config_schema import JSONConfigSchema
from kinit_fast_task.config import settings
from kinit_fast_task.utils.logger import TaskLogger


class SchemaGenerate(GenerateBase):
    BASE_FIELDS = ["id", "create_datetime", "update_datetime", "delete_datetime", "is_delete"]

    def __init__(self, json_config: JSONConfigSchema, task_log: TaskLogger):
        """
        初始化工作

        :param json_config:
        :param task_log:
        """
        self.json_config = json_config
        self.file_path = settings.BASE_PATH / "app" / "schemas" / self.json_config.schemas.filename
        self.project_name = settings.system.PROJECT_NAME
        self.task_log = task_log
        self.task_log.info("开始生成 Schema 代码, Schema 文件地址为：", self.file_path, is_verbose=True)

    def write_generate_code(self, overwrite: bool = False):
        """
        生成 schema 文件，以及代码内容
        """

        if self.file_path.exists():
            if overwrite:
                self.task_log.warning("Schema 文件已存在, 已选择覆盖, 正在删除重新写入.")
                self.file_path.unlink()
            else:
                self.task_log.warning("Schema 文件已存在, 未选择覆盖, 不再进行 Schema 代码生成.")
                return False

        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.touch()

        code = self.generate_code()
        self.file_path.write_text(code, "utf-8")
        self.task_log.success("Schema 代码写入完成")

    def generate_code(self) -> str:
        """
        生成 schema 代码内容
        """
        schema = self.json_config.schemas
        code = self.generate_file_desc(self.file_path.name, "1.0", "Pydantic 模型，用于数据库序列化操作")

        modules = {
            "pydantic": ["Field"],
            f"{self.project_name}.core.types": ["DatetimeStr"],
            f"{self.project_name}.app.schemas.base": ["BaseSchema"],
        }
        code += self.generate_modules_code(modules)

        # 生成字段列表
        schema_field_code = ""
        for item in self.json_config.model.fields:
            if item.name in self.BASE_FIELDS:
                continue
            field = f'\n\t{item.name}: {item.field_python_type} {"| None " if item.nullable else ""}'
            default = None
            if item.default is not None:
                if item.field_python_type == "str":
                    default = f'"{item.default}"'
                else:
                    default = item.default
            elif default is None and not item.nullable:
                default = "..."

            field += f'= Field({default}, description="{item.comment}")'
            schema_field_code += field
        schema_field_code += "\n"

        base_schema_code = f"\n\nclass {schema.base_class_name}(BaseSchema):"
        base_schema_code += schema_field_code
        code += base_schema_code

        create_schema_code = f"\n\nclass {schema.create_class_name}({schema.base_class_name}):"
        create_schema_code += "\n\tpass\n"
        code += create_schema_code

        update_schema_code = f"\n\nclass {schema.update_class_name}({schema.base_class_name}):"
        update_schema_code += "\n\tpass\n"
        code += update_schema_code

        base_out_schema_code = f"\n\nclass {schema.simple_out_class_name}({schema.base_class_name}):"
        base_out_schema_code += '\n\tid: int = Field(..., description="编号")'
        base_out_schema_code += '\n\tcreate_datetime: DatetimeStr = Field(..., description="创建时间")'
        base_out_schema_code += '\n\tupdate_datetime: DatetimeStr = Field(..., description="更新时间")'
        base_out_schema_code += "\n"
        code += base_out_schema_code
        return code.replace("\t", "    ")
