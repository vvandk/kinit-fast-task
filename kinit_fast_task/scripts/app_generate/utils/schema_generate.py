# @version        : 1.0
# @Create Time    : 2024/1/12 17:28
# @File           : schema_generate.py
# @IDE            : PyCharm
# @desc           : schema 代码生成


from sqlalchemy import inspect as model_inspect
from pathlib import Path

from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.core.logger import log
from kinit_fast_task.scripts.app_generate.utils.schema import SchemaField
from sqlalchemy.sql.schema import Column as ColumnType
from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase


class SchemaGenerate(GenerateBase):
    BASE_FIELDS = ["id", "create_datetime", "update_datetime", "delete_datetime", "is_delete"]

    def __init__(
        self,
        *,
        model: type[AbstractORMModel],
        en_name: str,
        schema_file_path: Path,
        base_class_name: str,
        schema_simple_out_class_name: str,
        **kwargs,
    ):
        """
        初始化工作
        :param model: 提前定义好的 ORM 模型
        :param schema_file_path:
        :param en_name: 功能英文名称
        :param base_class_name: 基础名称
        :param schema_simple_out_class_name: simple out schema 名称
        """  # noqa E501
        self.model = model
        self.base_class_name = base_class_name
        self.schema_simple_out_class_name = schema_simple_out_class_name
        self.en_name = en_name
        self.schema_file_path = schema_file_path

    def write_generate_code(self):
        """
        生成 schema 文件，以及代码内容
        :return:
        """
        if self.schema_file_path.exists():
            log.info("Schema 文件已存在，正在删除重新写入")
            self.schema_file_path.unlink()

        self.schema_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.schema_file_path.touch()

        code = self.generate_code()
        self.schema_file_path.write_text(code, "utf-8")
        log.info("Schema 代码创建完成")

    def generate_code(self) -> str:
        """
        生成 schema 代码内容
        :return:
        """
        fields = []
        mapper = model_inspect(self.model)
        for attr_name, column_property in mapper.column_attrs.items():
            if attr_name in self.BASE_FIELDS:
                continue
            # 假设它是单列属性
            column: ColumnType = column_property.columns[0]
            item = SchemaField(
                name=attr_name,
                field_type=column.type.python_type.__name__,
                nullable=column.nullable,
                default=column.default.__dict__.get("arg", None) if column.default else None,
                title=column.comment,
                max_length=column.type.__dict__.get("length", None),
            )
            fields.append(item)

        code = self.generate_file_desc(self.schema_file_path.name, "1.0", "Pydantic 模型，用于数据库序列化操作")

        modules = {
            "pydantic": ["Field"],
            "kinit_fast_task.core.types": ["DatetimeStr"],
            "kinit_fast_task.app.schemas.base.base": ["BaseSchema"],
        }
        code += self.generate_modules_code(modules)

        # 生成字段列表
        schema_field_code = ""
        for item in fields:
            field = f'\n\t{item.name}: {item.field_type} {"| None " if item.nullable else ""}'
            default = None
            if item.default is not None:
                if item.field_type == "str":
                    default = f'"{item.default}"'
                else:
                    default = item.default
            elif default is None and not item.nullable:
                default = "..."

            field += f'= Field({default}, description="{item.title}")'
            schema_field_code += field
        schema_field_code += "\n"

        base_schema_code_class_name = f"{self.base_class_name}Base"

        base_schema_code = f"\n\nclass {base_schema_code_class_name}(BaseSchema):"
        base_schema_code += schema_field_code
        code += base_schema_code

        create_schema_code = f"\n\nclass {self.base_class_name}Create({base_schema_code_class_name}):"
        create_schema_code += "\n\tpass\n"
        code += create_schema_code

        update_schema_code = f"\n\nclass {self.base_class_name}Update({base_schema_code_class_name}):"
        update_schema_code += "\n\tpass\n"
        code += update_schema_code

        base_out_schema_code = f"\n\nclass {self.schema_simple_out_class_name}({base_schema_code_class_name}):"
        base_out_schema_code += '\n\tid: int = Field(..., description="编号")'
        base_out_schema_code += '\n\tcreate_datetime: DatetimeStr = Field(..., description="创建时间")'
        base_out_schema_code += '\n\tupdate_datetime: DatetimeStr = Field(..., description="更新时间")'
        base_out_schema_code += "\n"
        code += base_out_schema_code
        return code.replace("\t", "    ")
