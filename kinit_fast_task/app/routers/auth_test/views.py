# @Version        : 1.0
# @Create Time    : 2024/07/09
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 路由，视图文件

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Body, Query
from kinit_fast_task.utils.response import RestfulResponse, ResponseSchema, PageResponseSchema
from kinit_fast_task.db.database_factory import DBFactory
from kinit_fast_task.app.cruds.auth_test_crud import AuthTestCRUD
from kinit_fast_task.app.schemas import auth_test_schema, DeleteSchema
from .params import PageParams


router = APIRouter(prefix="/auth/test", tags=["测试管理"])


@router.post("/create", response_model=ResponseSchema[str], summary="创建测试")
async def create(
    data: auth_test_schema.AuthTestCreateSchema,
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    return RestfulResponse.success(await AuthTestCRUD(session).create_data(data=data))


@router.post("/update", response_model=ResponseSchema[str], summary="更新测试")
async def update(
    data_id: int = Body(..., description="测试编号"),
    data: auth_test_schema.AuthTestUpdateSchema = Body(..., description="更新内容"),
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    return RestfulResponse.success(await AuthTestCRUD(session).update_data(data_id, data))


@router.post("/delete", response_model=ResponseSchema[str], summary="批量删除测试")
async def delete(
    data: DeleteSchema = Body(..., description="测试编号列表"),
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    await AuthTestCRUD(session).delete_datas(ids=data.data_ids)
    return RestfulResponse.success("删除成功")


@router.get(
    "/list/query",
    response_model=PageResponseSchema[list[auth_test_schema.AuthTestSimpleOutSchema]],
    summary="获取测试列表",
)
async def list_query(
    params: PageParams = Depends(), session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter)
):
    datas = await AuthTestCRUD(session).get_datas(**params.dict(), v_return_type="dict")
    total = await AuthTestCRUD(session).get_count(**params.to_count())
    return RestfulResponse.success(data=datas, total=total, page=params.page, limit=params.limit)


@router.get("/one/query", summary="获取测试信息")
async def one_query(
    data_id: int = Query(..., description="测试编号"),
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    data = await AuthTestCRUD(session).get_data(
        data_id, v_schema=auth_test_schema.AuthTestSimpleOutSchema, v_return_type="dict"
    )
    return RestfulResponse.success(data=data)
