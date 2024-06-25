# @Version        : 1.0
# @Create Time    : 2024/5/22 下午3:54
# @File           : bilibili_hot_new.py
# @IDE            : PyCharm
# @Desc           :
from typing import Literal

from kinit_fast_task.app.schemas import scheduler_task_list_schema
from kinit_fast_task.core import CustomException
from motor.motor_asyncio import AsyncIOMotorClientSession
from kinit_fast_task.app.cruds.base.mongo import MongoCrud
from kinit_fast_task.app.schemas import bilibili_hot_new_schema
from kinit_fast_task.core import log
from kinit_fast_task.task.schema import AddTask, JobExecStrategy
from kinit_fast_task.task.main import scheduled_task
from kinit_fast_task.app.cruds.scheduler_task_list_crud import SchedulerTaskListCURD


class BilibiliHotNewListCURD(MongoCrud):
    def __init__(self, session: AsyncIOMotorClientSession | None = None):
        super().__init__()
        self.session = session
        self.collection = self.db["bilibili_hot_new"]
        self.simple_out_schema = bilibili_hot_new_schema.BilibiliHotNewSimpleOutSchema
        self.is_object_id = True

    async def add_task(self):
        """
        创建获取 bilibili 热搜数据任务

        :return:
        """
        task_data = scheduler_task_list_schema.TaskCreateSchema(
            name="获取 bilibili 热搜数据",
            group="热搜",
            job_class="bilibili_hot_new.main.bilibili_hot_new_schema.BilibiliHotNewSchema",
            job_params={},
            exec_strategy=JobExecStrategy.once,
            is_active=True,
        )
        obj = await SchedulerTaskListCURD(self.session).create_data(task_data)

        job_params = {"task_id": str(obj.inserted_id)}
        add_task_data = AddTask(
            task_id=str(obj.inserted_id),
            job_params=job_params,
            **task_data.model_dump(exclude={"name", "is_active", "job_params"}),
        )
        await scheduled_task.add_job(add_task_data)
        return "任务添加成功"

    async def mongo_transaction_example(self):
        """
        默认使用 Mongo 事务处理

        :return:
        """
        # 因在路由中调用该方法时，传入了事务 session，所以以下操作默认会通过事务 session 处理
        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据1", heat="50w", link="https://bilibili.com"
        )
        await self.create_data(data)

        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据2", heat="22w", link="https://bilibili.com"
        )
        await self.create_data(data)

        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据3", heat="100w", link="https://bilibili.com"
        )
        await self.collection.insert_one(data.model_dump(), session=self.session)

        raise CustomException("以上操作使用了事务 session, 所以这里抛出异常后, 以上的操作都会回滚, 不会新增到数据库中")

    async def mongo_no_transaction_example(self):
        """
        不使用 Mongo 事务处理

        :return:
        """
        # 因在路由中调用该方法时，未传入事务 session，所以以下操作不会通过事务 session 处理
        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据1", heat="88w", link="https://bilibili.com"
        )
        await self.create_data(data)

        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据2", heat="22w", link="https://bilibili.com"
        )
        await self.create_data(data)

        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据3", heat="100w", link="https://bilibili.com"
        )
        await self.collection.insert_one(data.model_dump())

        raise CustomException("以上操作未使用事务 session, 所以这里抛出异常后, 数据仍然会新增到数据库中")

    async def mongo_transaction_no_transaction_example(self):
        """
        使用与不使用事务示例

        :return:
        """
        # 在路由中传入了事务 session, 在使用默认操作时会通过事务 session 操作
        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据1", heat="69w", link="https://bilibili.com"
        )
        await self.create_data(data)

        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据2", heat="88w", link="https://bilibili.com"
        )
        await self.create_data(data)

        # 但是通过自行写插入语句时未使用事务 session
        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据3", heat="909w", link="https://bilibili.com"
        )
        await self.collection.insert_one(data.model_dump())

        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="Mongo 事务测试数据4", heat="1000w", link="https://bilibili.com"
        )
        await self.collection.insert_one(data.model_dump())

        raise CustomException(
            "使用父类进行增删改时, 如果存在 session, 那么会默认使用 session 操作, 所以这里只会新增两条数据, 分别为:3, 4"
        )

    @staticmethod
    async def task_example_01():
        """
        任务示例 1

        :return:
        """
        log.info("01 示例任务触发了, 任务编号: task_example_01")
        return "01 execute success"

    @staticmethod
    async def task_example_02():
        """
        任务示例 2

        :return:
        """
        # 经测试，无法使用通过该实例添加任务，因实例中存在无法序列化对象会报错
        # 所以需要在任务中重新实例化 bilibili_hot_new_schema.BilibiliHotNewSchemaListCURD 对象，并创建数据
        # 所以在添加 CRUD 方法任务时，需要使用 staticmethod 或者 classmethod 装饰
        data = bilibili_hot_new_schema.BilibiliHotNewSchema(
            title="APScheduler 实例直接调用示例 02", heat="999w", link="https://bilibili.com"
        )
        await BilibiliHotNewListCURD().create_data(data.model_dump())

        log.info("02 示例任务触发了, 任务编号: task_example_02")
        return "02 execute success"

    async def apscheduler_example(self, task_number: Literal["01", "02", "03"]):
        """
        APScheduler 实例直接调用示例, 添加任务

        :param task_number: 执行指定任务
        :return:
        """
        scheduler_ins = scheduled_task.get_scheduler()
        if task_number == "01":
            # 每 10 秒执行一次 task_example_01
            scheduler_ins.add_job(self.task_example_01, "interval", seconds=10, id="task_example_01")
        elif task_number == "02":
            # 每 20 秒执行一次 task_example_02
            scheduler_ins.add_job(self.task_example_02, "interval", seconds=20, id="task_example_02")
        elif task_number == "03":
            # 每分钟执行一次 task_example_03
            scheduler_ins.add_job(task_example_03, "interval", minutes=1, id="task_example_03")
        return "任务添加成功"


async def task_example_03():
    """
    任务示例 3, 外部函数

    :return:
    """
    data = bilibili_hot_new_schema.BilibiliHotNewSchema(
        title="APScheduler 实例直接调用示例 03", heat="888w", link="https://bilibili.com"
    )
    await BilibiliHotNewListCURD().create_data(data.model_dump())

    log.info("03 示例任务触发了, 任务编号: task_example_03")
    return "03 execute success"
