# @Version        : 1.0
# @Create Time    : 2024/5/15 下午6:21
# @File           : auth_user.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息


from sqlalchemy.orm import relationship, Mapped, mapped_column

from kinit_fast_task.app.models.auth_user_to_role_model import auth_user_to_role_model
from kinit_fast_task.app.models.base.orm import AbstractORMModel
from sqlalchemy import String, Text, DECIMAL


class AuthUserModel(AbstractORMModel):
    __tablename__ = "auth_user"
    __table_args__ = {"comment": "用户表"}

    roles: Mapped[set["AuthRoleModel"]] = relationship(secondary=auth_user_to_role_model, back_populates="users")

    name: Mapped[str] = mapped_column(String(255), default="aaaaaa", index=True, comment="用户名")
    telephone: Mapped[str] = mapped_column(String(11), comment="手机号")
    email: Mapped[str | None] = mapped_column(comment="邮箱")
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否可用")
    age: Mapped[int] = mapped_column(comment="年龄")
    content: Mapped[str] = mapped_column(Text, comment="年龄")
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), comment="年龄")
