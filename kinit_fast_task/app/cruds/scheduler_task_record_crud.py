# @Version        : 1.0
# @Update Time    : 2024/5/18 14:48
# @File           : scheduler_task_record.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息


from motor.motor_asyncio import AsyncIOMotorClientSession
from kinit_fast_task.app.cruds.base.mongo import MongoCrud
from kinit_fast_task.app.schemas import scheduler_task_record_schema


class SchedulerTaskRecordCURD(MongoCrud):
    def __init__(self, session: AsyncIOMotorClientSession | None = None):
        super().__init__()
        self.session = session
        self.collection = self.db["scheduler_task_record"]
        self.simple_out_schema = scheduler_task_record_schema.TaskRecordSimpleOutSchema
        self.is_object_id = True
