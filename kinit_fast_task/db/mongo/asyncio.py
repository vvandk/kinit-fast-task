# @Version        : 1.0
# @Create Time    : 2024/4/1 13:58
# @File           : asyncio.py
# @IDE            : PyCharm
# @Desc           : mongodb
from urllib.parse import urlparse, parse_qs

from kinit_fast_task.db.async_base import AsyncAbstractDatabase
from kinit_fast_task.config import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorClientSession
from kinit_fast_task.core import CustomException
from pymongo.errors import ServerSelectionTimeoutError
from kinit_fast_task.utils import log


class MongoDatabase(AsyncAbstractDatabase):
    """
    安装：poetry add motor
    官方文档：https://motor.readthedocs.io/en/stable/index.html
    官方文档：https://motor.readthedocs.io/en/stable/tutorial-asyncio.html#

    Motor 中使用事务
    Motor与MongoDB事务一起使用需要MongoDB 4.0及以上版本，并且数据库需要配置为复制集（replica set）模式

    MongoDB 复制集
    MongoDB的复制集（replica set）模式是一种高可用性和数据冗余解决方案
    复制集由一组MongoDB实例组成，这些实例维护相同的数据集副本，提供数据冗余和故障转移能力
    复制集至少包含一个主节点（primary）和一个或多个从节点（secondary）
    在复制集中，主节点负责处理所有写操作，而从节点则从主节点复制数据并保持数据的冗余
    """

    def __init__(self):
        """
        实例化 MongoDB 数据库连接
        """
        self._engine: AsyncIOMotorClient | None = None
        self._db: AsyncIOMotorDatabase | None = None

    def create_connection(self, db_url: str = None) -> None:
        """
        创建数据库连接

        :return:
        """
        # maxPoolSize：连接池中的最大连接数。这决定了最多可以有多少个活跃的连接同时存在。
        # minPoolSize：连接池中的最小连接数。即使在空闲时，连接池也会尝试保持这么多的连接打开。
        # maxIdleTimeMS：连接可以保持空闲状态的最大毫秒数，之后连接会被关闭。这有助于避免保持长时间不使用的连接。
        # serverSelectionTimeoutMS 参数设置了服务器选择的超时时间（以毫秒为单位），在这里设置为 5000 毫秒（5 秒）
        if not db_url:
            db_url = settings.db.MONGO_DB_URL.unicode_string()
        self._engine = AsyncIOMotorClient(
            db_url, maxPoolSize=10, minPoolSize=2, maxIdleTimeMS=300000, serverSelectionTimeoutMS=5000
        )

        # 从数据库链接中提取数据库名称
        parsed_url = urlparse(db_url)
        query_params = parse_qs(parsed_url.query)
        db_name = query_params.get("authSource")[0]

        self._db = self._engine[db_name]
        if self._db is None:
            raise CustomException("MongoDB 数据库连接失败！")

    async def db_transaction_getter(self) -> AsyncIOMotorClientSession:
        """
        获取数据库事务

        :return:
        """
        async with await self._engine.start_session() as session:
            async with session.start_transaction():
                yield session

    def db_getter(self) -> AsyncIOMotorDatabase:
        """
        获取数据库连接

        :return:
        """
        if not self._engine:
            raise CustomException("未连接 MongoDB 数据库！")
        if self._db is None:
            raise CustomException("MongoDB 数据库连接失败！")
        return self._db

    async def test_connection(self) -> None:
        """
        测试数据库连接

        :return:
        """
        db = self.db_getter()
        try:
            # 发送 ping 命令以测试连接
            result = await db.command("ping")
            log.info(f"MongoDB Ping successful: {result}")
        except ServerSelectionTimeoutError as e:
            log.error(f"MongoDB Server Connection Timed Out, content: {e}")
            raise

    async def close_connection(self) -> None:
        """
        关闭连接池

        :return:
        """
        if self._engine:
            self._engine.close()
