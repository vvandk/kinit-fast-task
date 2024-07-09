# @Version        : 1.0
# @Create Time    : 2024/5/15 下午6:21
# @File           : auth_role.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息


from sqlalchemy.orm import Mapped, mapped_column
from kinit_fast_task.app.models.base.orm import AbstractORMModel
from sqlalchemy import String


class AuthTestModel(AbstractORMModel):
    __tablename__ = "auth_test"
    __table_args__ = {"comment": "测试表"}

    name: Mapped[str] = mapped_column(String(255), index=True, comment="角色名称")
    role_key: Mapped[str] = mapped_column(String(11), comment="标识")
    is_active: Mapped[bool] = mapped_column(default=True, comment="是否可用")
    age: Mapped[int] = mapped_column(comment="整数")
