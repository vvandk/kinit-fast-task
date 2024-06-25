#!/usr/bin/python
# @version        : 1.0
# @Create Time    : 2023/6/21 10:10
# @File           : main.py
# @IDE            : PyCharm
# @desc           : 调度任务

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from kinit_fast_task.core import CustomException
from kinit_fast_task.task.utils.scheduler import Scheduler, scheduler_active
from kinit_fast_task.core import log
from kinit_fast_task.task.schema import JobExecStrategy, AddTask
from kinit_fast_task.config import settings
from kinit_fast_task.utils.singleton import Singleton


class ScheduledTask(Scheduler, metaclass=Singleton):
    def __init__(self):
        super().__init__()

    @scheduler_active
    async def add_job(self, job_params: AddTask) -> None:
        """
        添加定时任务
        :param job_params: 执行参数
        :return:
        """
        task_id = job_params.task_id
        exec_strategy = job_params.exec_strategy
        error_info = None
        try:
            if exec_strategy == JobExecStrategy.interval:
                self.add_interval_job(**job_params.model_dump())
            elif exec_strategy == JobExecStrategy.cron:
                self.add_cron_job(**job_params.model_dump())
            elif exec_strategy == JobExecStrategy.date:
                self.add_date_job(**job_params.model_dump())
            elif exec_strategy == JobExecStrategy.once:
                self.run_job(**job_params.model_dump())
            else:
                raise ValueError("无效的触发器")
        except ConflictingIdError:
            # 任务编号已存在，重复添加报错
            error_info = "任务编号已存在"
        except ValueError as e:
            error_info = e.__str__()

        if error_info:
            log.error(f"任务编号：{task_id}，报错：{error_info}")
            await self.add_task_error_record(task_id, error_info)

    def get_scheduler(self) -> AsyncIOScheduler:
        """
        获取 APScheduler AsyncIOScheduler 实例

        :return:
        """
        scheduler_ins = self._get_scheduler_instance()
        if scheduler_ins is None:
            raise CustomException("未成功开启 Scheduled Task 引擎！")
        return scheduler_ins


scheduled_task = ScheduledTask()
if settings.task.TASK_ENABLE:
    scheduled_task.start_scheduler()
