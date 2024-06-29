# @Version        : 1.0
# @Create Time    : 2024/05/17 18:14
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 路由，视图文件
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Body, Query

from kinit_fast_task.db.database_factory import DBFactory
from kinit_fast_task.utils.response import RestfulResponse, ResponseSchema, PageResponseSchema
from kinit_fast_task.app.cruds.auth_role_crud import AuthRoleCRUD
from kinit_fast_task.app.schemas import auth_role_schema
from .params import PageParams

router = APIRouter(prefix="/auth/role", tags=["角色管理"])


@router.post("/create", response_model=ResponseSchema[str], summary="创建角色")
async def create(
    data: auth_role_schema.AuthRoleCreateSchema,
    session: AsyncSession = Depends(DBFactory.get_db_instance("orm").db_transaction_getter),
):
    """
    示例数据：

        {
          "name": "管理员",
          "role_key": "admin",
          "is_active": true
        }
    """
    return RestfulResponse.success(await AuthRoleCRUD(session).create_data(data=data))


@router.post("/batch/create", response_model=ResponseSchema[str], summary="批量创建角色")
async def batch_create(
    datas: list[auth_role_schema.AuthRoleCreateSchema],
    session: AsyncSession = Depends(DBFactory.get_db_instance("orm").db_transaction_getter),
):
    """
    示例数据：

        [
            {
              "name": "管理员",
              "role_key": "admin",
              "is_active": true
            },
            ...
        ]
    """
    return RestfulResponse.success(await AuthRoleCRUD(session).create_datas(datas))


@router.put("/update", response_model=ResponseSchema[str], summary="更新角色")
async def update(
    data_id: int = Body(..., description="角色编号"),
    data: auth_role_schema.AuthRoleUpdateSchema = Body(..., description="更新内容"),
    session: AsyncSession = Depends(DBFactory.get_db_instance("orm").db_transaction_getter),
):
    return RestfulResponse.success(await AuthRoleCRUD(session).update_data(data_id, data))


@router.delete("/delete", response_model=ResponseSchema[str], summary="批量删除角色")
async def delete(
    data_ids: list[int] = Body(..., description="角色编号列表"),
    session: AsyncSession = Depends(DBFactory.get_db_instance("orm").db_transaction_getter),
):
    await AuthRoleCRUD(session).delete_datas(ids=data_ids)
    return RestfulResponse.success("删除成功")


@router.get(
    "/list/query",
    response_model=PageResponseSchema[list[auth_role_schema.AuthRoleSimpleOutSchema]],
    summary="获取角色列表",
)
async def list_query(
    params: PageParams = Depends(),
    session: AsyncSession = Depends(DBFactory.get_db_instance("orm").db_transaction_getter),
):
    datas = await AuthRoleCRUD(session).get_datas(**params.dict(), v_return_type="dict")
    total = await AuthRoleCRUD(session).get_count(**params.to_count())
    return RestfulResponse.success(data=datas, total=total, page=params.page, limit=params.limit)


@router.get("/one/query", summary="获取角色信息")
async def one_query(
    data_id: int = Query(..., description="角色编号"),
    session: AsyncSession = Depends(DBFactory.get_db_instance("orm").db_transaction_getter),
):
    data = await AuthRoleCRUD(session).get_data(
        data_id, v_schema=auth_role_schema.AuthRoleSimpleOutSchema, v_return_type="dict"
    )
    return RestfulResponse.success(data=data)
