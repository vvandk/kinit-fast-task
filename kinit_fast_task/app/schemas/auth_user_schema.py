# @Version        : 1.0
# @Create Time    : 2024/05/17 14:37
# @File           : auth_user.py
# @IDE            : PyCharm
# @Desc           : Pydantic 模型，用于数据库序列化操作

from pydantic import Field
from kinit_fast_task.core.types import DatetimeStr, Email, Telephone
from kinit_fast_task.app.schemas.base.base import BaseSchema
from kinit_fast_task.app.schemas import auth_role_schema


class AuthUserSchema(BaseSchema):
    name: str = Field(..., description="用户名")
    telephone: Telephone = Field(..., description="手机号")
    email: Email | None = Field(None, description="邮箱")
    is_active: bool = Field(True, description="是否可用")
    age: int = Field(..., description="年龄")


class AuthUserCreateSchema(AuthUserSchema):
    role_ids: list[int] = Field(..., description="关联角色列表")


class AuthUserUpdateSchema(AuthUserSchema):
    role_ids: list[int] = Field(..., description="关联角色列表")


class AuthUserSimpleOutSchema(AuthUserSchema):
    id: int = Field(..., description="编号")
    create_datetime: DatetimeStr = Field(..., description="创建时间")
    update_datetime: DatetimeStr = Field(..., description="更新时间")


class AuthUserOutSchema(AuthUserSimpleOutSchema):
    roles: list[auth_role_schema.AuthRoleSimpleOutSchema] = Field(..., description="角色列表")
