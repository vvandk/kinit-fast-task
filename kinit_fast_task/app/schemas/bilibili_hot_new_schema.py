# @Version        : 1.0
# @Create Time    : 2024/5/22 下午3:54
# @File           : bilibili_hot_new.py
# @IDE            : PyCharm
# @Desc           : bilibili 热搜数据

from pydantic import Field
from kinit_fast_task.core.types import DatetimeStr, ObjectIdStr
from kinit_fast_task.app.schemas.base.base import BaseSchema


class BilibiliHotNewSchema(BaseSchema):
    title: str = Field(..., description="热搜标题")
    heat: str = Field(..., description="热搜热度")
    link: str = Field(..., description="	b站链接")


class BilibiliHotNewSimpleOutSchema(BilibiliHotNewSchema):
    id: ObjectIdStr = Field(..., alias="_id")
    create_datetime: DatetimeStr = Field(..., description="创建时间")
    update_datetime: DatetimeStr = Field(..., description="更新时间")
