import uuid
from pathlib import Path
from typing import Any
from loguru import logger
from kinit_fast_task.config import settings
from kinit_fast_task.utils.singleton import Singleton


class TaskLogger:
    """
    任务日志
    """

    def __init__(self, verbose: bool = False) -> None:
        self.task_log_id = str(uuid.uuid4())
        self.verbose = verbose
        self._logger = logger

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
        msg = f"{self.task_log_id} - {msg}"
        if is_verbose:
            if self.verbose:
                self._logger.opt(depth=depth + 1).log(level, msg)
        else:
            self._logger.opt(depth=depth + 1).log(level, msg)

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
        self._verbose = False
        self._logger = logger

    def _configure_logging(self, log_file_path: str | Path) -> None:
        """
        配置日志文件的存储和轮转。
        """

        self._logger.add(
            log_file_path,  # 日志文件路径
            rotation="5 MB",  # 当日志文件达到该大小时，将切换到一个新的日志文件
            retention="3 days",  # 日志保留期限
            enqueue=True,  # 设置为True，日志消息会被放入队列中，异步写入文件，这样可以提高程序性能
            encoding="UTF-8",  # 日志文件的编码格式
            level="DEBUG",  # 设置日志级别为DEBUG，意味着DEBUG及以上级别的日志会被写入此文件
            mode="a",  # 如果文件已经存在，则追加内容
        )
        # 自定义格式
        # format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}"

    def remove_console(self):
        """
        移除默认的控制台输出
        """
        try:
            self._logger.remove(0)
        except ValueError:
            pass

    def get_log_path(self) -> Path:
        """
        获取日志文件路径
        """
        return self._log_file_path

    def run(self, log_file_path: str | None = None, console: bool = settings.system.LOG_CONSOLE_OUT):
        """
        主入口程序

        Parameters
        ----------
        log_file_path: str
            日志文件存储的地址
        console: bool, optional
            是否将日志输出到控制台
        """
        if log_file_path is None:
            log_file_path = settings.system.LOG_PATH

        self.remove_console() if not console else None

        self._log_file_path = Path(log_file_path)

        # 确保日志目录存在, 不存在则创建
        self._log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # 配置日志文件
        self._configure_logging(self._log_file_path)

    def _log(self, level: str, *args: Any, depth: int = 0) -> None:
        """
        记录日志消息

        :param level: 日志级别
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        msg = " ".join(map(str, args))
        self._logger.opt(depth=depth + 1).log(level, msg)

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

    @staticmethod
    def create_task(msg: str = "BEGIN", verbose: bool = False, depth: int = 0) -> TaskLogger:
        """
        输出任务开始信息

        :param msg: title
        :param verbose: 是否输出详细日志
        :param depth: 调用堆栈的深度，用于调整日志消息的来源
        """
        _task_log = TaskLogger(verbose)
        _task_log.info("=======", depth=depth + 1)
        _task_log.info(msg, depth=depth + 1)
        return _task_log


# 创建LoguruLogger实例，可以根据需要调整参数
log = LoguruLogger()
log.run()


if __name__ == "__main__":
    log.debug("main, This is a debug message")
    log.info("main, This is an info message")

    task_log = log.create_task(verbose=True)
    task_log.debug("This is a debug message", is_verbose=True)
    task_log.info("This is an info message")
    task_log.success("This is a success message", is_verbose=True)
    task_log.warning("This is a warning message")
    task_log.error("This is an error message")
    task_log.critical("This is a critical message")
    task_log.end()
