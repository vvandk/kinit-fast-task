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
    celery 使用

    官方文档：https://docs.celeryq.dev/en/stable/index.html
    GitHub：https://github.com/celery/celery
    """

    def __init__(self):
        self._app = Celery(settings.system.PROJECT_NAME)

    def main(self):
        """
        主入口程序
        """
        self._app.conf.update(
            # 指定任务队列的消息代理
            broker_url=settings.task.CELERY_BROKER.unicode_string(),
            # 指定存储任务结果的中间件
            result_backend=settings.task.CELERY_RESULT_BACKEND.unicode_string(),
            # 用于指定任务的序列化方式，即在任务发送到消息队列之前，如何将任务数据转换为字节流
            # 常用的序列化方式有 json 和 pickle
            # json：使用 JSON 序列化，优点是易于阅读和调试，但只能序列化基础数据类型（如字符串、数字、列表、字典等）
            # pickle：使用 Python 的 pickle 模块进行序列化，可以处理复杂的 Python 对象，但生成的字节流不可读
            task_serializer='json',
            # 用于指定任务结果的序列化方式，即在任务结果存储到结果中间件之前，如何将结果数据转换为字节流
            # 常用的序列化格式同样是 json 和 pickle
            # json：适用于结果是基础数据类型的情况，安全且易于阅读
            # pickle：适用于结果是复杂 Python 对象的情况
            result_serializer='json',
            # 用于指定 Celery Worker 可以接受的内容类型 这是为了防止 Worker 处理不受信任或不期望的序列化格式，从而提高安全性和一致性
            # 常见的值包括 json 和 pickle
            # ['json']：表示 Worker 只接受 JSON 格式的消息
            # ['json', 'pickle']：表示 Worker 同时接受 JSON 和 Pickle 格式的消息
            accept_content=['json'],  # 只接受 JSON 格式
            # 指定时区
            timezone='Asia/Shanghai',
            # 是否启用 UTC 时间
            enable_utc=False
        )

        self._app.autodiscover_tasks(settings.task.CELERY_TASK_PAG)

        return self._app


celery_app = CeleryApp().main()


# celery 启动：
# celery -A kinit_fast_task.celery_worker worker -l info  # 默认多进程方式, 不支持 win
# celery -A kinit_fast_task.celery_worker worker -l info --pool=prefork  # 多进程方式, 不支持 win
# celery -A kinit_fast_task.celery_worker worker -l info --pool=threads  # 多线程方式, 无法接收停止信号
# celery -A kinit_fast_task.celery_worker:celery_app worker -l info --pool=solo  # 单进程方式, 无法接收停止信号
