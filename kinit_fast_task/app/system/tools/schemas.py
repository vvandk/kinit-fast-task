# @Version        : 1.0
# @Create Time    : 2024/5/17 下午2:43
# @File           : schemas.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息


from pydantic import Field
from kinit_fast_task.app.schemas.base.base import BaseSchema


class GenerateAppCode(BaseSchema):
    orm_model_file_name: str = Field("auth_role", description="模型文件名称")
    zh_name: str = Field(
        None, examples=None, description="功能中文名称, 主要用于描述和注释，默认使用表说明信息 comment", hidden=True
    )
    en_name: str = Field(
        None,
        examples=None,
        description="功能英文名称, 主要用于 Schema, Params, CRUD, URL 命名，默认使用 model file name",
        hidden=True,
    )
    read_only: bool = Field(False, description="是否只打印代码，不写入文件")
    reload: bool = Field(True, description="是否在写入生成代码后，自动重新加载服务")
