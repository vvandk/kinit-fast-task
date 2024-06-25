# @Version        : 1.0
# @Create Time    : 2024/6/14 下午6:58
# @File           : generate_code.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息

from kinit_fast_task.scripts.app_generate.v1.json_config_schema import JSONConfigSchema


class GenerateCode:

    def __init__(self, json_config: dict):
        self.json_config = JSONConfigSchema(**json_config)

    def generate(self):
        pass
