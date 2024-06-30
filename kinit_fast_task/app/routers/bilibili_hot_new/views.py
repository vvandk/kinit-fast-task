# @Version        : 1.0
# @Create Time    : 2024/5/22 下午3:54
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 任务示例

from kinit_fast_task.db import DBFactory
from motor.motor_asyncio import AsyncIOMotorClientSession
from fastapi import APIRouter, Depends, Query

from kinit_fast_task.task.main import scheduled_task
from kinit_fast_task.utils.response import RestfulResponse, ResponseSchema
from kinit_fast_task.app.cruds.bilibili_hot_new_crud import BilibiliHotNewListCURD
from typing import Literal

from apscheduler.jobstores.base import JobLookupError

router = APIRouter(prefix="/bilibili/hot/new", tags=["bilibili 热搜数据"])


@router.post("/task/create", response_model=ResponseSchema[str], summary="创建任务")
async def task_create(
    session: AsyncIOMotorClientSession = Depends(DBFactory.get_db_instance("mongo").db_transaction_getter),
):
    """
    创建获取 bilibili 热搜数据任务
    """
    await BilibiliHotNewListCURD(session=session).add_task()
    return RestfulResponse.success()


@router.post(
    "/mongo/transaction/example/create",
    response_model=ResponseSchema[str],
    summary="默认使用 Mongo 事务处理",
    tags=["MongoDB 事务"],
)
async def mongo_transaction_example_create(
    session: AsyncIOMotorClientSession = Depends(DBFactory.get_db_instance("mongo").db_transaction_getter),
):
    """
    默认使用 Mongo 事务处理
    """
    await BilibiliHotNewListCURD(session).mongo_transaction_example()
    return RestfulResponse.success()


@router.post(
    "/mongo/no/transaction/example/create",
    response_model=ResponseSchema[str],
    summary="不使用 Mongo 事务处理",
    tags=["MongoDB 事务"],
)
async def mongo_no_transaction_example_create():
    """
    不使用 Mongo 事务处理
    """
    await BilibiliHotNewListCURD().mongo_no_transaction_example()
    return RestfulResponse.success()


@router.post(
    "/mongo/transaction/no/transaction/example/create",
    response_model=ResponseSchema[str],
    summary="使用与不使用事务示例",
    tags=["MongoDB 事务"],
)
async def mongo_transaction_no_transaction_example_create(
    session: AsyncIOMotorClientSession = Depends(DBFactory.get_db_instance("mongo").db_transaction_getter),
):
    """
    使用与不使用事务示例
    """
    await BilibiliHotNewListCURD(session).mongo_transaction_no_transaction_example()
    return RestfulResponse.success()


@router.post(
    "/apscheduler/example/create",
    response_model=ResponseSchema[str],
    summary="APScheduler 实例直接调用示例, 添加任务",
    tags=["APScheduler 实例"],
)
async def apscheduler_example_create(task_number: Literal["01", "02", "03"] = Query(..., description="执行指定任务")):
    """
    APScheduler 实例直接调用示例, 添加任务

    直接使用 APScheduler 实例添加定时任务时：

        1. 该任务不会存入 scheduler_task_list 任务列表中
        2. 但是任务仍然会创建 scheduler_task_record 任务执行记录
    """
    await BilibiliHotNewListCURD().apscheduler_example(task_number)
    return RestfulResponse.success()


@router.delete(
    "/apscheduler/delete/example/delete",
    response_model=ResponseSchema[str],
    summary="APScheduler 实例直接调用示例, 删除工作任务",
    tags=["APScheduler 实例"],
)
async def apscheduler_delete_example_delete(job_id: str = Query(..., description="删除指定工作任务")):
    """
    APScheduler 实例直接调用示例, 删除工作任务
    """
    scheduler_ins = scheduled_task.get_scheduler()
    try:
        scheduler_ins.remove_job(job_id)
        return RestfulResponse.success()
    except JobLookupError:
        return RestfulResponse.error(f"无 {job_id} 工作任务编号")
