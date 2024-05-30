# @Version        : 1.0
# @Create Time    : 2022/10/9 17:09
# @File           : tools.py
# @IDE            : PyCharm
# @Desc           : 工具类

import datetime
import random
import re
import string
import importlib
import subprocess
from kinit_fast_task.core.logger import log
from kinit_fast_task.core.exception import CustomException


def camel_to_snake(name: str) -> str:
    """
    将大驼峰命名（CamelCase）转换为下划线命名（snake_case）
    在大写字母前添加一个空格，然后将字符串分割并用下划线拼接
    :param name: 大驼峰命名（CamelCase）
    :return:
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name: str) -> str:
    """
    将下划线命名（snake_case）转换为大驼峰命名（CamelCase）
    根据下划线分割，然后将字符串转为第一个字符大写后拼接
    :param name: 下划线命名（snake_case）
    :return:
    """
    # 按下划线分割字符串
    words = name.split("_")
    # 将每个单词的首字母大写，然后拼接
    return "".join(word.capitalize() for word in words)


def test_password(password: str) -> str | bool:
    """
    检测密码强度
    :param password: 原始密码
    :return:
    """
    if len(password) < 8 or len(password) > 16:
        return "长度需为8-16个字符,请重新输入。"
    else:
        for i in password:
            if 0x4E00 <= ord(i) <= 0x9FA5 or ord(i) == 0x20:  # Ox4e00等十六进制数分别为中文字符和空格的Unicode编码
                return "不能使用空格、中文，请重新输入。"
        else:
            key = 0
            key += 1 if bool(re.search(r"\d", password)) else 0
            key += 1 if bool(re.search(r"[A-Za-z]", password)) else 0
            key += 1 if bool(re.search(r"\W", password)) else 0
            if key >= 2:
                return True
            else:
                return "至少含数字/字母/字符2种组合，请重新输入。"


def list_dict_find(options: list[dict], key: str, value: any) -> dict | None:
    """
    字典列表查找
    :param options:
    :param key:
    :param value:
    :return:
    """
    return next((item for item in options if item.get(key) == value), None)


def get_time_interval(start_time: str, end_time: str, interval: int, time_format: str = "%H:%M:%S") -> list:
    """
    获取时间间隔
    :param end_time: 结束时间
    :param start_time: 开始时间
    :param interval: 间隔时间（分）
    :param time_format: 字符串格式化，默认：%H:%M:%S
    """
    if start_time.count(":") == 1:
        start_time = f"{start_time}:00"
    if end_time.count(":") == 1:
        end_time = f"{end_time}:00"
    start_time = datetime.datetime.strptime(start_time, "%H:%M:%S")
    end_time = datetime.datetime.strptime(end_time, "%H:%M:%S")
    time_range = []
    while end_time > start_time:
        time_range.append(start_time.strftime(time_format))
        start_time = start_time + datetime.timedelta(minutes=interval)
    return time_range


def generate_string(length: int = 8) -> str:
    """
    生成随机字符串
    :param length: 字符串长度
    """
    return "".join(random.sample(string.ascii_letters + string.digits, length))


def import_modules(modules: list, desc: str, **kwargs):
    """
    通过反射执行方法
    :param modules:
    :param desc:
    :param kwargs:
    :return:
    """
    for module in modules:
        if not module:
            continue
        try:
            module_pag = importlib.import_module(module[0 : module.rindex(".")])
            getattr(module_pag, module[module.rindex(".") + 1 :])(**kwargs)
        except ModuleNotFoundError as e:
            log.error(f"AttributeError：导入{desc}失败，模块：{module}，详细报错信息：{e}")
        except AttributeError as e:
            log.error(f"ModuleNotFoundError：导入{desc}失败，模块方法：{module}，详细报错信息：{e}")


async def import_modules_async(modules: list, desc: str, **kwargs):
    """
    通过反射执行异步方法
    :param modules:
    :param desc:
    :param kwargs:
    :return:
    """
    for module in modules:
        if not module:
            continue
        try:
            module_pag = importlib.import_module(module[0 : module.rindex(".")])
            await getattr(module_pag, module[module.rindex(".") + 1 :])(**kwargs)
        except ModuleNotFoundError as e:
            log.error(f"AttributeError：导入{desc}失败，模块：{module}，详细报错信息：{e}")
        except AttributeError as e:
            log.error(f"ModuleNotFoundError：导入{desc}失败，模块方法：{module}，详细报错信息：{e}")


def exec_shell_command(
    command: str, error_text: str = "命令执行失败", cwd: str = None, shell: bool = True, check: bool = False
) -> str:
    """
    执行 shell 命令
    :param command:
    :param error_text: 报错时的文本输出内容
    :param cwd: 命令执行工作目录
    :param shell:
        当 shell=True 时，Python 将使用系统的默认 shell（比如在 Windows 下是 cmd.exe，而在 Unix/Linux 下是 /bin/sh）来执行指定的命令。
        当 shell=False 时，Python 直接执行指定的命令，不经过 shell 解释器。
        使用 shell=True 时，你可以像在命令行中一样使用一些特殊的 shell 功能，比如重定向 (>)、管道 (|) 等。
        但要注意，使用 shell=True 也可能存在一些安全风险，因为它可以执行更复杂的命令，并且可能受到 shell 注入攻击的影响。
    :param check: 是否忽略错误
    :return:
    """  # noqa: E501
    result = subprocess.run([item for item in command.split(" ")], shell=shell, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0 and not check:
        raise CustomException(
            f"{error_text}，执行命令：{command}，结果 Code：{result.returncode}，报错内容：{result.stdout}"
        )
    return result.stdout


def ruff_format_code():
    """
    使用 ruff 格式化生成的代码
    """
    try:
        exec_shell_command("ruff check --fix", check=True)
        exec_shell_command("ruff format", check=True)
        log.info("已完成代码格式化")
    except Exception as e:
        log.error(f"代码格式化失败: {e}")
