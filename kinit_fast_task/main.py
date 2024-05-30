# @Version        : 1.0
# @Create Time    : 2024/3/24 19:55
# @File           : main.py
# @IDE            : PyCharm
# @Desc           : 项目启动
from rich.padding import Padding
from rich.panel import Panel
from rich import print

from kinit_fast_task.config import settings
from kinit_fast_task.core.register import (
    register_middleware,
    register_static,
    register_router,
    register_system_router,
    register_exception,
    register_event,
)
from fastapi import FastAPI

from kinit_fast_task.utils.response import ErrorResponseSchema

import logging

# 关闭 Uvicorn HTTP 请求日志记录
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers = []
uvicorn_access_logger.propagate = False


# uvicorn 主日志处理器
uvicorn_logger = logging.getLogger("uvicorn")


def create_app():
    """
    启动项目
    docs_url：配置交互文档的路由地址，如果禁用则为None，默认为 /docs
    redoc_url： 配置 Redoc 文档的路由地址，如果禁用则为None，默认为 /redoc
    openapi_url：配置接口文件json数据文件路由地址，如果禁用则为None，默认为/openapi.json
    """

    description = """
    本项目基于Python社区FastAPI技术栈编写而成，本意为所有需要使用FastAPI开发的人提供一个合适的脚手架，避免重复开发。
    
    在项目中也融合了很多FastAPI技术栈可以参考使用。
    """  # noqa E501
    host = str(settings.system.SERVER_HOST)
    port = settings.system.SERVER_PORT
    server_address = f"http://{'127.0.0.1' if host == '0.0.0.0' else host}:{port}"

    serving_str = f"[dim]API Server URL:[/dim] [link]http://{host}:{port}[/link]"
    serving_str += f"\n\n[dim]Swagger UI Docs:[/dim] [link]{server_address}/docs[/link]"
    serving_str += f"\n\n[dim]Redoc HTML Docs:[/dim] [link]{server_address}/redoc[/link]"

    # 踩坑1：rich Panel 使用中文会导致边框对不齐的情况
    panel = Panel(
        serving_str,
        title=f"{settings.system.PROJECT_NAME}",
        expand=False,
        padding=(1, 2),
        style="black on yellow",
    )
    print(Padding(panel, 1))

    # 异常 Response 定义
    responses = {400: {"model": ErrorResponseSchema, "description": "请求失败"}}

    _app = FastAPI(
        title="KINIT FAST TASK",
        description=description,
        lifespan=register_event,
        docs_url=None,
        redoc_url=None,
        responses=responses,
    )

    # 全局异常捕捉处理
    register_exception(_app)

    # 注册中间件
    register_middleware(_app)

    # 挂在静态目录
    register_static(_app)

    # 引入应用中的路由
    register_router(_app)

    # 加载系统路由
    register_system_router(_app)

    uvicorn_logger.info(f"Load API Number：{len(_app.routes)}, Custom Add Number：{len(_app.routes) - 5}")
    uvicorn_logger.info(f"Load APPS：{settings.router.APPS}")
    uvicorn_logger.info(f"Load APPS Path：{settings.router.APPS_PATH}")

    return _app


app = create_app()
