#!/usr/bin/python
# @version        : 1.0
# @Create Time    : 2023/6/21 14:42
# @File           : listener.py
# @IDE            : PyCharm
# @desc           : 简要说明
import asyncio
import datetime
import json

import bson
from apscheduler.events import JobExecutionEvent
from kinit_fast_task.task.utils.scheduler_task_record import SchedulerTaskRecordCURD
from kinit_fast_task.task.utils.scheduler_task_list import SchedulerTaskListCURD
import pytz
from kinit_fast_task.utils import log
from kinit_fast_task.app.cruds.base.mongo import ReturnType


def async_listener_decorator(async_func):
    """
    使异步事件监听器可以在上下文中被调用

    :param async_func:
    :return:
    """

    def wrapper(event):
        asyncio.create_task(async_func(event))

    return wrapper


async def before_job_execution(event: JobExecutionEvent):
    # print("在执行定时任务前执行的代码...")
    shanghai_tz = pytz.timezone("Asia/Shanghai")
    start_datetime: datetime.datetime = event.scheduled_run_time.astimezone(shanghai_tz)
    end_datetime = datetime.datetime.now(shanghai_tz)
    process_time = (end_datetime - start_datetime).total_seconds()
    task_id = event.job_id
    if "-temp-" in task_id:
        task_id = task_id.split("-")[0]
    # print("任务标识符，关联任务列表id字段：", event.task_id)
    # print("任务开始执行时间：", start_time.strftime("%Y-%m-%d %H:%M:%S"))
    # print("任务执行完成时间：", end_time.strftime("%Y-%m-%d %H:%M:%S"))
    # print("任务耗时（秒）：", process_time)
    # print("任务返回值：", event.retval)
    # print("异常信息：", event.exception)
    # print("堆栈跟踪：", event.traceback)

    result = {
        "task_id": task_id,
        "start_datetime": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "end_datetime": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        "process_time": process_time,
        "retval": json.dumps(event.retval),
        "exception": json.dumps(event.exception),
        "traceback": json.dumps(event.traceback),
        "job_class": None,
        "job_params": None,
        "name": "null",
        "group": "null",
        "exec_strategy": None,
        "expression": None,
    }

    try:
        task = await SchedulerTaskListCURD().get_data(task_id, v_return_type=ReturnType.SCHEMA)
        result["job_class"] = task.job_class
        result["job_params"] = task.job_params
        result["name"] = task.name
        result["group"] = task.group
        result["exec_strategy"] = task.exec_strategy
        result["expression"] = task.expression
    except ValueError as e:
        result["exception"] = str(e)
        log.error(f"任务编号：{event.job_id}，报错：{e}")
    except bson.errors.InvalidId:
        result["exception"] = "任务列表中无该任务编号"
        log.error(f"任务编号：{event.job_id}，报错：任务列表中无该任务编号")
    await SchedulerTaskRecordCURD().create_data(result)
