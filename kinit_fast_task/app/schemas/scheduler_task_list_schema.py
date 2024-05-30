# @Version        : 1.0
# @Update Time    : 2024/5/18 14:59
# @File           : scheduler_task_list.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息

from pydantic import Field
from kinit_fast_task.core.types import DatetimeStr, ObjectIdStr, DictStr
from kinit_fast_task.app.schemas.base.base import BaseSchema
from kinit_fast_task.task.schema import JobExecStrategy


class TaskSchema(BaseSchema):
    name: str = Field(..., description="任务名称")
    group: str | None = Field(None, description="任务标签，任务组名")
    job_class: str = Field(..., description="任务执行实体类")
    job_params: DictStr = Field({}, description="任务执行实体类参数, dict 类型参数, 入参方式为：**kwargs")
    exec_strategy: JobExecStrategy = Field(..., description="执行策略")
    expression: str | None = Field(None, description="执行表达式, 一次任务可以不填")
    is_active: bool = Field(..., description="状态是否正常")
    remark: str | None = Field(None, description="描述")
    start_datetime: DatetimeStr | None = Field(None, description="任务开始时间")
    end_datetime: DatetimeStr | None = Field(None, description="任务结束时间")


class TaskSimpleOutSchema(TaskSchema):
    id: ObjectIdStr = Field(..., alias="_id")
    create_datetime: DatetimeStr = Field(..., description="创建时间")
    update_datetime: DatetimeStr = Field(..., description="更新时间")
    last_run_datetime: DatetimeStr | None = Field(None, description="最近一次执行时间")


class TaskCreateSchema(TaskSchema):
    """
    创建任务
    """

    pass
