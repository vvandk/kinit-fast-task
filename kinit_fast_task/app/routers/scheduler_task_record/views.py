# @Version        : 1.0
# @Create Time    : 2024/05/17 14:37
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 路由，视图文件
from kinit_fast_task.db.database_factory import DBFactory
from motor.motor_asyncio import AsyncIOMotorClientSession
from fastapi import APIRouter, Depends

from kinit_fast_task.app.cruds.base.mongo import ReturnType
from kinit_fast_task.app.routers.scheduler_task.params import PageParams
from kinit_fast_task.utils.response import RestfulResponse, PageResponseSchema
from kinit_fast_task.app.schemas import scheduler_task_record_schema
from kinit_fast_task.app.cruds.scheduler_task_record_crud import SchedulerTaskRecordCURD

router = APIRouter(prefix="/scheduler/task/record", tags=["调度任务执行记录管理"])


@router.get(
    "/list/query",
    response_model=PageResponseSchema[list[scheduler_task_record_schema.TaskRecordSimpleOutSchema]],
    summary="获取任务执行记录列表",
)
async def list_query(
    params: PageParams = Depends(),
    session: AsyncIOMotorClientSession = Depends(DBFactory.get_db_instance("mongo").db_transaction_getter),
):
    datas = await SchedulerTaskRecordCURD(session).get_datas(**params.dict(), v_return_type=ReturnType.DICT)
    total = await SchedulerTaskRecordCURD(session).get_count(**params.to_count())
    return RestfulResponse.success(data=datas, total=total, page=params.page, limit=params.limit)
