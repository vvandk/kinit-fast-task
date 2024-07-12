# @Version        : 1.0
# @Create Time    : 2024/05/17 18:14
# @File           : auth_role.py
# @IDE            : PyCharm
# @Desc           : 数据操作

from sqlalchemy.ext.asyncio import AsyncSession
from kinit_fast_task.app.cruds.base import ORMCrud
from kinit_fast_task.app.cruds.base.orm import ORMModel
from kinit_fast_task.app.schemas import auth_role_schema as role_s
from kinit_fast_task.app.models.auth_role_model import AuthRoleModel
from kinit_fast_task.core.exception import CustomException


class AuthRoleCRUD(ORMCrud[AuthRoleModel]):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.model = AuthRoleModel
        self.simple_out_schema = role_s.AuthRoleSimpleOutSchema

    async def create_data(self, data: role_s.AuthRoleCreateSchema, *, v_return_obj: bool = False) -> ORMModel | str:
        """
        重写创建角色方法
        """
        role_key = await self.get_data(role_key=data.role_key, v_return_none=True)
        if role_key:
            raise CustomException("角色唯一标识已存在！")
        return await super().create_data(data, v_return_obj=v_return_obj)

    async def create_datas(
        self, datas: list[role_s.AuthRoleCreateSchema], v_return_objs: bool = False
    ) -> list[ORMModel] | str:
        """
        重写批量创建角色方法
        """
        key_list = [r.role_key for r in datas]
        if len(key_list) != len(set(key_list)):
            raise CustomException("数据中存在重复的角色唯一标识, 请检查数据！")
        count = await self.get_count(role_key=("in", key_list))
        if count > 0:
            raise CustomException("角色唯一标识已存在, 请检查数据！")
        return await super().create_datas(datas, v_return_objs=v_return_objs)

    async def update_data(
        self, data_id: int, data: role_s.AuthRoleBaseSchema | dict, *, v_return_obj: bool = False
    ) -> ORMModel | str:
        """
        重写更新角色方法
        """
        role_obj = await self.get_data(role_key=data.role_key, v_return_none=True)
        if role_obj and role_obj.id != data_id:
            raise CustomException("角色唯一标识已存在！")
        return await super().update_data(data_id, data, v_return_obj=v_return_obj)
