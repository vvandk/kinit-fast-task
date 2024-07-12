# @Version        : 1.0
# @Create Time    : 2024/5/15 下午6:21
# @File           : auth_role.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息


from sqlalchemy.orm import relationship, Mapped, mapped_column
from kinit_fast_task.app.models.base.orm import AbstractORMModel
from sqlalchemy import String
from kinit_fast_task.app.models.auth_user_to_role_model import auth_user_to_role_model


class AuthRoleModel(AbstractORMModel):
    __tablename__ = "auth_role"
    __table_args__ = {"comment": "角色表"}

    users: Mapped[set["AuthUserModel"]] = relationship(secondary=auth_user_to_role_model, back_populates="roles")

    name: Mapped[str] = mapped_column(String(255), index=True, comment="角色名称")
    role_key: Mapped[str] = mapped_column(String(11), comment="角色唯一标识")
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否可用")
