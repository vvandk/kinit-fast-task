import os
import time
from loguru import logger
from kinit_fast_task.config import settings
from kinit_fast_task.utils.singleton import Singleton


class LoguruLogger(metaclass=Singleton):
    """
    LoguruLogger类用于封装loguru日志的配置，以便于灵活地设置日志文件、格式和级别。

    具体其他配置 可自行参考 https://github.com/Delgan/loguru
    """

    def __init__(
        self,
        log_dir: str,
        info_filename: str = "info",
        error_filename: str = "error",
        retention: str = "3 days",
        encoding: str = "UTF-8",
    ):
        """
        初始化日志配置

        :param log_dir: 日志文件存储的目录
        :param info_filename: 信息日志文件的名称前缀
        :param error_filename: 错误日志文件的名称前缀
        :param retention: 日志文件的保留期限
        :param encoding: 日志文件的编码
        """
        self.base_dir = log_dir
        self.info_filename = info_filename
        self.error_filename = error_filename
        self.retention = retention
        self.encoding = encoding

        if not settings.system.LOG_CONSOLE_OUT:
            # 移除默认的控制台输出
            logger.remove()

        # 确保日志目录存在
        self._ensure_log_dir()

        # 配置日志文件
        self._configure_logging()

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
        date_str = time.strftime("%Y-%m-%d")
        info_path = os.path.join(self.base_dir, f"{self.info_filename}_{date_str}.log")
        error_path = os.path.join(self.base_dir, f"{self.error_filename}_{date_str}.log")

        logger.add(
            info_path,  # 日志文件路径
            rotation="00:00",  # 轮转时间设置，每天午夜进行日志轮转
            retention=self.retention,  # 日志保留期限
            enqueue=True,  # 设置为True，日志消息会被放入队列中，异步写入文件，这样可以提高程序性能
            encoding=self.encoding,  # 日志文件的编码格式
            level="INFO",  # 设置日志级别为INFO，意味着INFO及以上级别的日志会被写入此文件
        )

        logger.add(
            error_path, rotation="00:00", retention=self.retention, enqueue=True, encoding=self.encoding, level="ERROR"
        )

    @staticmethod
    def get_logger():
        """
        获取 logger
        """
        return logger


# 创建LoguruLogger实例，可以根据需要调整参数
log = LoguruLogger(log_dir=settings.system.LOG_PATH).get_logger()
