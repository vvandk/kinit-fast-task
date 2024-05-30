# @Version        : 1.0
# @Create Time    : 2023/3/27 9:48
# @File           : response.py
# @IDE            : PyCharm
# @Desc           : 全局响应


from pydantic import BaseModel, Field
from kinit_fast_task.utils.response_code import Status
from typing import Generic, TypeVar
from fastapi import status as fastapi_status
from fastapi.responses import ORJSONResponse

DataT = TypeVar("DataT")


class ResponseSchema(BaseModel, Generic[DataT]):
    """
    默认响应模型
    """

    code: int = Field(Status.HTTP_SUCCESS, description="响应状态码（响应体内）")
    message: str = Field("success", description="响应结果描述")
    data: DataT = Field(None, description="响应结果数据")


class PageResponseSchema(ResponseSchema):
    """
    带有分页的响应模型
    """

    total: int = Field(0, description="总数据量")
    page: int = Field(1, description="当前页数")
    limit: int = Field(10, description="每页多少条数据")


class ErrorResponseSchema(BaseModel, Generic[DataT]):
    """
    默认请求失败响应模型
    """

    code: int = Field(Status.HTTP_ERROR, description="响应状态码（响应体内）")
    message: str = Field("请求失败，请联系管理员", description="响应结果描述")
    data: DataT = Field(None, description="响应结果数据")


ResponseSchemaT = TypeVar("ResponseSchemaT", bound=ResponseSchema)


class RestfulResponse:
    """
    响应体
    """

    @staticmethod
    def success(
        message: str = "success",
        *,
        code: int = Status.HTTP_SUCCESS,
        data: DataT = None,
        status_code: int = fastapi_status.HTTP_200_OK,
        **kwargs,
    ) -> ORJSONResponse:
        """
        成功响应

        :param message: 响应结果描述
        :param code: 业务响应体状态码
        :param data: 响应结果数据
        :param status_code: HTTP 响应状态码
        :param kwargs: 额外参数
        :return:
        """
        content = ResponseSchema(code=code, message=message, data=data)
        content = content.model_dump() | kwargs
        return ORJSONResponse(content=content, status_code=status_code)

    @staticmethod
    def error(
        message: str,
        *,
        code: int = Status.HTTP_ERROR,
        data: DataT = None,
        status_code: int = fastapi_status.HTTP_200_OK,
        **kwargs,
    ) -> ORJSONResponse:
        """
        失败响应

        :param message: 响应结果描述
        :param code: 业务响应体状态码
        :param data: 响应结果数据
        :param status_code: HTTP 响应状态码
        :return:
        """
        content = ErrorResponseSchema(code=code, message=message, data=data)
        content = content.model_dump() | kwargs
        return ORJSONResponse(content=content, status_code=status_code)
