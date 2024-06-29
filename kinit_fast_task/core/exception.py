# @Version        : 1.0
# @Create Time    : 2024/16/19 15:47
# @File           : exception.py
# @IDE            : PyCharm
# @Desc           : 全局异常处理

from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from kinit_fast_task.utils.response_code import Status as UtilsStatus
from fastapi import status as fastapi_status
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi import FastAPI
from kinit_fast_task.core import log


class CustomException(Exception):
    """
    自定义异常
    """

    def __init__(
        self,
        message: str,
        *,
        code: int = UtilsStatus.HTTP_ERROR,
        status_code: int = fastapi_status.HTTP_200_OK,
        desc: str = None,
    ):
        """
        自定义异常
        :param message: 报错内容提示信息
        :param code: 描述 code
        :param status_code: 响应 code
        :param desc: 描述信息，不返回给前端，只在接口日志中输出
        """
        self.message = message
        self.status_code = status_code
        if self.status_code != fastapi_status.HTTP_200_OK:
            self.code = self.status_code
        else:
            self.code = code
        self.desc = desc


def refactoring_exception(app: FastAPI):
    """
    异常捕捉
    """

    @app.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        """
        自定义异常
        """
        func_desc = "捕捉到自定义CustomException异常：custom_exception_handler"
        log.error(f"请求地址：{request.url.__str__()} {func_desc} 异常信息：{exc.message} {exc.desc}")
        # 打印栈信息，方便追踪排查异常
        # log.exception(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message, "code": exc.code},
        )

    @app.exception_handler(StarletteHTTPException)
    async def unicorn_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        重写HTTPException异常处理器
        """
        func_desc = "捕捉到重写HTTPException异常异常：unicorn_exception_handler"
        log.error(f"请求地址：{request.url.__str__()} {func_desc} 异常信息：{exc.detail}")
        # 打印栈信息，方便追踪排查异常
        # log.exception(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        重写请求验证异常处理器
        """
        func_desc = "捕捉到重写请求验证异常异常：validation_exception_handler"
        log.error(f"请求地址：{request.url.__str__()} {func_desc} 异常信息：{exc.errors()}")
        # 打印栈信息，方便追踪排查异常
        # log.exception(exc)
        msg = exc.errors()[0].get("msg")
        if msg == "field required":
            msg = "请求失败，缺少必填项！"
        elif msg == "value is not a valid list":
            msg = "类型错误，提交参数应该为列表！"
        elif msg == "value is not a valid int":
            msg = "类型错误，提交参数应该为整数！"
        elif msg == "value could not be parsed to a boolean":
            msg = "类型错误，提交参数应该为布尔值！"
        elif msg == "Input should be a valid list":
            msg = "类型错误，输入应该是一个有效的列表！"
        return JSONResponse(
            status_code=fastapi_status.HTTP_200_OK,
            content=jsonable_encoder({"message": msg, "body": exc.body, "code": UtilsStatus.HTTP_ERROR}),
        )

    @app.exception_handler(ValueError)
    async def value_exception_handler(request: Request, exc: ValueError):
        """
        捕获值异常
        """
        func_desc = "捕捉到值异常：value_exception_handler"
        log.error(f"请求地址：{request.url.__str__()} {func_desc} 异常信息：{exc.__str__()}")
        # 打印栈信息，方便追踪排查异常
        # log.exception(exc)
        return JSONResponse(
            status_code=fastapi_status.HTTP_200_OK,
            content=jsonable_encoder({"message": exc.__str__(), "code": UtilsStatus.HTTP_ERROR}),
        )

    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        """
        捕捉到全局异常
        """
        func_desc = "捕捉到全局异常：all_exception_handler"
        log.error(f"请求地址：{request.url.__str__()} {func_desc} 异常信息：{exc.__str__()}")
        # 打印栈信息，方便追踪排查异常
        # log.exception(exc)
        return JSONResponse(
            status_code=fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder({"message": "接口异常，请联系管理员！", "code": UtilsStatus.HTTP_500}),
        )
