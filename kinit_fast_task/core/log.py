import os
from typing import Any
from loguru import logger
from kinit_fast_task.config import settings


class LoguruLogger:
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

    def __init__(
        self,
        log_dir: str,
        info_filename: str = 'info',
        error_filename: str = 'error',
        retention: str = '3 days',
        encoding: str = 'UTF-8'
    ):
        """
        初始化日志配置

        Parameters
        ----------
        log_dir: str
            日志文件存储的目录
        info_filename: str
            信息日志文件的名称前缀
        error_filename: str
            错误日志文件的名称前缀
        retention: str
            日志文件的保留期限
        encoding: str
            日志文件的编码
        """
        self.base_dir = log_dir
        self.info_filename = info_filename
        self.error_filename = error_filename
        self.retention = retention
        self.encoding = encoding
        self.verbose = False
        self._logger = logger

    def _ensure_log_dir(self):
        """
        确保日志目录存在，如果不存在则创建。
        """
        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)

    def _configure_logging(self):
        """
        配置日志文件的存储和轮转。
        """
        info_path = os.path.join(self.base_dir, f'{self.info_filename}.log')
        error_path = os.path.join(self.base_dir, f'{self.error_filename}.log')

        self._logger.add(
            info_path,  # 日志文件路径
            rotation="00:00",  # 轮转时间设置，每天午夜进行日志轮转
            retention=self.retention,  # 日志保留期限
            enqueue=True,  # 设置为True，日志消息会被放入队列中，异步写入文件，这样可以提高程序性能
            encoding=self.encoding,  # 日志文件的编码格式
            level="INFO"  # 设置日志级别为INFO，意味着INFO及以上级别的日志会被写入此文件
        )

        self._logger.add(
            error_path,
            rotation="00:00",
            retention=self.retention,
            enqueue=True,
            encoding=self.encoding,
            level="ERROR"
        )

    def main(self, console: bool = True):
        """
        主入口程序

        Parameters
        ----------
        console: bool, optional
            是否将日志输出到控制台
        """
        if not console:
            # 移除默认的控制台输出
            self._logger.remove()

        # 确保日志目录存在
        self._ensure_log_dir()

        # 配置日志文件
        self._configure_logging()

    def _log(self, level: str, *args: Any, is_verbose: bool = False) -> None:
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
        """
        msg = " ".join(map(str, args))
        if is_verbose:
            if self.verbose:
                self._logger.opt(depth=2).log(level, msg)
        else:
            self._logger.opt(depth=2).log(level, msg)

    def debug(self, *args: Any, is_verbose: bool = False) -> None:
        """
        级别数值：10. 用于记录调试信息，帮助开发者调试程序

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        """
        self._log("DEBUG", *args, is_verbose=is_verbose)

    def info(self, *args: Any, is_verbose: bool = False) -> None:
        """
        级别数值：20, 用于记录普通的信息，描述程序的正常运行情况

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        """
        self._log("INFO", *args, is_verbose=is_verbose)

    def success(self, *args: Any, is_verbose: bool = False) -> None:
        """
        级别数值：25, 用于记录成功的操作，表示程序某些操作成功完成

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        """
        self._log("SUCCESS", *args, is_verbose=is_verbose)

    def warning(self, *args: Any, is_verbose: bool = False) -> None:
        """
        级别数值：30, 用于记录警告信息，表示程序出现了不期望的情况，但仍然可以继续运行

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        """
        self._log("WARNING", *args, is_verbose=is_verbose)

    def error(self, *args: Any, is_verbose: bool = False) -> None:
        """
        级别数值：40, 用于记录错误信息，表示程序遇到了严重的问题，无法执行某些功能

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        """
        self._log("ERROR", *args, is_verbose=is_verbose)

    def critical(self, *args: Any, is_verbose: bool = False) -> None:
        """
        级别数值：50, 用于记录非常严重的错误，表示程序可能无法继续运行

        Parameters
        ----------
        args: Any
            消息列表
        is_verbose: bool
            是否属于详细类日志
        """
        self._log("CRITICAL", *args, is_verbose=is_verbose)

    def start(self, msg: str = "BEGIN", verbose: bool = False) -> None:
        """
        任务程序，输出任务开始信息

        Parameters
        ----------
        msg: str
            开始信息
        verbose: bool
            是否属于详细类日志
        """
        self._log("INFO", f"======================={msg}==========================")
        self.update_verbose(verbose)

    def end(self, msg: str = "EOF") -> None:
        """
        任务程序，输出任务结束信息

        Parameters
        ----------
        msg: str
            结束信息
        """
        self._log("INFO", f"======================={msg}==========================\n\n")
        self.update_verbose(False)

    def update_verbose(self, verbose: bool) -> None:
        """
        更新 verbose 状态

        Parameters
        ----------
        verbose: bool
            是否属于详细类日志
        """
        self.verbose = verbose


# 创建LoguruLogger实例，可以根据需要调整参数
log = LoguruLogger(log_dir=settings.system.LOG_PATH)
log.main(console=settings.system.LOG_CONSOLE_OUT)


if __name__ == '__main__':
    log.start("hello")



