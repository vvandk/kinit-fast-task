from typing import Literal
from pydantic import BaseModel, Field
from kinit_fast_task.scripts.app_generate.utils.schema_base import ModelFieldSchema


class ModelConfigSchema(BaseModel):
    filename: str = Field(..., description="文件名称")
    class_name: str = Field(..., description="class 名称")
    table_args: dict = Field(..., description="表参数")
    fields: list[ModelFieldSchema] = Field(..., description="字段列表")


class SchemaConfigSchema(BaseModel):
    filename: str = Field(..., description="文件名称")
    base_class_name: str = Field(..., description="base schema 类名")
    create_class_name: str = Field(..., description="create schema 类名")
    update_class_name: str = Field(..., description="update schema 类名")
    simple_out_class_name: str = Field(..., description="simple_out schema 类名")


class CRUDConfigSchema(BaseModel):
    filename: str = Field(..., description="文件名称")
    class_name: str = Field(..., description="类名")


class ParamsConfigSchema(BaseModel):
    filename: str = Field(..., description="文件名称")
    class_name: str = Field(..., description="类名")


RouterAction = Literal["create", "update", "delete", "list_query", "one_query"]


class ViewsConfigSchema(BaseModel):
    filename: str = Field(..., description="文件名称")
    routers: list[RouterAction] = Field(..., description="需要生成的路由")


class JSONConfigSchema(BaseModel):
    version: str = Field("1.0", description="版本")
    app_name: str = Field(..., description="应用名称")
    app_desc: str = Field(..., description="应用描述")
    model: ModelConfigSchema = Field(..., description="ORM Model 配置")
    schemas: SchemaConfigSchema = Field(..., description="schema 序列化配置")
    crud: CRUDConfigSchema = Field(..., description="crud 配置")
    params: ParamsConfigSchema = Field(..., description="params 配置")
    views: ViewsConfigSchema = Field(..., description="views 配置")
