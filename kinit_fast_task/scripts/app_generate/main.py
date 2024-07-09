import importlib
import json
from typing import Literal

from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.config import settings
from kinit_fast_task.scripts.app_generate.v1.model_to_json import ModelToJson as ModelToJsonV1
from kinit_fast_task.scripts.app_generate.v1.generate_code import GenerateCode as GenerateCodeV1
from kinit_fast_task.utils import log

VERSIONS = Literal["1.0"]


class AppGenerate:
    """
    生成 APP 代码:

        1. 基于 ORM Model 生成 Json 配置文件
        2. 基于 JSON 配置文件生成代码
        3. 基于 ORM Model 生成代码（先生成 JSON 配置后基于 JSON 生成代码）
    """

    SCRIPT_PATH = settings.BASE_PATH / "scripts" / "app_generate"

    def __init__(self, verbose: bool = False):
        """
        初始化 AppGenerate 类
        """
        self.verbose = verbose
        self.task_log = log.create_task(verbose=verbose)

    @staticmethod
    def model_mapping(model_class_name: str) -> type[AbstractORMModel]:
        """
        映射 ORM Model

        :return: ORM Model 类
        """
        module = importlib.import_module(f"{settings.system.PROJECT_NAME}.app.models")
        return getattr(module, model_class_name)

    @staticmethod
    def write_json(filename: str, data: dict) -> None:
        """
        写入 json 文件

        :param filename:
        :param data:
        :return:
        """
        if filename is not None:
            with open(filename, "w", encoding="utf-8") as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

    @staticmethod
    def read_json(filename: str) -> dict:
        """
        读取 json 文件

        :param filename:
        :return:
        """
        with open(filename, encoding="utf-8") as json_file:
            json_config = json.load(json_file)
            return json_config

    def model_to_json(
        self, *, model_class_name: str, app_name: str, app_desc: str, version: VERSIONS = "1.0", filename: str = None
    ) -> dict:
        """
        基于单个 model 输出 JSON 配置文件

        :param model_class_name: Model 类名, 示例：AuthUserModel
        :param app_name: app 名称, 示例：auth_user
        :param app_desc: app 描述, 示例：AuthUserModel
        :param version: json 版本
        :param filename: 文件名称, 为 None 则不写入文件
        :return: dict
        """
        model = self.model_mapping(model_class_name)
        if version == "1.0":
            mtj = ModelToJsonV1(model, app_name, app_desc)
        else:
            raise NotImplementedError(f"version {version} not implemented")

        json_config = mtj.to_json()

        if filename:
            self.write_json(filename, json_config)

        return json_config

    def json_to_code(
        self, *, json_config_file: str = None, json_config: dict = None, is_write: bool = False, overwrite: bool = False
    ) -> None:
        """
        基于 JSON 配置文件生成代码

        :param json_config_file: json 配置文件地址
        :param json_config: json 配置
        :param is_write: 是否将生成结果直接写入文件
        :param overwrite: 是否在写入时覆盖文件
        """
        if json_config_file:
            self.task_log.info("基于 JSON 配置生成代码, 配置文件：", json_config_file, is_verbose=True)
            json_config = self.read_json(json_config_file)

        version = json_config["version"]
        self.task_log.info("基于 JSON 配置生成代码, 版本：", version, is_verbose=True)

        if version == "1.0":
            gc = GenerateCodeV1(json_config, task_log=self.task_log)
        else:
            raise NotImplementedError(f"version {version} not implemented")

        if is_write:
            self.task_log.info("基于 JSON 配置生成代码, 开始生成, 并将生成结果直接写入文件")
            gc.write_generate(overwrite=overwrite)
        else:
            self.task_log.info("基于 JSON 配置生成代码, 开始生成, 只输出代码, 不写入文件")
            gc.generate()
        self.task_log.success("基于 JSON 配置生成代码, 执行成功", is_verbose=True)
        if is_write:
            self.task_log.info("推荐执行代码格式化命令：")
            self.task_log.info("1. ruff format")
            self.task_log.info("2. ruff check --fix")
            self.task_log.info("如若使用还需进行以下两步操作：")
            migrate_command = "python main.py migrate"
            model_class = gc.json_config.model.class_name
            self.task_log.info(
                f"1. 请确认 {model_class} 数据表已完成迁移至数据库, 若还没迁移, 可执行：{migrate_command} 迁移命令！"
            )
            self.task_log.info(f"2. 请确认在 config.py:RouterSettings.APPS 配置中添加 {gc.json_config.app_name} 路由！")
        self.task_log.end()

    def model_to_code(
        self, *, model_class_name: str, app_name: str, app_desc: str, write_only: bool = False, overwrite: bool = False
    ) -> None:
        """
        基于单个 model 生成代码

        :param model_class_name: Model 类名, 示例：AuthUserModel
        :param app_name: app 名称, 示例：auth_user
        :param app_desc: app 描述, 示例：AuthUserModel
        :param write_only: 是否只写入文件
        :param overwrite: 是否在写入时覆盖文件
        """

        json_config = self.model_to_json(
            model_class_name=model_class_name, app_name=app_name, app_desc=app_desc, version="1.0"
        )
        self.json_to_code(json_config=json_config, is_write=write_only, overwrite=overwrite)


if __name__ == "__main__":
    app = AppGenerate(verbose=False)

    # config = app.model_to_json(
    #     model_class_name="AuthRoleModel",
    #     app_name="auth_role",
    #     app_desc="角色",
    #     filename="role_data.json"
    # )
    # print(json.dumps(config, indent=4, ensure_ascii=False))

    # app.json_to_code(json_config_file="role_data.json", is_write=True, overwrite=False)

    app.model_to_code(
        model_class_name="AuthTestModel", app_name="auth_test", app_desc="测试", write_only=True, overwrite=True
    )
