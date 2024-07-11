# @Version        : 1.0
# @Update Time    : 2024/5/18 14:46
# @File           : scheduler_task_list.py
# @IDE            : PyCharm
# @Desc           : 调度任务


from motor.motor_asyncio import AsyncIOMotorClientSession
from kinit_fast_task.app.cruds.base.mongo import MongoCrud, ReturnType
from kinit_fast_task.app.schemas import scheduler_task_list_schema
from kinit_fast_task.core import CustomException
from kinit_fast_task.task.schema import AddTask
from kinit_fast_task.task.main import scheduled_task


class SchedulerTaskListCURD(MongoCrud):
    def __init__(self, session: AsyncIOMotorClientSession | None = None):
        super().__init__()
        self.session = session
        self.collection = self.db["scheduler_task_list"]
        self.simple_out_schema = scheduler_task_list_schema.TaskSimpleOutSchema
        self.is_object_id = True

    async def start_task(self, data_id: str):
        """
        开启任务
        :param data_id: 任务编号
        :return:
        """
        obj: scheduler_task_list_schema.TaskSimpleOutSchema = await self.get_data(
            data_id, v_return_type=ReturnType.SCHEMA
        )
        if not obj.is_active:
            await self.update_data(data_id, {"is_active": True})
            task_data = AddTask(task_id=data_id, **obj.model_dump(exclude={"name", "is_active"}))
            await scheduled_task.add_job(task_data)
            return "任务开启成功"
        return "该任务已处于运行状态"

    async def stop_task(self, data_id: str):
        """
        暂停任务
        """
        obj: scheduler_task_list_schema.TaskSimpleOutSchema = await self.get_data(
            data_id, v_return_type=ReturnType.SCHEMA
        )
        if obj.is_active:
            await self.update_data(data_id, {"is_active": False})
            scheduled_task.remove_job(data_id)
            return "任务暂停成功"
        return "该任务不处于运行状态"

    async def add_task(self, data: scheduler_task_list_schema.TaskCreateSchema) -> str:
        """
        创建任务，添加任务
        """
        obj = await self.create_data(data)
        if data.is_active:
            task_data = AddTask(task_id=str(obj.inserted_id), **data.model_dump(exclude={"name", "is_active"}))
            await scheduled_task.add_job(task_data)
        return "任务添加成功"

    async def delete_task(self, data_id: str) -> str:
        """
        删除任务
        """
        obj: scheduler_task_list_schema.TaskSimpleOutSchema = await self.get_data(
            data_id, v_return_type=ReturnType.SCHEMA
        )
        if obj.is_active:
            raise CustomException("请暂停任务后再删除！")
        await self.delete_data(data_id)
        return "任务删除成功"
