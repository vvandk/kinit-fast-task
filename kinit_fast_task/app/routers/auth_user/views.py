# @Version        : 1.0
# @Create Time    : 2024/05/17 14:37
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 路由，视图文件

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Body, Query
from sqlalchemy.orm import selectinload

from kinit_fast_task.db import DBFactory
from kinit_fast_task.utils.response import RestfulResponse, ResponseSchema, PageResponseSchema
from kinit_fast_task.app.cruds.auth_user_crud import AuthUserCRUD
from kinit_fast_task.app.schemas import auth_user_schema
from kinit_fast_task.app.models.auth_user_model import AuthUserModel
from .params import PageParams
from .services import UserService

router = APIRouter(prefix="/auth/user", tags=["用户管理"])


@router.post("/create", response_model=ResponseSchema[str], summary="创建用户")
async def create(
    data: auth_user_schema.AuthUserCreateSchema,
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    """
    示例数据：

        {
          "name": "kinit",
          "telephone": "18820240528",
          "email": "user@email.com",
          "is_active": true,
          "age": 3,
          "role_ids": [
            1, 2
          ]
        }
    """
    return RestfulResponse.success(await AuthUserCRUD(session).create_data(data=data))


@router.put("/update", response_model=ResponseSchema[str], summary="更新用户")
async def update(
    data_id: int = Body(..., description="用户编号"),
    data: auth_user_schema.AuthUserUpdateSchema = Body(..., description="更新内容"),
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    return RestfulResponse.success(await AuthUserCRUD(session).update_data(data_id, data))


@router.delete("/delete", response_model=ResponseSchema[str], summary="批量删除用户")
async def delete(
    data_ids: list[int] = Body(..., description="用户编号列表"),
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    await AuthUserCRUD(session).delete_datas(ids=data_ids)
    return RestfulResponse.success("删除成功")


@router.get(
    "/list/query", response_model=PageResponseSchema[list[auth_user_schema.AuthUserOutSchema]], summary="获取用户列表"
)
async def list_query(
    params: PageParams = Depends(),
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    v_options = [selectinload(AuthUserModel.roles)]
    v_schema = auth_user_schema.AuthUserOutSchema
    datas = await AuthUserCRUD(session).get_datas(
        **params.dict(), v_options=v_options, v_return_type="dict", v_schema=v_schema
    )
    total = await AuthUserCRUD(session).get_count(**params.to_count())
    return RestfulResponse.success(data=datas, total=total, page=params.page, limit=params.limit)


@router.get("/one/query", response_model=PageResponseSchema[auth_user_schema.AuthUserOutSchema], summary="获取用户信息")
async def one_query(
    data_id: int = Query(..., description="用户编号"),
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    v_options = [selectinload(AuthUserModel.roles)]
    data = await AuthUserCRUD(session).get_data(
        data_id, v_schema=auth_user_schema.AuthUserOutSchema, v_options=v_options, v_return_type="dict"
    )
    return RestfulResponse.success(data=data)


@router.get("/recent/month/user/query", response_model=PageResponseSchema[dict], summary="获取最近一个月的用户新增情况")
async def recent_month_user_query(
    session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter),
):
    return RestfulResponse.success(data=await UserService(session).get_recent_users_count())


@router.post("/orm/db/getter/01/test", response_model=ResponseSchema[str], summary="ORM db_getter 手动事务测试")
async def orm_db_getter_test():
    """
    ORM db_getter 手动事务测试
    """
    await UserService().orm_db_getter_01_test()
    return RestfulResponse.success()


@router.post("/orm/db/getter/02/test", response_model=ResponseSchema[str], summary="ORM db_getter 测试")
async def orm_db_getter_test_02():
    """
    ORM db_getter 测试
    """
    await UserService().orm_db_getter_02_test()
    return RestfulResponse.success()


@router.post("/orm/03/test", response_model=ResponseSchema[str], summary="ORM 多对多（多对一也可用）关联查询测试")
async def orm_03_test(session: AsyncSession = Depends(DBFactory.get_instance("orm").db_transaction_getter)):
    """
    ORM 多对多（多对一也可用）关联查询测试
    """
    await UserService(session).orm_03_test()
    return RestfulResponse.success()
