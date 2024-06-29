# @Version        : 1.0
# @Create Time    : 2021/10/19 15:47
# @File           : middleware.py
# @IDE            : PyCharm
# @Desc           : 中间件

"""
官方文档——中间件：https://fastapi.tiangolo.com/tutorial/middleware/
官方文档——高级中间件：https://fastapi.tiangolo.com/advanced/middleware/

经测试：中间件中报错，或使用 raise 无论哪种类型的 Exception，都会被全局异常捕获，无法被特定异常捕获
所以最好是改变返回的 response
"""

import datetime
import json
import time

from fastapi import Request
from kinit_fast_task.utils import log
from fastapi import FastAPI
from fastapi.routing import APIRoute
from user_agents import parse
from kinit_fast_task.config import settings
from kinit_fast_task.app.cruds.record_operation_crud import OperationCURD
from kinit_fast_task.utils.response import RestfulResponse
from kinit_fast_task.utils.response_code import Status


def register_request_log_middleware(app: FastAPI):
    """
    记录请求日志中间件
    :param app:
    :return:
    """

    @app.middleware("http")
    async def request_log_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = f"{int((time.time() - start_time) * 1000)}ms"
        response.headers["X-Process-Time"] = str(process_time)
        http_version = f"http/{request.scope['http_version']}"
        content_length = response.raw_headers[0][1]
        process_time = response.headers["X-Process-Time"]
        content = (
            f"request router: '{request.method} {request.url} {http_version}' {response.status_code} "
            f"{response.charset} {content_length} {process_time}"
        )
        if response.status_code != 200:
            log.error(content)
        else:
            log.info(content)
        return response


def register_operation_record_middleware(app: FastAPI):
    """
    操作记录中间件
    用于将使用认证的操作全部记录到 mongodb 数据库中
    :param app:
    :return:
    """

    @app.middleware("http")
    async def operation_record_middleware(request: Request, call_next):
        if not settings.db.MONGO_DB_ENABLE:
            log.error("未开启 MongoDB 数据库，无法存入操作记录，请在 config.py:OPERATION_LOG_RECORD 中关闭操作记录")
            return RestfulResponse.error("系统异常，请联系管理员", code=Status.HTTP_500)

        start_time = time.time()
        body_params = await request.body()
        body_params = body_params.decode("utf-8", errors="ignore")
        response = await call_next(request)
        route = request.scope.get("route")
        if (
            request.method not in settings.system.OPERATION_RECORD_METHOD
            or route.name in settings.system.IGNORE_OPERATION_FUNCTION
        ):
            return response
        process_time = time.time() - start_time
        user_agent = parse(request.headers.get("user-agent"))
        system = f"{user_agent.os.family} {user_agent.os.version_string}"
        browser = f"{user_agent.browser.family} {user_agent.browser.version_string}"
        query_params = dict(request.query_params.multi_items())
        path_params = request.path_params
        params = {
            "body_params": body_params,
            "query_params": query_params if query_params else None,
            "path_params": path_params if path_params else None,
        }
        content_length = response.raw_headers[0][1]
        assert isinstance(route, APIRoute)
        document = {
            "process_time": process_time,
            "request_api": request.url.__str__(),
            "client_ip": request.client.host,
            "system": system,
            "browser": browser,
            "request_method": request.method,
            "api_path": route.path,
            "summary": route.summary,
            "description": route.description,
            "tags": route.tags,
            "route_name": route.name,
            "status_code": response.status_code,
            "content_length": content_length,
            "create_datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "params": json.dumps(params),
        }
        await OperationCURD().create_data(document)
        return response


def register_demo_env_middleware(app: FastAPI):
    """
    演示环境中间件
    :param app:
    :return:
    """

    @app.middleware("http")
    async def demo_env_middleware(request: Request, call_next):
        path = request.scope.get("path")
        # if request.method != "GET":
        #     print("路由：", path, request.method)
        if settings.demo.DEMO_ENV and request.method != "GET":
            if path in settings.demo.DEMO_BLACK_LIST_PATH:
                return RestfulResponse.error("演示环境，禁止操作")
            elif path not in settings.demo.DEMO_WHITE_LIST_PATH:
                return RestfulResponse.error("演示环境，禁止操作")
        return await call_next(request)


def register_jwt_refresh_middleware(app: FastAPI):
    """
    JWT刷新中间件
    :param app:
    :return:
    """

    @app.middleware("http")
    async def jwt_refresh_middleware(request: Request, call_next):
        response = await call_next(request)
        refresh = request.scope.get("if-refresh", 0)
        response.headers["if-refresh"] = str(refresh)
        return response
