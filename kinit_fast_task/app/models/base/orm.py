# @Version        : 1.0
# @Create Time    : 2021/10/18 22:19
# @File           : orm.py
# @IDE            : PyCharm
# @Desc           : 数据库公共 ORM 模型

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from kinit_fast_task.db.orm.async_base_model import AsyncBaseORMModel
from sqlalchemy import func, inspect


class AbstractORMModel(AsyncBaseORMModel):
    """
    公共 ORM 模型，基表

    表配置官方文档：https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
    支持 Enum 与 Literal 官方文档：https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#using-python-enum-or-pep-586-literal-types-in-the-type-map
    中文官方文档：https://docs.sqlalchemy.org.cn/en/20/orm/declarative_tables.html#using-annotated-declarative-table-type-annotated-forms-for-mapped-column
    """  # noqa E501

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, comment="主键ID")
    create_datetime: Mapped[datetime] = mapped_column(server_default=func.now(), comment="创建时间")
    update_datetime: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
    delete_datetime: Mapped[datetime | None] = mapped_column(comment="删除时间")
    is_delete: Mapped[bool] = mapped_column(default=False, comment="是否软删除")

    @classmethod
    def get_column_attrs(cls) -> list:
        """
        获取模型中除 relationships 外的所有字段名称
        :return:
        """
        mapper = inspect(cls)

        # for column in mapper.columns:
        #     assert isinstance(column, Column)
        #     print(column)
        #     print(column.__dict__)
        #     print(type(column))
        #     print(column.name)
        #     print(column.type, column.type.python_type, type(column.type), column.type.__dict__)
        #     print(column.nullable)
        #     print(column.default)
        #     print(column.comment)

        return mapper.columns.keys()

    @classmethod
    def get_attrs(cls) -> list:
        """
        获取模型所有字段名称
        :return:
        """
        mapper = inspect(cls)
        return mapper.attrs.keys()

    @classmethod
    def get_relationships_attrs(cls) -> list:
        """
        获取模型中 relationships 所有字段名称
        :return:
        """
        mapper = inspect(cls)
        return mapper.relationships.keys()
