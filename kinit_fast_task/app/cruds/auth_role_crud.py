# @Version        : 1.0
# @Create Time    : 2024/05/17 18:14
# @File           : auth_role.py
# @IDE            : PyCharm
# @Desc           : 数据操作

from sqlalchemy.ext.asyncio import AsyncSession
from kinit_fast_task.app.cruds.base import ORMCrud
from kinit_fast_task.app.schemas import auth_role_schema
from kinit_fast_task.app.models.auth_role_model import AuthRoleModel


class AuthRoleCRUD(ORMCrud[AuthRoleModel]):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.model = AuthRoleModel
        self.simple_out_schema = auth_role_schema.AuthRoleSimpleOutSchema
