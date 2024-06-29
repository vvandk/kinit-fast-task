# @Version        : 1.0
# @Create Time    : 2024/6/7 下午1:45
# @File           : model_to_json.py
# @IDE            : PyCharm
# @Desc           : model to json

from sqlalchemy import inspect as sa_inspect, Column
from sqlalchemy.sql.schema import ScalarElementColumnDefault

from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.scripts.app_generate.utils import schema_base


class ModelToJsonBase:
    def __init__(self, model: type(AbstractORMModel), app_name: str, app_desc: str):
        """
        基于单个 model 输出 JSON 配置文件

        :param model: Model 类
        :param app_name: app 名称, 示例：auth_user
        :param app_desc: app 描述, 示例：AuthUserModel
        """
        self.model = model
        self.app_name = app_name
        self.app_desc = app_desc

    def parse_model_fields(self) -> list[schema_base.ModelFieldSchema]:
        """
        解析模型字段

        :return:
        """
        fields = []
        mapper = sa_inspect(self.model)
        for column in mapper.columns:
            assert isinstance(column, Column)
            default = column.default
            if default is not None:
                assert isinstance(default, ScalarElementColumnDefault)
                default = default.arg
            field_type = type(column.type).__name__
            params = column.type.__dict__
            if field_type == "String":
                keys = ["length"]
            elif field_type == "DECIMAL":
                keys = ["precision", "scale"]
            else:
                keys = []
            field_kwargs = {key: params[key] for key in keys}
            item = schema_base.ModelFieldSchema(
                name=column.name,
                field_type=field_type,
                field_python_type=column.type.python_type.__name__,
                field_kwargs=field_kwargs,
                nullable=column.nullable,
                default=default,
                comment=column.comment,
            )
            fields.append(item)
        return fields
