# @Version        : 1.0
# @Create Time    : 2024/07/09
# @File           : auth_test_crud.py
# @IDE            : PyCharm
# @Desc           : 数据操作

from sqlalchemy.ext.asyncio import AsyncSession
from kinit_fast_task.app.cruds.base import ORMCrud
from kinit_fast_task.app.schemas import auth_test_schema
from kinit_fast_task.app.models.auth_test_model import AuthTestModel


class AuthTestCRUD(ORMCrud[AuthTestModel]):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.model = AuthTestModel
        self.simple_out_schema = auth_test_schema.AuthTestSimpleOutSchema
