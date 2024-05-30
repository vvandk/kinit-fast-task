# @Version        : 1.0
# @Create Time    : 2024/4/7 10:11
# @File           : __init__.py
# @IDE            : PyCharm
# @Desc           : 自动遍历导入所有 models

from pathlib import Path
import importlib

from kinit_fast_task.core.logger import log
from kinit_fast_task.utils.tools import snake_to_camel

# 排除的 Model 文件
excluded_files = {"__init__.py"}

# 动态加载各目录下的已存在 __init__.py 文件中的 Model
for file in Path(__file__).parent.iterdir():
    if file.is_file() and file.name.endswith(".py") and file.name not in excluded_files:
        file_name = file.name[:-3]  # 去除文件的.py扩展名得到模块名
        module = importlib.import_module(f".{file_name}", package=__name__)

        if "_to_" in file_name:
            class_name = file_name
        else:
            class_name = snake_to_camel(file_name)

        try:
            cls = getattr(module, class_name)
            globals()[class_name] = cls
        except AttributeError as e:
            log.error(f"导入 Model 失败，未在 {file_name}.py 文件中找到 {class_name} Model，错误：{e}")
