# @Version        : 1.0
# @Create Time    : 2024/4/22 17:58
# @File           : event.py
# @IDE            : PyCharm
# @Desc           : 全局事件

from fastapi import FastAPI
from kinit_fast_task.db import DBFactory

from kinit_fast_task.utils import log

from kinit_fast_task.task.main import scheduled_task


async def close_db_event(app: FastAPI, status: bool):
    """
    关闭数据库连接事件
    :param app:
    :param status: 用于判断是开始还是结束事件，为 True 说明是开始事件，反着关闭事件
    :return:
    """
    if status:
        log.info("启动项目事件成功执行！")
    else:
        await DBFactory.clear()
        scheduled_task.shutdown()
        log.info("关闭项目事件成功执行！")
