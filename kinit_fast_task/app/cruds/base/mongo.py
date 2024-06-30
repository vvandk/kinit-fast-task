# @Version        : 1.0
# @Create Time    : 2024/04/08 22:18
# @File           : mongo.py
# @IDE            : PyCharm
# @Desc           : mongo 数据库 增删改查操作

import datetime
import json
from enum import Enum

from kinit_fast_task.db import DBFactory
from kinit_fast_task.utils.response_code import Status as UtilsStatus
from bson import ObjectId
from bson.errors import InvalidId
from bson.json_util import dumps
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClientSession
from pymongo.results import InsertOneResult, UpdateResult, InsertManyResult
from kinit_fast_task.core import CustomException
from typing import Any
from pydantic import BaseModel as AbstractSchemaModel


class ReturnType(Enum):
    """
    查询数据返回类型
    """

    MODEL = "model"  # 返回结果 Model 对象
    SCHEMA = "schema"  # 返回 Pydantic Schema 序列化对象
    DICT = "dict"  # 返回 Pydantic Schema 序列化后的 Dict


class MongoCrud:
    """
    MongoDB CRUD 基础操作管理器
    博客：https://www.cnblogs.com/aduner/p/13532504.html
    mongodb 官网：https://www.mongodb.com/docs/drivers/motor/
    motor 文档：https://motor.readthedocs.io/en/stable/

    默认使用 AsyncIOMotorDatabase 处理增删改操作
    如果传入 AsyncIOMotorClientSession 则会增加使用 session 处理数据

    传入 session 事务的操作才会执行回滚，未使用 session 事务的操作不支持回滚
    """

    def __init__(
        self,
        session: AsyncIOMotorClientSession | None = None,
        collection: str = None,
        schema: type[AbstractSchemaModel] = None,
        is_object_id: bool = True,
    ):
        """
        初始化 MongoDB CRUD 基础操作管理器
        :param session: mongodb 数据库会话
        :param collection: 集合
        :param schema: 默认序列化 schema
        :param is_object_id: _id 列是否为 ObjectId 格式
        """
        self.db = DBFactory.get_db_instance("mongo").db_getter()
        self.session = session
        self.collection = self.db[collection] if collection else None
        self.simple_out_schema = schema
        self.is_object_id = is_object_id
        self.order_fields = ["desc", "descending"]

    async def get_data(
        self,
        data_id: str = None,
        *,
        v_return_none: bool = False,
        v_schema: AbstractSchemaModel = None,
        v_return_type: ReturnType = ReturnType.MODEL,
        **kwargs,
    ) -> Any:
        """
        获取单个数据，默认使用 ID 查询，否则使用关键词查询

        :param data_id: 数据 ID
        :param v_return_none: 是否返回空 None，否则抛出异常，默认抛出异常
        :param v_schema: 指定使用的序列化对象
        :param v_return_type: 指定数据返回类型，默认返回模型对象
        :param kwargs: 查询参数
        :return:
        """
        if data_id and self.is_object_id:
            kwargs["_id"] = ObjectId(data_id)
        elif data_id:
            kwargs["_id"] = data_id

        params = self.filter_condition(**kwargs)
        data = await self.collection.find_one(params)

        if not data and v_return_none:
            return None
        elif not data:
            raise CustomException(message=f"未查询到编号为：{data_id} 的数据！", code=UtilsStatus.HTTP_404)

        if v_return_type == ReturnType.MODEL or v_return_type == "model":
            return data

        v_schema = v_schema or self.simple_out_schema

        if v_return_type == ReturnType.DICT or v_return_type == "dict":
            return v_schema.model_validate(data).model_dump()
        elif v_return_type == ReturnType.SCHEMA or v_return_type == "schema":
            return v_schema.model_validate(data)
        else:
            raise CustomException("无效的返回值类型！")

    async def create_data(self, data: dict | AbstractSchemaModel) -> InsertOneResult:
        """
        创建数据
        :param data:
        :return:
        """
        data = jsonable_encoder(data)
        data["create_datetime"] = datetime.datetime.now()
        data["update_datetime"] = datetime.datetime.now()
        result = await self.collection.insert_one(data, session=self.session)
        # 判断插入是否成功
        if result.acknowledged:
            return result
        else:
            raise CustomException("新增数据失败")

    async def create_datas(self, datas: list[dict | AbstractSchemaModel]) -> InsertManyResult:
        """
        批量创建数据

        :param datas:
        :return:
        """
        dict_datas = []
        for data in datas:
            item = jsonable_encoder(data)
            item["create_datetime"] = datetime.datetime.now()
            item["update_datetime"] = datetime.datetime.now()
            dict_datas.append(item)
        result = await self.collection.insert_many(dict_datas, session=self.session)
        # 判断插入是否成功
        if result.acknowledged:
            return result
        else:
            raise CustomException("批量新增数据失败")

    async def update_data(self, data_id: str, data: dict | AbstractSchemaModel) -> UpdateResult:
        """
        更新数据
        :param data_id:
        :param data:
        :return:
        """
        data = jsonable_encoder(data)
        data["update_datetime"] = datetime.datetime.now()
        new_data = {"$set": data}
        result = await self.collection.update_one(
            {"_id": ObjectId(data_id) if self.is_object_id else data_id}, new_data, session=self.session
        )

        if result.matched_count > 0:
            return result
        else:
            raise CustomException("未查询到需要更新的数据！")

    async def delete_data(self, data_id: str) -> int:
        """
        删除数据
        :param data_id:
        :return:
        """
        result = await self.collection.delete_one(
            {"_id": ObjectId(data_id) if self.is_object_id else data_id}, session=self.session
        )

        if result.deleted_count > 0:
            return result.deleted_count
        else:
            raise CustomException("未查询到需要删除的数据！")

    async def get_datas(
        self,
        *,
        page: int = 1,
        limit: int = 10,
        v_schema: type[AbstractSchemaModel] = None,
        v_order: str = None,
        v_order_field: str = None,
        v_return_type: ReturnType = ReturnType.MODEL,
        **kwargs,
    ) -> Any:
        """
        使用 find() 要查询的一组文档。 find() 没有I / O，也不需要 await 表达式。它只是创建一个 AsyncIOMotorCursor 实例
        当您调用 to_list() 或为循环执行异步时 (async for) ，查询实际上是在服务器上执行的。
        :param page:
        :param limit:
        :param v_schema:
        :param v_order:
        :param v_order_field:
        :param v_return_type: 指定数据返回类型，默认返回模型对象
        :param kwargs:
        :return:
        """

        params = self.filter_condition(**kwargs)
        cursor = self.collection.find(params)

        if v_order or v_order_field:
            v_order_field = v_order_field if v_order_field else "create_datetime"
            v_order = -1 if v_order in self.order_fields else 1
            cursor.sort(v_order_field, v_order)

        if limit != 0:
            # 对查询应用排序(sort)，跳过(skip)或限制(limit)
            cursor.skip((page - 1) * limit).limit(limit)

        result = []
        async for row in cursor:
            data = json.loads(dumps(row))
            result.append(data)

        if not result or v_return_type == ReturnType.MODEL or v_return_type == "model":
            return result

        v_schema = v_schema or self.simple_out_schema

        if v_return_type == ReturnType.DICT or v_return_type == "dict":
            return [v_schema.model_validate(obj).model_dump() for obj in result]
        elif v_return_type == ReturnType.SCHEMA or v_return_type == "schema":
            return [v_schema.model_validate(obj) for obj in result]
        else:
            raise CustomException("无效的返回值类型！")

    async def get_count(self, **kwargs) -> int:
        """
        获取统计数据
        :param kwargs:
        :return:
        """
        params = self.filter_condition(**kwargs)
        return await self.collection.count_documents(params)

    def filter_condition(self, **kwargs):
        """
        过滤条件
        :param kwargs:
        :return:
        """
        params = {}
        for k, v in kwargs.items():
            if not v:
                continue
            elif isinstance(v, tuple):
                if v[0] == "like" and v[1]:
                    params[k] = {"$regex": v[1]}
                elif v[0] == "between" and len(v[1]) == 2:
                    params[k] = {"$gte": f"{v[1][0]} 00:00:00", "$lt": f"{v[1][1]} 23:59:59"}
                elif v[0] == "ObjectId" and v[1]:
                    try:
                        params[k] = ObjectId(v[1])
                    except InvalidId as exc:
                        raise CustomException(f"{self}.filter_condition，过滤失败，任务编号格式不正确！") from exc
            else:
                params[k] = v
        return params

    def __str__(self):
        return self.__class__.__name__
