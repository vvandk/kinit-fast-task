# @Version        : 1.0
# @Create Time    : 2024/03/25 18:08
# @File           : register.py
# @IDE            : PyCharm
# @Desc           : 功能注册
import importlib
import sys
from contextlib import asynccontextmanager
from kinit_fast_task.core.exception import refactoring_exception
from kinit_fast_task.utils.tools import import_modules, import_modules_async
from fastapi.middleware.cors import CORSMiddleware
from kinit_fast_task.config import settings
from starlette.staticfiles import StaticFiles  # 依赖安装：poetry add aiofiles
from fastapi import FastAPI


@asynccontextmanager
async def register_event(app: FastAPI):
    await import_modules_async(settings.system.EVENTS, "全局事件", app=app, status=True)

    yield

    await import_modules_async(settings.system.EVENTS, "全局事件", app=app, status=False)


def register_middleware(app: FastAPI):
    """
    注册中间件
    """
    import_modules(settings.system.MIDDLEWARES, "中间件", app=app)

    if settings.system.CORS_ORIGIN_ENABLE:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.system.ALLOW_ORIGINS,
            allow_credentials=settings.system.ALLOW_CREDENTIALS,
            allow_methods=settings.system.ALLOW_METHODS,
            allow_headers=settings.system.ALLOW_HEADERS,
        )


def register_exception(app: FastAPI):
    """
    注册异常
    """
    refactoring_exception(app)


def register_static(app: FastAPI):
    """
    挂载静态文件目录
    """
    app.mount(settings.storage.LOCAL_BASE_URL, app=StaticFiles(directory=settings.storage.LOCAL_PATH))


def register_router(app: FastAPI):
    """
    注册路由
    """
    sys.path.append(settings.router.APPS_PATH)
    for app_module_str in settings.router.APPS:
        module_views = importlib.import_module(f"{app_module_str}.views")
        app.include_router(module_views.router)


def register_system_router(app: FastAPI):
    """
    注册系统路由
    """
    from kinit_fast_task.app.system.docs import views as docs_views

    if settings.system.API_DOCS_ENABLE:
        docs_views.load_system_routes(app)
