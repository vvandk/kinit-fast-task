# @Version        : 1.0
# @Create Time    : 2024/5/15 下午7:04
# @File           : auth_user_to_role.py
# @IDE            : PyCharm
# @Desc           : user role 多对多关联表


from kinit_fast_task.db.orm.async_base_model import AsyncBaseORMModel
from sqlalchemy import ForeignKey, Column, Table, Integer


auth_user_to_role_model = Table(
    "auth_user_to_role",
    AsyncBaseORMModel.metadata,
    Column("user_id", Integer, ForeignKey("auth_user.id", ondelete="CASCADE")),
    Column("role_id", Integer, ForeignKey("auth_role.id", ondelete="CASCADE")),
)
