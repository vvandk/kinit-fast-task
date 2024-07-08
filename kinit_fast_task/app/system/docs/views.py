# @Version        : 1.0
# @Create Time    : 2024/5/17 下午4:40
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 接口文档


from fastapi import Request, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
from kinit_fast_task.config import settings


def load_system_routes(app: FastAPI):
    """
    加载系统系统
    :param app:
    :return:
    """

    @app.get("/docs", summary="Swagger UI API Docs", include_in_schema=False)
    def rewrite_generate_swagger_ui(request: Request):
        return get_swagger_ui_html(
            openapi_url=request.app.openapi_url,
            title=f"{request.app.title} - Swagger UI",
            oauth2_redirect_url=request.app.swagger_ui_oauth2_redirect_url,
            swagger_js_url=f"{settings.storage.LOCAL_BASE_URL}/swagger_ui/swagger-ui-bundle.js",
            swagger_css_url=f"{settings.storage.LOCAL_BASE_URL}/swagger_ui/swagger-ui.css",
        )

    @app.get("/swagger-redirect", summary="Swagger UI Redirect", include_in_schema=False)
    def rewrite_swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    @app.get("/redoc", summary="Redoc HTML API Docs", include_in_schema=False)
    def rewrite_generate_redoc_html(request: Request):
        return get_redoc_html(
            openapi_url=request.app.openapi_url,
            title=f"{request.app.title} - ReDoc",
            redoc_js_url=f"{settings.storage.LOCAL_BASE_URL}/redoc_ui/redoc.standalone.js",
        )
