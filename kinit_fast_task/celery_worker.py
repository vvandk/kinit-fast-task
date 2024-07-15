# @Version        : 1.0
# @Update Time    : 2024/7/13
# @File           : celery_worker.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息

from celery import Celery
from kinit_fast_task.config import settings
from kinit_fast_task.utils.singleton import Singleton


class CeleryApp(metaclass=Singleton):
    """
    celery 初始化

    官方文档：https://docs.celeryq.dev/en/stable/index.html
    GitHub：https://github.com/celery/celery
    """

    def __init__(self):
        self._app = Celery(settings.system.PROJECT_NAME)

    def __set_config(self):
        """
        配置解释:

        Backends and Brokers 官方文档：https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html
        Backends Settings 官方文档：https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-result-backend-settings

        配置与默认值官方文档：https://docs.celeryq.dev/en/stable/userguide/configuration.html#configuration-and-defaults
        官方调优指南：https://docs.celeryq.dev/en/stable/userguide/optimizing.html#guide-optimizing

        任务调用详细官方文档：https://docs.celeryq.dev/en/stable/userguide/calling.html#guide-calling
        守护进程官方文档：https://docs.celeryq.dev/en/stable/userguide/daemonizing.html#daemonizing
        worker 启动命令详细官方文档：https://docs.celeryq.dev/en/stable/userguide/workers.html#guide-workers

        任务状态：https://docs.celeryq.dev/en/stable/userguide/tasks.html#built-in-states
        任务 hook: https://docs.celeryq.dev/en/stable/userguide/tasks.html#handlers

        broker_url: 指定任务队列的消息代理中间件，可选择 redis 或者 RabbitMQ
            Redis: 适用于快速传输小消息, 大消息可能会阻塞系统
            RabbitMQ: 处理大消息比 Redis 更好, 但如果有大量消息快速进入, 扩展可能成为问题, 除非 RabbitMQ 运行在非常大规模, 否则应该考虑使用 Redis
        result_backend: 指定存储任务结果的中间件, 推荐选择 Redis 或者 SQLAlchemy(Mysql, PostgreSQL)
            Redis: 超快的键值存储, 使其在获取任务调用结果时非常高效. 由于 Redis 的设计, 您需要考虑存储数据的内存限制, 以及如何处理数据持久性. 如果结果持久性很重要, 请考虑使用其他数据库作为后端
            SQLAlchemy: SQL 数据库提供了可靠的持久性，适合需要长时间存储结果的应用, 与 Redis 这样的内存数据库相比，SQL 数据库的读写性能可能稍逊一筹，尤其是在高并发环境下
            注意：RabbitMQ（作为代理）和 Redis（作为后端）通常一起使用。如果需要更长时间的结果存储持久性，请考虑使用 PostgreSQL 或 MySQL（通过 SQLAlchemy）
        task_serializer: 用于指定任务结果的序列化方式，即在任务结果存储到结果中间件之前，如何将结果数据转换为字节流, 推荐选择 json 或者 pickle
            json：使用 JSON 序列化，优点是易于阅读和调试，但只能序列化基础数据类型（如字符串、数字、列表、字典等）
            pickle：使用 Python 的 pickle 模块进行序列化，可以处理复杂的 Python 对象，但生成的字节流不可读
        result_serializer: 用于指定任务结果的序列化方式，即在任务结果存储到结果中间件之前，如何将结果数据转换为字节流, 推荐选择 json 或者 pickle
            json：适用于结果是基础数据类型的情况，安全且易于阅读
            pickle：适用于结果是复杂 Python 对象的情况
        accept_content: 用于指定 Celery Worker 可以接受的内容类型 这是为了防止 Worker 处理不受信任或不期望的序列化格式，从而提高安全性和一致性
            ['json']：表示 Worker 只接受 JSON 格式的消息
            ['json', 'pickle']：表示 Worker 同时接受 JSON 和 Pickle 格式的消息
        timezone: 指定时区
        enable_utc: 是否启用 UTC 时间
        """
        self._app.conf.update(
            broker_url=settings.task.CELERY_BROKER.unicode_string(),
            result_backend=settings.task.CELERY_RESULT_BACKEND.unicode_string(),
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
            timezone='Asia/Shanghai',
            enable_utc=False
        )

    def main(self):
        """
        主入口程序
        """
        self.__set_config()
        self._app.autodiscover_tasks(settings.task.CELERY_TASK_PAG, related_name=False)

        return self._app


celery_app = CeleryApp().main()


# celery 启动：
# celery -A kinit_fast_task.celery_worker worker -l info  # 默认多进程方式, 不支持 win
# celery -A kinit_fast_task.celery_worker worker -l info --pool=prefork  # 多进程方式, 不支持 win
# celery -A kinit_fast_task.celery_worker worker -l info --pool=threads  # 多线程方式, 无法接收停止信号
# celery -A kinit_fast_task.celery_worker:celery_app worker -l info --pool=solo  # 单进程方式, 无法接收停止信号
