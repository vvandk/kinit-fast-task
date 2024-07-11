# @Version        : 1.0
# @Create Time    : 2024/7/11
# @File           : global_schema.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息
from pydantic import Field

from kinit_fast_task.app.schemas import BaseSchema


class DeleteSchema(BaseSchema):
    data_ids: list[int] = Field(..., description="需要删除的数据编号列表")
