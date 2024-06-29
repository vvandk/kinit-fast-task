# @Version        : 1.0
# @Create Time    : 2024/4/1 13:58
# @File           : asyncio.py
# @IDE            : PyCharm
# @Desc           : mongodb


from kinit_fast_task.db.async_base import AsyncAbstractDatabase
from kinit_fast_task.config import settings
import redis.asyncio as redis
from kinit_fast_task.core import CustomException
from kinit_fast_task.utils import log


class RedisDatabase(AsyncAbstractDatabase):
    """
    安装： poetry add redis
    GitHub: https://github.com/redis/redis-py
    异步连接官方文档：https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html
    """

    def __init__(self):
        """
        实例化 Redis 数据库连接
        """
        self._engine: redis.ConnectionPool | None = None

    def create_connection(self, db_url: str = None) -> None:
        """
        创建 redis 数据库连接

        官方文档：https://redis.readthedocs.io/en/stable/connections.html#connectionpool-async
        :return:
        """
        # 创建一个异步连接池
        # decode_responses: 自动解码响应为字符串
        # protocol: 指定使用 RESP3 协议
        # max_connections: 最大连接数
        if not db_url:
            db_url = settings.db.REDIS_DB_URL.unicode_string()
        self._engine = redis.ConnectionPool.from_url(
            db_url, encoding="utf-8", decode_responses=True, protocol=3, max_connections=10
        )

    def db_getter(self) -> redis.Redis:
        """
        返回一个从连接池获取的 Redis 客户端
        :return:
        """
        if not self._engine:
            raise CustomException("未连接 Redis 数据库！")
        return redis.Redis(connection_pool=self._engine)

    async def db_transaction_getter(self):
        """
        获取数据库事务

        :return:
        """
        raise NotImplementedError("未实现 Redis 事务功能！")

    async def test_connection(self) -> None:
        """
        测试数据库连接
        :return:
        """
        rd = self.db_getter()
        try:
            result = await rd.ping()
            log.info(f"Redis Ping successful: {result}")
        except Exception as e:
            log.error(f"Redis Server Connection Fail, content: {e}")
            raise

    async def close_connection(self) -> None:
        """
        关闭 redis 连接池
        :return:
        """
        if not self._engine:
            return None
        await self._engine.aclose()
