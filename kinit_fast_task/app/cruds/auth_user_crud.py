# @Version        : 1.0
# @Create Time    : 2024/05/17 14:37
# @File           : auth_user.py
# @IDE            : PyCharm
# @Desc           : 数据操作
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as AbstractSchemaModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from kinit_fast_task.app.cruds.base.orm import ORMCrud, ORMModel
from kinit_fast_task.app.schemas import auth_user_schema as user_s
from kinit_fast_task.app.models.auth_user_model import AuthUserModel
from kinit_fast_task.app.cruds.auth_role_crud import AuthRoleCRUD
from kinit_fast_task.core.exception import CustomException


class AuthUserCRUD(ORMCrud[AuthUserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.model = AuthUserModel
        self.simple_out_schema = user_s.AuthUserSimpleOutSchema

    async def create_data(
        self, data: user_s.AuthUserCreateSchema, *, v_return_obj: bool = False
    ) -> AuthUserModel | str:
        """
        重写创建用户, 增加创建关联角色数据

        :param data: 创建数据
        :param v_return_obj: 是否返回 ORM 对象
        :return:
        """  # noqa E501

        # 验证数据是否合格
        telephone = await self.get_data(telephone=data.telephone, v_return_none=True)
        if telephone:
            raise CustomException("手机号已注册！")
        if data.email:
            email = await self.get_data(email=data.email, v_return_none=True)
            if email:
                raise CustomException("邮箱已注册！")

        # 开始创建操作
        data = jsonable_encoder(data)
        role_ids = data.pop("role_ids")
        obj = self.model(**data)
        if role_ids:
            roles = await AuthRoleCRUD(self.session).get_datas(limit=0, id=("in", role_ids), v_return_type="model")
            if len(role_ids) != len(roles):
                raise CustomException("关联角色异常, 请确保关联的角色存在！")
            for role in roles:
                obj.roles.add(role)
        await self.flush(obj)
        if v_return_obj:
            return obj
        return "创建成功"

    async def create_datas(
        self, datas: list[dict | AbstractSchemaModel], v_return_objs: bool = False
    ) -> list[ORMModel] | str:
        """
        重写批量创建用户方法
        """
        raise NotImplementedError("未实现批量创建用户方法！")

    async def update_data(
        self, data_id: int, data: user_s.AuthUserUpdateSchema | dict, *, v_return_obj: bool = False
    ) -> AuthUserModel | str:
        """
        根据 id 更新用户信息

        :param data_id: 修改行数据的 ID
        :param data: 更新的数据内容
        :param v_return_obj: 是否返回对象
        """
        v_options = [selectinload(AuthUserModel.roles)]
        obj: AuthUserModel = await self.get_data(data_id, v_options=v_options)

        # 验证数据是否合格
        if obj.telephone != data.telephone:
            telephone = await self.get_data(telephone=data.telephone, v_return_none=True)
            if telephone:
                raise CustomException("手机号已注册！")
        if obj.email != data.email and data.email is not None:
            email = await self.get_data(email=data.email, v_return_none=True)
            if email:
                raise CustomException("邮箱已注册！")

        # 开始更新操作
        data_dict = jsonable_encoder(data)
        for key, value in data_dict.items():
            if key == "role_ids":
                if value:
                    roles = await AuthRoleCRUD(self.session).get_datas(limit=0, id=("in", value), v_return_type="model")
                    if len(value) != len(roles):
                        raise CustomException("关联角色异常, 请确保关联的角色存在！")
                    if obj.roles:
                        obj.roles.clear()
                    for role in roles:
                        obj.roles.add(role)
                continue
            setattr(obj, key, value)
        await self.flush()
        if v_return_obj:
            return obj
        return "更新成功"
