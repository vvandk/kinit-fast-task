# @Version        : 1.0
# @Create Time    : 2024/4/7 10:11
# @File           : __init__.py
# @IDE            : PyCharm
# @Desc           : 自动遍历导入所有 models
from pathlib import Path
import importlib
from kinit_fast_task.core import log
import ast


def find_classes_ending_with_model(file_path: Path) -> list[str]:
    """
    读取文件，查找出以Model结尾的class名称
    """
    try:
        tree = ast.parse(file_path.read_bytes(), filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError) as e:
        log.error(f"解析 Model 文件失败 {file_path}, 报错内容: {e}")
        return []

    return [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and node.name.endswith('Model')
    ]


def import_models_from_directory(directory: Path, excluded: set) -> None:
    """
    从指定目录导入符合条件的 Model 类
    """
    for file in directory.glob("*.py"):
        if file.name in excluded:
            continue

        module_name = file.stem
        try:
            module = importlib.import_module(f".{module_name}", package=__name__)
            class_names = [module_name] if "_to_" in module_name else find_classes_ending_with_model(file)

            for class_name in class_names:
                try:
                    cls = getattr(module, class_name)
                    globals()[class_name] = cls
                    # log.info(f"成功引入 Model: {cls}")
                except AttributeError as e:
                    log.error(f"导入 Model 失败，未在 {module_name}.py 文件中找到 {class_name} Model，错误：{e}")
        except ImportError as e:
            log.error(f"导入模块 {module_name} 失败，错误：{e}")


# 排除的 Model 文件
excluded_files = {"__init__.py"}

# 动态加载各目录下的已存在 __init__.py 文件中的 Model
import_models_from_directory(Path(__file__).parent, excluded_files)

