# @Version        : 1.0
# @Create Time    : 2021/10/19 15:47
# @File           : main.py
# @IDE            : PyCharm
# @Desc           : 主程序入口

"""
FastApi 更新文档：https://github.com/tiangolo/fastapi/releases
FastApi Github：https://github.com/tiangolo/fastapi
Typer 官方文档：https://typer.tiangolo.com/
"""

import typer

from kinit_fast_task.core.logger import log


shell_app = typer.Typer(rich_markup_mode="rich")


@shell_app.command()
def run(reload: bool = typer.Option(default=False, help="是否自动重载")):
    """
    项目启动

    命令行执行（自动重启）：python main.py run --reload
    命令行执行（不自动重启）：python main.py run

    原始命令行执行（uvicorn）：uvicorn kinit_fast_task.main:app

    # 在 pycharm 中使用自动重载是有 bug 的，很慢，截至 2024-04-30 还未修复，在使用 pycharm 开发时，不推荐使用 reload 功能

    :param reload: 是否自动重启
    :return:
    """  # noqa E501
    import uvicorn

    from kinit_fast_task.config import settings

    import sys
    import os

    sys.path.append(os.path.abspath(__file__))

    uvicorn.run(
        app="kinit_fast_task.main:app",
        host=str(settings.system.SERVER_HOST),
        port=settings.system.SERVER_PORT,
        reload=reload,
        lifespan="on",
    )


@shell_app.command()
def migrate():
    """
    将模型迁移到数据库，更新数据库表结构

    命令示例：python main.py migrate

    :return:
    """
    from kinit_fast_task.utils.tools import exec_shell_command

    log.info("开始更新数据库表")
    exec_shell_command("alembic revision --autogenerate", "生成迁移文件失败")
    exec_shell_command("alembic upgrade head", "迁移至数据库失败")
    log.info("数据库表迁移完成")


# @shell_app.command()
# def generate_app_code(
#     model_file_name: str = typer.Option(..., help="模型文件名称"),
#     read_only: bool = typer.Option(True, help="是否只打印代码，不写入文件"),
#     zh_name: str = typer.Option(None, help="功能中文名称, 主要用于描述和注释，默认使用表说明信息 comment"),
#     en_name: str = typer.Option(
#         None, help="功能英文名称, 主要用于 Schema, Params, CRUD, URL 命名，默认使用 model file name"
#     ),
# ):
#     """
#     基于 ORM Model 生成 app 代码
#
#     命令示例（输出代码模式）：python main.py generate-app-code --model-file-name auth_user
#     命令示例（写入代码模式）：python main.py generate-app-code --model-file-name auth_user --no-read-only
#
#     :return:
#     """
#     from kinit_fast_task.scripts.app_generate.main import AppGenerate
#
#     generate = AppGenerate(model_file_name, zh_name=zh_name, en_name=en_name)
#     log.info(f"开始生成 {generate.zh_name} App 代码")
#     if read_only:
#         generate.generate_codes()
#     else:
#         generate.write_app_generate_code()
#     log.info(f"{generate.zh_name} App 代码生成完成")


if __name__ == "__main__":
    shell_app()
