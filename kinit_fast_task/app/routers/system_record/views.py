# @Version        : 1.0
# @Create Time    : 2024/05/17 14:37
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 路由，视图文件

from fastapi import APIRouter, Depends

from kinit_fast_task.app.cruds.base.mongo import ReturnType
from kinit_fast_task.app.routers.scheduler_task.params import PageParams
from kinit_fast_task.utils.response import RestfulResponse, PageResponseSchema
from kinit_fast_task.app.schemas import record_operation_schema
from kinit_fast_task.app.cruds.record_operation_crud import OperationCURD

router = APIRouter(prefix="/system/record", tags=["系统记录管理"])


@router.get(
    "/operation/list/query",
    response_model=PageResponseSchema[list[record_operation_schema.OperationSimpleOutSchema]],
    summary="获取系统操作记录列表",
)
async def operation_list_query(params: PageParams = Depends()):
    """
    可以在 kinit_fast_task/config.py:SystemSettings.OPERATION_LOG_RECORD 中选择开启或关闭系统操作记录功能
    """
    datas = await OperationCURD().get_datas(**params.dict(), v_return_type=ReturnType.DICT)
    total = await OperationCURD().get_count(**params.to_count())
    return RestfulResponse.success(data=datas, total=total, page=params.page, limit=params.limit)
