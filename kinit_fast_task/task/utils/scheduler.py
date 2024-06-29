#!/usr/bin/python
# @version        : 1.0
# @Create Time    : 2023/6/21 10:10
# @File           : scheduler.py
# @IDE            : PyCharm
# @desc           : 调度任务基础功能

import datetime
import importlib
import json
import re
from types import ModuleType

from apscheduler.jobstores.base import JobLookupError
from apscheduler.jobstores.mongodb import MongoClient, MongoDBJobStore
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from pytz import timezone as pytz_timezone

from .listener import before_job_execution, async_listener_decorator
from apscheduler.events import EVENT_JOB_EXECUTED
from kinit_fast_task.config import settings
from kinit_fast_task.app.cruds.base.mongo import ReturnType
from kinit_fast_task.task.utils.scheduler_task_record import SchedulerTaskRecordCURD
from kinit_fast_task.task.utils.scheduler_task_list import SchedulerTaskListCURD
from kinit_fast_task.utils import log
from kinit_fast_task.core import CustomException
from functools import wraps
from typing import Any
from collections.abc import Callable


def scheduler_active(func: Callable) -> Callable:
    """
    用于检测定时任务调度器状态是否正常
    如果在非正常情况下调用了装饰方法，那么会直接抛出异常

    非正常情况：

        1. 项目配置中未开启定时任务引擎：kinit_fast_task/config.py:TaskSettings.TASK_ENABLE
        2. 任务实例中未成功启用 scheduler
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        if not settings.task.TASK_ENABLE:
            raise CustomException("项目配置中未开启定时任务引擎：kinit_fast_task/config.py:TaskSettings.TASK_ENABLE")
        elif self._get_scheduler_instance() is None:
            raise CustomException("未成功开启 Scheduled Task 引擎！")
        return func(self, *args, **kwargs)

    return wrapper


class Scheduler:
    TASK_DIR = settings.task.TASK_PAG
    COLLECTION = settings.task.SCHEDULER_TASK_JOBS

    def __init__(self):
        self.__scheduler = None

    def start_scheduler(self, listener: bool = True) -> None:
        """
        创建并启动调度器

        :param listener: 是否注册事件监听器
        :return:
        """
        self.__scheduler = AsyncIOScheduler()
        self.__scheduler.configure(
            job_defaults={
                "misfire_grace_time": None,  # 错过的任务仍然保持执行
                "coalesce": True,  # 合并错过的任务，只执行一次
            },
            timezone=pytz_timezone("Asia/Shanghai"),  # 设置时区
        )
        if listener:
            # 注册事件监听器
            self.__scheduler.add_listener(async_listener_decorator(before_job_execution), EVENT_JOB_EXECUTED)
        self.__scheduler.add_jobstore(self.__get_mongodb_job_store())
        self.__scheduler.start()

    def __get_mongodb_job_store(self) -> MongoDBJobStore:
        """
        获取 MongoDB Job Store

        APScheduler 不支持异步 mongodb 数据库存储
        所以这里会使用 apscheduler 内部实例化 mongodb client
        :return: MongoDB Job Store
        """
        db_name = dict(settings.db.MONGO_DB_URL.query_params()).get("authSource")
        return MongoDBJobStore(database=db_name, collection=self.COLLECTION, client=self.__get_mongodb_client())

    @staticmethod
    def __get_mongodb_client() -> MongoClient:
        """
        获取 MongoDB Client

        :return: MongoDB Client
        """
        return MongoClient(settings.db.MONGO_DB_URL.unicode_string())

    def _get_scheduler_instance(self) -> AsyncIOScheduler | None:
        """
        获取 APScheduler AsyncIOScheduler 实例

        :return:
        """
        return self.__scheduler

    @scheduler_active
    def __add_reflection_scheduler_job(
        self,
        *,
        job_class: str,
        job_params: str,
        trigger: CronTrigger | DateTrigger | IntervalTrigger | None,
        task_id: str = None,
    ) -> Job:
        """
        通过反射任务实体类，添加到调度任务

        :param job_class: 任务执行实体类
        :param job_params: 任务执行实体类参数
        :param trigger: 触发条件
        :param task_id: 任务编号
        :return:
        """
        job_class = self.__import_module(job_class, job_params)
        if job_class:
            return self.__scheduler.add_job(job_class.main, trigger=trigger, id=task_id)
        else:
            raise CustomException(f"添加任务失败，未找到定义的任务：{job_class}")

    @scheduler_active
    def add_cron_job(
        self,
        *,
        job_class: str,
        job_params: str,
        expression: str,
        start_datetime: str | datetime.datetime = None,
        end_datetime: str | datetime.datetime = None,
        timezone: str = "Asia/Shanghai",
        task_id: str = None,
        **kwargs,
    ) -> Job:
        """
        通过 cron 表达式添加定时任务

        :param job_class: 任务执行实体类
        :param job_params: 任务执行实体类参数
        :param expression: cron 表达式，六位或七位，分别表示秒、分钟、小时、天、月、星期几、年
        :param start_datetime: 触发器的开始日期时间。可选参数，默认为 None。
        :param end_datetime: 触发器的结束日期时间。可选参数，默认为 None。
        :param timezone: 时区，表示触发器应用的时区。可选参数，默认为 None，使用上海默认时区。
        :param task_id: 任务编号
        :return:
        """
        second, minute, hour, day, month, day_of_week, year = self.__parse_cron_expression(expression)
        trigger = CronTrigger(
            second=second,
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            year=year,
            start_date=start_datetime,
            end_date=end_datetime,
            timezone=timezone,
        )
        return self.__add_reflection_scheduler_job(
            job_class=job_class, job_params=job_params, trigger=trigger, task_id=task_id
        )

    @scheduler_active
    def add_date_job(self, *, job_class: str, job_params: str, expression: str, task_id: str = None, **kwargs) -> Job:
        """
        date触发器用于在指定的日期和时间触发一次任务。它适用于需要在特定时间点执行一次的任务，例如执行一次备份操作

        :param job_class: 任务执行实体类
        :param job_params: 任务执行实体类参数
        :param expression: date
        :param task_id: 任务编号
        :return:
        """  # noqa E501
        trigger = DateTrigger(run_date=expression)
        return self.__add_reflection_scheduler_job(
            job_class=job_class, job_params=job_params, trigger=trigger, task_id=task_id
        )

    @scheduler_active
    def add_interval_job(
        self,
        *,
        job_class: str,
        job_params: str,
        expression: str,
        start_datetime: str | datetime.datetime = None,
        end_datetime: str | datetime.datetime = None,
        timezone: str = "Asia/Shanghai",
        jitter: int = None,
        task_id: str = None,
        **kwargs,
    ) -> Job:
        """
        date触发器用于在指定的日期和时间触发一次任务。它适用于需要在特定时间点执行一次的任务，例如执行一次备份操作。

        :param job_class: 任务执行实体类
        :param job_params: 任务执行实体类参数
        :param expression：interval 表达式，分别为：秒、分、时、天、周，例如，设置 10 * * * * 表示每隔 10 秒执行一次任务。
        :param start_datetime: 表示任务的结束时间，可以设置为 datetime 对象或者字符串。
                         例如，设置 end_date='2023-06-23 10:00:00' 表示任务在 2023 年 6 月 23 日 10 点结束。
        :param end_datetime: 表示任务的起始时间，可以设置为 datetime 对象或者字符串。
                           例如，设置 start_date='2023-06-22 10:00:00' 表示从 2023 年 6 月 22 日 10 点开始执行任务。
        :param timezone：表示时区，可以设置为字符串或 pytz.timezone 对象。例如，设置 timezone='Asia/Shanghai' 表示使用上海时区。
        :param jitter：表示时间抖动，可以设置为整数或浮点数。例如，设置 jitter=2 表示任务的执行时间会在原定时间上随机增加 0~2 秒的时间抖动。
        :param task_id: 任务编号
        :return:
        """  # noqa E501
        second, minute, hour, day, week = self.__parse_interval_expression(expression)
        trigger = IntervalTrigger(
            weeks=week,
            days=day,
            hours=hour,
            minutes=minute,
            seconds=second,
            start_date=start_datetime,
            end_date=end_datetime,
            timezone=timezone,
            jitter=jitter,
        )
        return self.__add_reflection_scheduler_job(
            job_class=job_class, job_params=job_params, trigger=trigger, task_id=task_id
        )

    @scheduler_active
    def run_job(self, job_class: str, job_params: str, task_id: str = None, **kwargs) -> None:
        """
        立即执行一次任务

        :param job_class: 类路径
        :param job_params: 任务执行实体类参数
        :param task_id: 任务编号
        :return:
        """
        return self.__add_reflection_scheduler_job(
            job_class=job_class, job_params=job_params, trigger=None, task_id=task_id
        )

    @scheduler_active
    def remove_job(self, task_id: str) -> None:
        """
        删除任务

        :param task_id: 任务编号
        :return:
        """
        try:
            self.__scheduler.remove_job(task_id)
        except JobLookupError as e:
            raise ValueError(f"删除任务失败, 报错：{e}")

    @scheduler_active
    def get_job(self, task_id: str) -> Job:
        """
        获取任务

        :param task_id: 任务编号
        :return:
        """
        return self.__scheduler.get_job(task_id)

    @scheduler_active
    def has_job(self, task_id: str) -> bool:
        """
        判断任务是否存在

        :param task_id: 任务编号
        :return:
        """
        if self.get_job(task_id):
            return True
        else:
            return False

    @scheduler_active
    def get_jobs(self) -> list[Job]:
        """
        获取所有任务

        :return:
        """
        return self.__scheduler.get_jobs()

    @scheduler_active
    def get_job_task_ids(self) -> list[str]:
        """
        获取所有任务编号

        :return:
        """
        jobs = self.__scheduler.get_jobs()
        return [job.id for job in jobs]

    def __import_module(self, job_class: str, job_params: str) -> ModuleType:
        """
        反射模块

        :param job_class: 任务执行实体类, 示例：test.
        :param job_params: 任务执行实体类参数
        :return: 类实例
        """
        module_pag = self.TASK_DIR + "." + job_class[0 : job_class.rindex(".")]
        module_class = job_class[job_class.rindex(".") + 1 :]
        try:
            # 动态导入模块
            pag = importlib.import_module(module_pag)
            return getattr(pag, module_class)(**json.loads(job_params))
        except ModuleNotFoundError:
            raise ValueError(f"未找到该模块：{module_pag}")
        except AttributeError:
            raise ValueError(f"未找到该模块下的方法：{module_class}")
        except TypeError as e:
            raise ValueError(f"参数传递错误：{job_params}, 没有参数时需要为: {{}}, 详情：{e}")

    @staticmethod
    def __parse_cron_expression(expression: str) -> tuple:
        """
        解析 cron 表达式

        :param expression: cron 表达式，支持六位或七位，分别表示秒、分钟、小时、天、月、星期几、年
        :return: 解析后的秒、分钟、小时、天、月、星期几、年字段的元组
        """
        fields = expression.strip().split()

        if len(fields) not in (6, 7):
            raise ValueError("无效的 Cron 表达式")

        parsed_fields = [None if field in ("*", "?") else field for field in fields]
        if len(fields) == 6:
            parsed_fields.append(None)

        return tuple(parsed_fields)

    @staticmethod
    def __parse_interval_expression(expression: str) -> tuple:
        """
        解析 interval 表达式

        :param expression: interval 表达式，分别为：秒、分、时、天、周，例如，设置 10 * * * * 表示每隔 10 秒执行一次任务。
        :return:
        """  # noqa E501
        # 将传入的 interval 表达式拆分为不同的字段
        fields = expression.strip().split()

        if len(fields) != 5:
            raise ValueError("无效的 interval 表达式")

        parsed_fields = [int(field) if field != "*" else 0 for field in fields]
        return tuple(parsed_fields)

    @classmethod
    def __parse_string_to_class(cls, expression: str) -> tuple:
        """
        使用正则表达式匹配类路径和参数

        :param expression: 表达式
        :return:
        """
        pattern = r"([\w.]+)(?:\((.*)\))?"
        match = re.match(pattern, expression)

        if match:
            class_path = match.group(1)
            arguments = match.group(2)

            if arguments:
                arguments = cls.__parse_arguments(arguments)
            else:
                arguments = []

            return class_path, arguments

        return None, None

    @staticmethod
    def __parse_arguments(args_str) -> list:
        """
        解析类路径参数字符串

        :param args_str: 类参数字符串
        :return:
        """
        # 更新的正则表达式
        pattern = r'\'([^\']*)\'|"([^"]*)"|(\d+\.\d+)|(\d+)|([Tt]rue|[Ff]alse)'

        matches = re.findall(pattern, args_str)

        # 将匹配结果整理为一个扁平化的列表
        flattened_matches = [item for sublist in matches for item in sublist if item]

        # 解析匹配结果
        parsed_matches = []
        for match in flattened_matches:
            if match.lower() == "true":
                parsed_matches.append(True)
            elif match.lower() == "false":
                parsed_matches.append(False)
            elif re.match(r"^\d+\.\d+$", match):  # 检查是否是小数
                parsed_matches.append(float(match))
            elif re.match(r"^\d+$", match):  # 检查是否是整数
                parsed_matches.append(int(match))
            else:  # 默认作为字符串处理
                parsed_matches.append(match)

        return parsed_matches

    @staticmethod
    async def add_task_error_record(task_id: str, error_info: str) -> None:
        """
        添加任务失败记录，并且将任务状态改为 False

        :param task_id: 任务编号
        :param error_info: 报错信息
        :return:
        """
        try:
            await SchedulerTaskListCURD().update_data(task_id, {"is_active": False})
            task = await SchedulerTaskListCURD().get_data(task_id, v_return_type=ReturnType.SCHEMA)
            # 执行你想要在任务执行前执行的代码
            result = {
                "job_id": task_id,
                "job_class": task.job_class,
                "name": task.name,
                "group": task.group,
                "exec_strategy": task.exec_strategy,
                "expression": task.expression,
                "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "process_time": 0,
                "retval": "任务添加失败",
                "exception": error_info,
                "traceback": None,
            }
            await SchedulerTaskRecordCURD().create_data(result)
        except ValueError as e:
            log.error(f"任务编号：{task_id}, 报错：{e}")

    def shutdown(self) -> None:
        """
        关闭调度器
        :return:
        """
        if self.__scheduler:
            self.__scheduler.shutdown()
