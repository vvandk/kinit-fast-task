# @Version        : 1.0
# @Create Time    : 2024/5/17 下午2:40
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 项目工具接口
import importlib

from kinit_fast_task.utils.response import RestfulResponse
from .schemas import GenerateAppCode
from kinit_fast_task.scripts.app_generate.main import AppGenerate

from fastapi import FastAPI


def load_system_routes(app: FastAPI):
    """
    加载系统系统
    :param app:
    :return:
    """

    @app.post(
        "/generate/app/code",
        summary="基于 ORM Model 生成 App 代码",
    )
    def generate_app_code(data: GenerateAppCode):
        generate = AppGenerate(model_file_name=data.orm_model_file_name, zh_name=data.zh_name, en_name=data.en_name)
        if data.read_only:
            result = generate.generate_codes()
        else:
            generate.write_app_generate_code()
            if data.reload:
                result = "生成代码已成功写入，并已加载到服务，请刷新页面查看"
                module_views = importlib.import_module(f"{generate.en_name}.views")
                app.include_router(module_views.router)
                # 重新生成 OpenAPI 文档
                app.openapi_schema = None
                app.openapi()
            else:
                result = "代码生成成功"
        return RestfulResponse.success(result)
