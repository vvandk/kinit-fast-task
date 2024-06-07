from pathlib import Path
from kinit_fast_task.config import settings


class AppGenerate:
    """
    生成 APP 代码:

        1. 基于 ORM Model 生成 Json 配置文件
        2. 基于 JSON 配置文件生成代码
        3. 基于 ORM Model 生成代码（先生成 JSON 配置后基于 JSON 生成代码）
    """

    SCRIPT_PATH = Path(settings.system.BASE_PATH) / "scripts" / "app_generate"

    def __init__(self):
        """
        初始化 AppGenerate 类
        """
        pass

    def model_to_json(self, model_module: str, version: str = "1.0") -> dict:
        """
        基于单个 model 输出 JSON 配置文件

        :param model_module: model 模块, 示例：auth_user_model.AuthUserModel
        :param version: json 版本
        :return: dict
        """


if __name__ == "__main__":
    generate = AppGenerate()
