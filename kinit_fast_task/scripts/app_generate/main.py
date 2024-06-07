import importlib
import json

from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.config import settings
from kinit_fast_task.scripts.app_generate.utils.model_to_json import ModelToJson


class AppGenerate:
    """
    生成 APP 代码:

        1. 基于 ORM Model 生成 Json 配置文件
        2. 基于 JSON 配置文件生成代码
        3. 基于 ORM Model 生成代码（先生成 JSON 配置后基于 JSON 生成代码）
    """

    SCRIPT_PATH = settings.BASE_PATH / "scripts" / "app_generate"

    def __init__(self):
        """
        初始化 AppGenerate 类
        """
        pass

    @staticmethod
    def model_mapping(model_class_name) -> type[AbstractORMModel]:
        """
        映射 ORM Model

        :return: ORM Model 类
        """
        module = importlib.import_module(f"{settings.system.PROJECT_NAME}.app.models")
        return getattr(module, model_class_name)

    def model_to_json(self, model_class_name: str, app_name: str, app_desc: str, version: str = "1.0") -> dict:
        """
        基于单个 model 输出 JSON 配置文件

        :param model_class_name: Model 类名, 示例：AuthUserModel
        :param app_name: app 名称, 示例：auth_user
        :param app_desc: app 描述, 示例：AuthUserModel
        :param version: json 版本
        :return: dict
        """
        model = self.model_mapping(model_class_name)
        mtj = ModelToJson(model, app_name, app_desc)
        # try:
        json_config = getattr(mtj, f"to_json_{version.replace('.', '_')}")()
        # except AttributeError:
        #     raise AttributeError(f"不存在的 Version：{version}！")
        return json_config


if __name__ == "__main__":
    app = AppGenerate()
    config = app.model_to_json(model_class_name="AuthUserModel", app_name="auth_user", app_desc="用户功能")
    print(json.dumps(config, indent=4, ensure_ascii=False))
