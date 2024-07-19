# @Version        : 1.0
# @Create Time    : 2024/7/19
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息


from fastapi import APIRouter

from kinit_fast_task.utils.response import RestfulResponse, ResponseSchema
from kinit_fast_task.utils.storage import StorageFactory

from kinit_fast_task.celery_worker import celery_app

router = APIRouter(prefix="/system/task", tags=["系统任务管理"])


@router.post("/example/create", response_model=ResponseSchema[str], summary="创建示例任务")
async def example_create():
    celery_app.send_task()
    return RestfulResponse.success(data=result)
