# @Version        : 1.0
# @Create Time    : 2024/07/09
# @File           : auth_test_schema.py
# @IDE            : PyCharm
# @Desc           : Pydantic 模型，用于数据库序列化操作

from pydantic import Field
from kinit_fast_task.core.types import DatetimeStr
from kinit_fast_task.app.schemas.base import BaseSchema


class AuthTestSchema(BaseSchema):
    name: str = Field(..., description="角色名称")
    role_key: str = Field(..., description="标识")
    is_active: bool = Field(True, description="是否可用")
    age: int = Field(..., description="整数")


class AuthTestCreateSchema(AuthTestSchema):
    pass


class AuthTestUpdateSchema(AuthTestSchema):
    pass


class AuthTestSimpleOutSchema(AuthTestSchema):
    id: int = Field(..., description="编号")
    create_datetime: DatetimeStr = Field(..., description="创建时间")
    update_datetime: DatetimeStr = Field(..., description="更新时间")
