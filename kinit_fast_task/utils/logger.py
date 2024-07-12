import sys
from pathlib import Path
from typing import Any
from loguru import logger
from kinit_fast_task.config import settings
from kinit_fast_task.utils.singleton import Singleton


class TaskLogger:
    """
    任务日志
    """

    def __init__(self, log_filename: str, verbose: bool = False) -> None:
        self._log_filename = log_filename
        self._log_file_path = None
        self.verbose = verbose
        self._logger = logger

        self._configure_logging()

    def _configure_logging(self):
        """
        配置日志文件的存储和轮转。
        """

        # 添加日志文件路径
        self._log_file_path = Path(settings.system.LOG_PATH) / self._log_filename

        self._logger.add(
            self._log_file_path,  # 日志文件路径
            rotation="5 MB",  # 当日志文件达到该大小时，将切换到一个新的日志文件
            retention="3 days",  # 日志保留期限
            enqueue=True,  # 设置为True，日志消息会被放入队列中，异步写入文件，这样可以提高程序性能
            encoding="UTF-8",  # 日志文件的编码格式
            level="DEBUG",  # 设置日志级别为DEBUG，意味着DEBUG及以上级别的日志会被写入此文件
            mode="a",  # 如果文件已经存在，则追加内容
            filter=lambda record: record["extra"].get("filename") == self._log_filename,
        )

    def _log(self, level: str, *args: Any, is_verbose: bool = False, depth: int = 0) -> None:
        """
        记录日志消息

        Parameters
        ----------
        level: str
            日志级别
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        depth: int
            调用堆栈的深度，用于调整日志消息的来源
        """
        msg = " ".join(map(str, args))
        if is_verbose:
            if self.verbose:
                self._logger.bind(filename=self._log_filename).opt(depth=depth + 1).log(level, msg)
        else:
            self._logger.bind(filename=self._log_filename).opt(depth=depth + 1).log(level, msg)

    def debug(self, *args: Any, is_verbose: bool = False, depth: int = 0) -> None:
        """
        级别数值：10. 用于记录调试信息，帮助开发者调试程序

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        depth: int
            调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("DEBUG", *args, is_verbose=is_verbose, depth=depth + 1)

    def info(self, *args: Any, is_verbose: bool = False, depth: int = 0) -> None:
        """
        级别数值：20, 用于记录普通的信息，描述程序的正常运行情况

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        depth: int
            调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("INFO", *args, is_verbose=is_verbose, depth=depth + 1)

    def success(self, *args: Any, is_verbose: bool = False, depth: int = 0) -> None:
        """
        级别数值：25, 用于记录成功的操作，表示程序某些操作成功完成

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        depth: int
            调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("SUCCESS", *args, is_verbose=is_verbose, depth=depth + 1)

    def warning(self, *args: Any, is_verbose: bool = False, depth: int = 0) -> None:
        """
        级别数值：30, 用于记录警告信息，表示程序出现了不期望的情况，但仍然可以继续运行

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        depth: int
            调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("WARNING", *args, is_verbose=is_verbose, depth=depth + 1)

    def error(self, *args: Any, is_verbose: bool = False, depth: int = 0) -> None:
        """
        级别数值：40, 用于记录错误信息，表示程序遇到了严重的问题，无法执行某些功能

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        depth: int
            调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("ERROR", *args, is_verbose=is_verbose, depth=depth + 1)

    def critical(self, *args: Any, is_verbose: bool = False, depth: int = 0) -> None:
        """
        级别数值：50, 用于记录非常严重的错误，表示程序可能无法继续运行

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        depth: int
            调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("CRITICAL", *args, is_verbose=is_verbose, depth=depth + 1)

    def start(self, msg: str = "BEGIN", depth: int = 0) -> None:
        """
        输出任务开始信息

        Parameters
        ----------
        msg: str
            开始信息
        depth: int
            调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("INFO", "=======", depth=depth + 1)
        self._log("INFO", msg, depth=depth + 1)

    def end(self, msg: str = None, depth: int = 0) -> None:
        """
        输出任务结束信息

        Parameters
        ----------
        msg: str
            结束信息
        depth: int
            调用堆栈的深度，用于调整日志消息的来源
        """
        if msg:
            self._log("INFO", msg, depth=depth + 1)
        self._log("INFO", "==EOF==\n", depth=depth + 1)


class LoguruLogger(metaclass=Singleton):
    """
    LoguruLogger类用于封装loguru日志的配置，以便于灵活地设置日志文件、格式和级别。

    Loguru 常用的六种日志级别：

    1. DEBUG：级别数值：10. 用于记录调试信息，帮助开发者调试程序
    2. INFO：级别数值：20, 用于记录普通的信息，描述程序的正常运行情况
    3. SUCCESS：级别数值：25, 用于记录成功的操作，表示程序某些操作成功完成
    4. WARNING：级别数值：30, 用于记录警告信息，表示程序出现了不期望的情况，但仍然可以继续运行
    5. ERROR：级别数值：40, 用于记录错误信息，表示程序遇到了严重的问题，无法执行某些功能
    6. CRITICAL：级别数值：50, 用于记录非常严重的错误，表示程序可能无法继续运行

    Examples:
    --------
    >>> log.debug("This is a debug message")
    >>> log.info("This is an info message")
    >>> log.success("This is a success message")
    >>> log.warning("This is a warning message")
    >>> log.error("This is an error message")
    >>> log.critical("This is a critical message")

    具体其他配置 可自行参考 https://github.com/Delgan/loguru
    """

    def __init__(self):
        """
        初始化日志配置
        """
        self._log_file_path = None
        self._task_loaders = {}

    def _configure_logging(self) -> None:
        """
        配置日志文件的存储和轮转。
        """
        # 确保日志目录存在, 不存在则创建
        self._log_file_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            self._log_file_path,  # 日志文件路径
            rotation="5 MB",  # 当日志文件达到该大小时，将切换到一个新的日志文件
            retention="3 days",  # 日志保留期限
            enqueue=True,  # 设置为True，日志消息会被放入队列中，异步写入文件，这样可以提高程序性能
            encoding="UTF-8",  # 日志文件的编码格式
            level="DEBUG",  # 设置日志级别为DEBUG，意味着DEBUG及以上级别的日志会被写入此文件
            mode="a",  # 如果文件已经存在，则追加内容
            filter=lambda record: record["extra"].get("filename") == self._log_file_path.stem,
        )
        # 自定义格式
        # format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}"

    def run(self):
        """
        主入口程序
        """

        # 禁用全局 logger 的默认处理器
        logger.remove()

        if settings.system.LOG_CONSOLE_OUT:
            # 添加控制台输出
            logger.add(sys.stdout, level="DEBUG")

        self._log_file_path = Path(settings.system.REQUEST_LOG_FILE_PATH)

        # 配置日志文件
        self._configure_logging()

    def _log(self, level: str, *args: Any, depth: int = 0) -> None:
        """
        记录日志消息

        :param level: 日志级别
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        msg = " ".join(map(str, args))
        logger.bind(filename=self._log_file_path.stem).opt(depth=depth + 1).log(level, msg)

    def debug(self, *args: Any, depth: int = 0) -> None:
        """
        级别数值：10. 用于记录调试信息，帮助开发者调试程序

        :param args: 消息列表
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("DEBUG", *args, depth=depth + 1)

    def info(self, *args: Any, depth: int = 0) -> None:
        """
        级别数值：20, 用于记录普通的信息，描述程序的正常运行情况

        :param args: 消息列表
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("INFO", *args, depth=depth + 1)

    def success(self, *args: Any, depth: int = 0) -> None:
        """
        级别数值：25, 用于记录成功的操作，表示程序某些操作成功完成

        :param args: 消息列表
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("SUCCESS", *args, depth=depth + 1)

    def warning(self, *args: Any, depth: int = 0) -> None:
        """
        级别数值：30, 用于记录警告信息，表示程序出现了不期望的情况，但仍然可以继续运行

        :param args: 消息列表
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("WARNING", *args, depth=depth + 1)

    def error(self, *args: Any, depth: int = 0) -> None:
        """
        级别数值：40, 用于记录错误信息，表示程序遇到了严重的问题，无法执行某些功能

        :param args: 消息列表
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("ERROR", *args, depth=depth + 1)

    def critical(self, *args: Any, depth: int = 0) -> None:
        """
        级别数值：50, 用于记录非常严重的错误，表示程序可能无法继续运行

        :param args: 消息列表
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        self._log("CRITICAL", *args, depth=depth + 1)

    def get_task_log(
        self, log_filename: str, *, msg: str = "BEGIN", verbose: bool = False, depth: int = 0
    ) -> TaskLogger:
        """
        获取独立任务日志管理器

        如果文件名称已存在任务日志加载器(_task_loaders)中，则直接返回对应的任务日志实例，反之则创建后返回

        :param log_filename: 日志文件名称
        :param msg: title
        :param verbose: 是否输出详细日志
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        if log_filename in self._task_loaders:
            task_log = self._task_loaders[log_filename]
        else:
            task_log = TaskLogger(log_filename=log_filename, verbose=verbose)
            self._task_loaders[log_filename] = task_log
            print("new")
        return task_log

    def remove_task_log(self, log_filename: str) -> None:
        """
        删除指定的任务日志管理器
        """
        if log_filename in self._task_loaders:
            del self._task_loaders[log_filename]


# 创建LoguruLogger实例，可以根据需要调整参数
log = LoguruLogger()
log.run()

if __name__ == "__main__":
    log.debug("main, This is a debug message")
    log.info("main, This is an info message")

    task_loger = log.get_task_log(log_filename="test.log", verbose=True)
    task_loger.start()
    task_loger.debug("This is a debug message", is_verbose=True)
    task_loger.info("This is an info message")
    task_loger.success("This is a success message", is_verbose=True)
    log.remove_task_log(log_filename="test.log")
    task_loger = log.get_task_log(log_filename="test.log", verbose=True)
    task_loger.warning("This is a warning message")
    task_loger.error("This is an error message")
    task_loger.critical("This is a critical message")
    task_loger.end()
