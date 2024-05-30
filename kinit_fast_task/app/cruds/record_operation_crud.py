# @Version        : 1.0
# @Create Time    : 2021/10/18 22:18
# @File           : crud.py
# @IDE            : PyCharm
# @Desc           : 数据库 增删改查操作

from kinit_fast_task.app.cruds.base.mongo import MongoCrud
from kinit_fast_task.app.schemas import record_operation_schema
from motor.motor_asyncio import AsyncIOMotorClientSession


class OperationCURD(MongoCrud):
    def __init__(self, session: AsyncIOMotorClientSession | None = None):
        super().__init__()
        self.session = session
        self.collection = self.db["record_operation"]
        self.simple_out_schema = record_operation_schema.OperationSimpleOutSchema
        self.is_object_id = True
