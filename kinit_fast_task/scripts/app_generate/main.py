import importlib
import json
from typing import Literal

from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.config import settings
from kinit_fast_task.scripts.app_generate.v1.model_to_json import ModelToJson as ModelToJsonV1
from kinit_fast_task.scripts.app_generate.v1.generate_code import GenerateCode as GenerateCodeV1


class AppGenerate:
    """
    生成 APP 代码:

        1. 基于 ORM Model 生成 Json 配置文件
        2. 基于 JSON 配置文件生成代码
        3. 基于 ORM Model 生成代码（先生成 JSON 配置后基于 JSON 生成代码）
    """

    SCRIPT_PATH = settings.BASE_PATH / "scripts" / "app_generate"
    VERSIONS = Literal["1.0"]

    def __init__(self):
        """
        初始化 AppGenerate 类
        """
        pass

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
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)

    @staticmethod
    def read_json(filename: str) -> dict:
        """
        读取 json 文件

        :param filename:
        :return:
        """
        with open(filename, 'r', encoding='utf-8') as json_file:
            json_config = json.load(json_file)
            return json_config

    def model_to_json(
        self,
        *,
        model_class_name: str,
        app_name: str,
        app_desc: str,
        version: VERSIONS = "1.0",
        filename: str = None
    ) -> dict:
        """
        基于单个 model 输出 JSON 配置文件

        :param model_class_name: Model 类名, 示例：AuthUserModel
        :param app_name: app 名称, 示例：auth_user
        :param app_desc: app 描述, 示例：AuthUserModel
        :param version: json 版本
        :param filename: 文件名称
        :return: dict
        """
        model = self.model_mapping(model_class_name)
        if version == "1.0":
            mtj = ModelToJsonV1(model, app_name, app_desc)
        else:
            raise NotImplementedError(f"version {version} not implemented")

        json_config = mtj.to_json()
        self.write_json(filename, json_config)

        return json_config

    def json_to_code(self, json_config_file: str) -> bool:
        """
        基于 JSON 配置文件生成代码

        :param json_config_file: json 配置文件地址
        :return:
        """
        json_config = self.read_json(json_config_file)
        version = json_config["version"]
        print(json_config)
        if version == "1.0":
            gc = GenerateCodeV1(json_config)
        else:
            raise NotImplementedError(f"version {version} not implemented")
        gc.generate()


if __name__ == "__main__":
    app = AppGenerate()
    config = app.model_to_json(
        model_class_name="AuthUserModel",
        app_name="auth_user",
        app_desc="用户功能",
        filename="data.json"
    )
    # print(json.dumps(config, indent=4, ensure_ascii=False))

    app.json_to_code("data.json")
