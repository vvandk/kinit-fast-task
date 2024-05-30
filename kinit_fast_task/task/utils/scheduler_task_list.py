# @Version        : 1.0
# @Update Time    : 2024/5/18 14:46
# @File           : scheduler_task_list.py
# @IDE            : PyCharm
# @Desc           : 调度任务


from motor.motor_asyncio import AsyncIOMotorClientSession
from kinit_fast_task.app.cruds.base.mongo import MongoCrud
from kinit_fast_task.app.schemas import scheduler_task_list_schema


class SchedulerTaskListCURD(MongoCrud):
    def __init__(self, session: AsyncIOMotorClientSession | None = None):
        super().__init__()
        self.session = session
        self.collection = self.db["scheduler_task_list"]
        self.simple_out_schema = scheduler_task_list_schema.TaskSimpleOutSchema
        self.is_object_id = True
