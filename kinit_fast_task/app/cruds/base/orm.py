# @Version        : 1.0
# @Create Time    : 2023/8/21 22:18
# @File           : crud.py
# @IDE            : PyCharm
# @Desc           : 数据库 增删改查操作

import datetime
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import NoResultFound

from kinit_fast_task.utils.response_code import Status as UtilsStatus
from sqlalchemy import func, delete, update, BinaryExpression, select, false, insert, Result, CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import _AbstractLoad
from kinit_fast_task.core import CustomException
from sqlalchemy.sql.selectable import Select as SelectType
from typing import Any, TypeVar, Generic
from pydantic import BaseModel as AbstractSchemaModel
from kinit_fast_task.app.models.base.orm import AbstractORMModel
from abc import ABC, abstractmethod
from enum import Enum


class ReturnType(Enum):
    """
    查询数据返回类型
    """

    MODEL = "model"  # 返回查询结果 ORM Model 对象
    SCHEMA = "schema"  # 返回 Pydantic Schema 序列化对象
    DICT = "dict"  # 返回 Pydantic Schema 序列化后的 Dict
    RAW_RESULT = "raw_result"  # 原始结果，未经处理的结果


ORMModel = TypeVar("ORMModel", bound=AbstractORMModel)


class ORMCrud(ABC, Generic[ORMModel]):
    """
    ORM CRUD 基础操作管理器
    sqlalchemy 官方文档：https://docs.sqlalchemy.org/en/20/index.html
    sqlalchemy 查询操作（官方文档）: https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html
    sqlalchemy 增删改操作：https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html
    """

    @abstractmethod
    def __init__(
        self,
        session: AsyncSession = None,
        model: type[ORMModel] = None,
        simple_out_schema: type[AbstractSchemaModel] = None,
    ):
        """
        初始化 ORM CRUD 基础操作管理器
        :param session: ORM 数据库会话
        :param model: 默认操作 ORM 模型
        :param simple_out_schema: 默认序列化输出 schema
        """
        self.session = session
        self.model = model
        self.simple_out_schema = simple_out_schema
        self.order_fields = ["desc", "descending"]

    async def get_data(
        self,
        data_id: int = None,
        *,
        v_start_sql: SelectType = None,
        v_select_from: list[Any] = None,
        v_join: list[Any] = None,
        v_outer_join: list[Any] = None,
        v_options: list[_AbstractLoad] = None,
        v_where: list[BinaryExpression] = None,
        v_order: str = None,
        v_order_field: str = None,
        v_return_none: bool = False,
        v_schema: type[AbstractSchemaModel] = None,
        v_return_type: ReturnType | str = ReturnType.MODEL,
        v_expire_all: bool = False,
        **kwargs,
    ) -> Any:
        """
        获取单个数据，默认使用 ID 查询，否则使用关键词查询

        :param data_id: 数据 ID
        :param v_start_sql: 初始 sql
        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_options: 用于为查询添加附加选项，如预加载、延迟加载等。
        :param v_where: 当前表查询条件，原始表达式
        :param v_order: 排序，默认正序，为 desc 是倒叙
        :param v_order_field: 排序字段
        :param v_return_none: 是否返回空 None，否认 抛出异常，默认抛出异常
        :param v_schema: 指定使用的序列化对象
        :param v_return_type: 指定数据返回类型，默认返回模型对象
        :param v_expire_all: 使当前会话（Session）中所有已加载的对象过期，确保您获取的是数据库中的最新数据，但可能会有性能损耗，博客：https://blog.csdn.net/k_genius/article/details/135490378。
        :param kwargs: 查询参数
        :return: 默认返回 ORM Model 对象
        """  # noqa E501
        if v_expire_all:
            self.session.expire_all()

        queryset = await self.filter_core(
            v_start_sql=v_start_sql,
            v_select_from=v_select_from,
            v_join=v_join,
            v_outer_join=v_outer_join,
            v_options=v_options,
            v_where=v_where,
            v_order=v_order,
            v_order_field=v_order_field,
            v_return_sql=False,
            id=data_id,
            **kwargs,
        )

        if v_return_type == ReturnType.RAW_RESULT or v_return_type == ReturnType.RAW_RESULT.value:
            return queryset.first()  # 返回格式：(<model object>, )

        data = queryset.scalars().first()

        if not data and v_return_none:
            return None
        elif not data:
            raise CustomException(message="未查询到对应数据！", code=UtilsStatus.HTTP_404)

        if v_return_type == ReturnType.MODEL or v_return_type == ReturnType.MODEL.value:
            return data  # 返回格式：<model object>

        v_schema = v_schema or self.simple_out_schema

        if v_return_type == ReturnType.DICT or v_return_type == ReturnType.DICT.value:
            # 返回格式：{"id": 1, ...}
            return v_schema.model_validate(data).model_dump()
        elif v_return_type == ReturnType.SCHEMA or v_return_type == ReturnType.SCHEMA.value:
            # 返回格式：<schema object>
            return v_schema.model_validate(data)
        else:
            raise CustomException("无效的返回值类型")

    async def get_datas(
        self,
        *,
        page: int = 1,
        limit: int = 10,
        v_start_sql: SelectType = None,
        v_select_from: list[Any] = None,
        v_join: list[Any] = None,
        v_outer_join: list[Any] = None,
        v_options: list[_AbstractLoad] = None,
        v_where: list[BinaryExpression] = None,
        v_order: str = None,
        v_order_field: str = None,
        v_schema: type[AbstractSchemaModel] = None,
        v_return_type: ReturnType | str = ReturnType.MODEL,
        v_expire_all: bool = False,
        **kwargs,
    ) -> Any:
        """
        获取数据列表

        :param page: 页码
        :param limit: 当前页数据量
        :param v_start_sql: 初始 sql
        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_options: 用于为查询添加附加选项，如预加载、延迟加载等。
        :param v_where: 当前表查询条件，原始表达式
        :param v_order: 排序，默认正序，为 desc 是倒叙
        :param v_order_field: 排序字段
        :param v_schema: 指定使用的序列化对象
        :param v_return_type: 指定数据返回类型，默认返回模型对象
        :param v_expire_all: 使当前会话（Session）中所有已加载的对象过期，确保您获取的是数据库中的最新数据，但可能会有性能损耗，博客：https://blog.csdn.net/k_genius/article/details/135490378。
        :param kwargs: 查询参数，使用的是自定义表达式
        :return:
        """  # noqa E501
        if v_expire_all:
            self.session.expire_all()

        sql: SelectType = await self.filter_core(
            v_start_sql=v_start_sql,
            v_select_from=v_select_from,
            v_join=v_join,
            v_outer_join=v_outer_join,
            v_options=v_options,
            v_where=v_where,
            v_order=v_order,
            v_order_field=v_order_field,
            v_return_sql=True,
            **kwargs,
        )

        if limit != 0:
            sql = sql.offset((page - 1) * limit).limit(limit)

        queryset = await self.session.execute(sql)
        if v_return_type == ReturnType.RAW_RESULT or v_return_type == ReturnType.RAW_RESULT.value:
            return queryset.all()  # 返回格式：[(<model object>, ), (<model object>, ), ...]

        queryset = queryset.scalars().all()

        if v_return_type == ReturnType.MODEL or v_return_type == ReturnType.MODEL.value:
            return queryset  # 返回格式：[<model object>, <model object>, ...]

        v_schema = v_schema or self.simple_out_schema

        if v_return_type == ReturnType.DICT or v_return_type == ReturnType.DICT.value:
            # 返回格式：[{"id": 1, ...}, {"id": 2, ...}, ...]
            return [v_schema.model_validate(obj).model_dump() for obj in queryset]
        elif v_return_type == ReturnType.SCHEMA or v_return_type == ReturnType.SCHEMA.value:
            # 返回格式：[<schema object>, <schema object>, ...]
            return [v_schema.model_validate(obj) for obj in queryset]
        else:
            raise CustomException("无效的返回值类型")

    async def get_count(
        self,
        *,
        v_select_from: list[Any] = None,
        v_join: list[Any] = None,
        v_outer_join: list[Any] = None,
        v_where: list[BinaryExpression] = None,
        **kwargs,
    ) -> int:
        """
        获取数据总数

        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_where: 当前表查询条件，原始表达式
        :param kwargs: 查询参数
        :return: 返回数据总数
        """  # noqa E501
        v_start_sql = select(func.count(self.model.id))
        sql = await self.filter_core(
            v_start_sql=v_start_sql,
            v_select_from=v_select_from,
            v_join=v_join,
            v_outer_join=v_outer_join,
            v_where=v_where,
            v_return_sql=True,
            **kwargs,
        )
        queryset = await self.session.execute(sql)
        return queryset.one()[0]

    async def create_data(self, data: AbstractSchemaModel | dict, *, v_return_obj: bool = False) -> ORMModel | str:
        """
        创建单个数据

        insert 官方文档：https://docs.sqlalchemy.org/en/20/tutorial/data_insert.html

        ORM Unit 官方文档：https://docs.sqlalchemy.org/en/20/tutorial/orm_data_manipulation.html#inserting-rows-using-the-orm-unit-of-work-pattern

        :param data: 创建数据
        :param v_return_obj: 是否返回 ORM 对象
        :return:
        """  # noqa E501
        obj = self.model(**jsonable_encoder(data))
        await self.flush(obj)
        if v_return_obj:
            return obj
        return "创建成功"

    async def create_datas(
        self, datas: list[dict | AbstractSchemaModel], v_return_objs: bool = False
    ) -> list[ORMModel] | str:
        """
        批量创建数据

        官方文档：https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-expression-update-delete

        SQLAlchemy 2.0 批量插入不支持 MySQL 返回值：
        https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#getting-new-objects-with-returning

        :param datas: 字典数据列表
        :param v_return_objs: 是否返回结果对象
        """  # noqa E501
        sql = insert(self.model)
        if v_return_objs:
            sql = sql.returning(self.model)
        result = await self.session.execute(sql, datas)
        if v_return_objs:
            queryset = result.scalars().all()
            assert isinstance(queryset, list)
            return queryset
        return "批量创建成功"

    async def update_data(
        self, data_id: int, data: AbstractSchemaModel | dict, *, v_return_obj: bool = False
    ) -> ORMModel | str:
        """
        根据 id 更新单个数据

        官方文档：https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-update-and-delete-with-custom-where-criteria

        :param data_id: 修改行数据的 ID
        :param data: 更新的数据内容
        :param v_return_obj: ，是否返回对象
        """
        sql = update(self.model).where(self.model.id == data_id).values(**jsonable_encoder(data))
        if v_return_obj:
            sql = sql.returning(self.model)
        result = await self.session.execute(sql)
        if v_return_obj:
            try:
                obj = result.scalar_one()
                return obj
            except NoResultFound:
                raise CustomException("未查询到需要更新的数据！", code=UtilsStatus.HTTP_404)
        assert isinstance(result, CursorResult)
        if result.rowcount == 0:
            raise CustomException("未查询到需要更新的数据！", code=UtilsStatus.HTTP_404)
        return "更新成功"

    async def delete_datas(self, ids: list[int], *, v_soft: bool = False, **kwargs) -> str:
        """
        删除多条数据

        :param ids: 数据集
        :param v_soft: 是否执行软删除
        :param kwargs: 其他更新字段
        """
        if v_soft:
            # 软删除，给数据添加标记
            result = await self.session.execute(
                update(self.model)
                .where(self.model.id.in_(ids))
                .values(delete_datetime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), is_delete=True, **kwargs)
            )
        else:
            # 硬删除，直接从数据库中删除
            result = await self.session.execute(delete(self.model).where(self.model.id.in_(ids)))
        if result.rowcount == 0:
            raise CustomException("未查询到需要删除的数据！", code=UtilsStatus.HTTP_404)
        return "删除成功"

    async def flush(self, obj: ORMModel = None) -> ORMModel | None:
        """
        刷新到数据库

        :param obj:
        :return:
        """
        if obj:
            self.session.add(obj)
        await self.session.flush()
        return obj

    async def filter_core(
        self,
        v_start_sql: SelectType = None,
        v_select_from: list[Any] = None,
        v_join: list[Any] = None,
        v_outer_join: list[Any] = None,
        v_options: list[_AbstractLoad] = None,
        v_where: list[BinaryExpression] = None,
        v_order: str = None,
        v_order_field: str = None,
        v_return_sql: bool = False,
        **kwargs,
    ) -> Result | SelectType:
        """
        数据过滤核心功能

        :param v_start_sql: 初始 sql
        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_options: 用于为查询添加附加选项，如预加载、延迟加载等。
        :param v_where: 当前表查询条件，原始表达式
        :param v_order: 排序，默认正序，为 desc 是倒叙
        :param v_order_field: 排序字段
        :param v_return_sql: 是否直接返回 sql
        :return: 返回过滤后的总数居 或 sql
        """  # noqa E501
        if not isinstance(v_start_sql, SelectType):
            v_start_sql = select(self.model).where(self.model.is_delete == false())

        sql = self.add_relation(
            v_start_sql=v_start_sql,
            v_select_from=v_select_from,
            v_join=v_join,
            v_outer_join=v_outer_join,
            v_options=v_options,
        )

        if v_where:
            sql = sql.where(*v_where)

        sql = self.add_filter_condition(sql, **kwargs)

        if v_order_field and (v_order in self.order_fields):
            sql = sql.order_by(getattr(self.model, v_order_field).desc(), self.model.id.desc())
        elif v_order_field:
            sql = sql.order_by(getattr(self.model, v_order_field), self.model.id)
        elif v_order in self.order_fields:
            sql = sql.order_by(self.model.id.desc())

        if v_return_sql:
            return sql

        queryset = await self.session.execute(sql)

        return queryset

    def add_relation(
        self,
        v_start_sql: SelectType,
        v_select_from: list[Any] = None,
        v_join: list[Any] = None,
        v_outer_join: list[Any] = None,
        v_options: list[_AbstractLoad] = None,
    ) -> SelectType:
        """
        关系查询，关系加载

        :param v_start_sql: 初始 sql
        :param v_select_from: 用于指定查询从哪个表开始，通常与 .join() 等方法一起使用。
        :param v_join: 创建内连接（INNER JOIN）操作，返回两个表中满足连接条件的交集。
        :param v_outer_join: 用于创建外连接（OUTER JOIN）操作，返回两个表中满足连接条件的并集，包括未匹配的行，并用 NULL 值填充。
        :param v_options: 用于为查询添加附加选项，如预加载、延迟加载等。
        """  # noqa E501
        if v_select_from:
            v_start_sql = v_start_sql.select_from(*v_select_from)

        if v_join:
            for relation in v_join:
                table = relation[0]
                if isinstance(table, str):
                    table = getattr(self.model, table)
                if len(relation) == 2:
                    v_start_sql = v_start_sql.join(table, relation[1])
                else:
                    v_start_sql = v_start_sql.join(table)

        if v_outer_join:
            for relation in v_outer_join:
                table = relation[0]
                if isinstance(table, str):
                    table = getattr(self.model, table)
                if len(relation) == 2:
                    v_start_sql = v_start_sql.outerjoin(table, relation[1])
                else:
                    v_start_sql = v_start_sql.outerjoin(table)

        if v_options:
            v_start_sql = v_start_sql.options(*v_options)

        return v_start_sql

    def add_filter_condition(self, sql: SelectType, **kwargs) -> SelectType:
        """
        添加过滤条件

        :param sql:
        :param kwargs: 关键词参数
        """
        conditions = self.__dict_filter(**kwargs)
        if conditions:
            sql = sql.where(*conditions)
        return sql

    def __dict_filter(self, **kwargs) -> list[BinaryExpression]:
        """
        字典过滤

        :param model:
        :param kwargs:
        """
        conditions = []
        for field, value in kwargs.items():
            if value is not None and value != "":
                attr = getattr(self.model, field)
                if isinstance(value, tuple):
                    if len(value) == 1:
                        if value[0] == "None":
                            conditions.append(attr.is_(None))
                        elif value[0] == "not None":
                            conditions.append(attr.isnot(None))
                        else:
                            raise CustomException(f"{self}.__dict_filter SQL查询语法错误")
                    elif len(value) == 2 and value[1] not in [None, [], ""]:
                        if value[0] == "date":
                            # 根据日期查询， 关键函数是：func.time_format和func.date_format
                            conditions.append(func.date_format(attr, "%Y-%m-%d") == value[1])
                        elif value[0] == "like":
                            conditions.append(attr.like(f"%{value[1]}%"))
                        elif value[0] == "in":
                            conditions.append(attr.in_(value[1]))
                        elif value[0] == "between" and len(value[1]) == 2:
                            conditions.append(attr.between(value[1][0], value[1][1]))
                        elif value[0] == "month":
                            conditions.append(func.date_format(attr, "%Y-%m") == value[1])
                        elif value[0] == "!=":
                            conditions.append(attr != value[1])
                        elif value[0] == ">":
                            conditions.append(attr > value[1])
                        elif value[0] == ">=":
                            conditions.append(attr >= value[1])
                        elif value[0] == "<=":
                            conditions.append(attr <= value[1])
                        else:
                            raise CustomException(f"{self}.__dict_filter SQL查询语法错误")
                else:
                    conditions.append(attr == value)
        return conditions

    def __str__(self):
        return self.__class__.__name__
