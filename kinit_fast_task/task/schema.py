# @Version        : 1.0
# @Create Time    : 2024/5/20 上午9:55
# @File           : schema.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息


from enum import Enum

from pydantic import Field
from kinit_fast_task.core.types import DatetimeStr, DictStr
from kinit_fast_task.app.schemas.base.base import BaseSchema


class JobExecStrategy(Enum):
    """
    任务执行策略
    """

    interval = "interval"  # 时间间隔
    date = "date"  # 指定日期
    cron = "cron"  # cron 表达式
    once = "once"  # 执行一次，立即执行


class AddTask(BaseSchema):
    """
    添加任务
    """

    task_id: str = Field(..., description="任务编号")
    group: str | None = Field(None, description="任务标签，任务组名")
    job_class: str = Field(..., description="任务执行实体类")
    job_params: DictStr = Field({}, description="任务执行实体类参数, dict 类型参数, 入参方式为：**kwargs")
    exec_strategy: JobExecStrategy = Field(..., description="执行策略")
    expression: str | None = Field(None, description="执行表达式")
    remark: str | None = Field(None, description="描述")
    start_datetime: DatetimeStr | None = Field(None, description="任务开始时间")
    end_datetime: DatetimeStr | None = Field(None, description="任务结束时间")
