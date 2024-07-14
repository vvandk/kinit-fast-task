# @Version        : 1.0
# @Update Time    : 2024/7/14
# @File           : example.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息

from celery import shared_task
from kinit_fast_task.utils import log
import time


@shared_task(name='my_task')
def my_task(params: dict):
    task_log = log.create_task("my_task.log")
    task_log.info("my_task 任务成功启动, 接收参数为", params)
    while True:
        task_log.info("任务已开始")
        time.sleep(5)
        task_log.info("任务已经完成")
