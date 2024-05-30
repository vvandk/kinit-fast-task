# @Version        : 1.0
# @Create Time    : 2024/4/1 13:58
# @File           : async_base.py
# @IDE            : PyCharm
# @Desc           : SQLAlchemy ORM 会话管理

from collections.abc import AsyncGenerator
from sqlalchemy import text

from kinit_fast_task.core.exception import CustomException
from kinit_fast_task.db.async_base import AsyncAbstractDatabase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from kinit_fast_task.config import settings
from kinit_fast_task.core.logger import log


class ORMDatabase(AsyncAbstractDatabase):
    """
    SQLAlchemy ORM 连接 会话管理
    安装： poetry add sqlalchemy[asyncio]
    官方文档：https://docs.sqlalchemy.org/en/20/intro.html#installation
    """

    def __init__(self):
        """
        实例化 SQLAlchemy ORM 数据库连接
        """
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def create_connection(self, db_url: str = None) -> None:
        """
        创建数据库引擎与会话工厂

        :param db_url: 数据库连接
        :return:
        """
        """
        # 创建数据库引擎与连接池并初始化相关的数据库连接信息。
        # 这个引擎对象会负责管理连接池中的连接资源，包括从池中获取连接、执行 SQL 命令、处理事务、连接回收等操作。
        # echo=False：当设置为 True 时，引擎将会在控制台输出所有生成的 SQL 语句
        # echo_pool=False：当设置为 True 时，连接池相关的操作（如连接的获取和释放）也会被输出到控制台。
        # pool_pre_ping=False：如果设置为 True，每次从连接池获取连接前都会执行一个轻量级的 SQL 命令（如 SELECT 1），以检查连接是否仍然有效。
        # pool_recycle=-1：此设置导致池在给定的秒数后重新使用连接。默认为-1，即没有超时。例如，将其设置为3600意味着在一小时后重新使用连接。
        # pool_size=5：在连接池内保持打开的连接数。pool_size设置为0表示没有限制
        # max_overflow 参数用于配置连接池中允许的连接 "溢出" 数量。这个参数用于在高负载情况下处理连接请求的峰值。
        # 当连接池的所有连接都在使用中时，如果有新的连接请求到达，连接池可以创建额外的连接来满足这些请求，最多创建的数量由 max_overflow 参数决定。
        """  # noqa E501
        if not db_url:
            db_url = settings.db.ORM_DATABASE_URL.unicode_string()
        self._engine = create_async_engine(
            db_url,
            echo=settings.db.ORM_DB_ECHO,
            echo_pool=False,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=5,
            connect_args={},
        )

        """
        # 创建会话工厂
        # autocommit=False: 这表明事务不会在每次操作后自动提交。在这种模式下，需要手动提交事务，这给予了更好的控制，可以在执行多个操作后作为一个整体提交。
        # autoflush=False: 这意味着在执行查询之前，SQLAlchemy 不会自动刷新（发送）当前会话中的更改到数据库。这可以避免不必要的数据库操作，提高性能。
        # bind=async_engine: 这里绑定了异步引擎 async_engine，该引擎负责与数据库进行异步通信。
        # expire_on_commit=True: 设置为 True 表示在提交事务后，会话中的所有实例都将过期并在下次访问时自动重新加载。
        # class_=AsyncSession: 指定会话类为 AsyncSession，这是进行异步操作的会话类型。
        """  # noqa E501
        self._session_factory = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine, expire_on_commit=True, class_=AsyncSession
        )

    async def db_transaction_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """
        从数据库会话工厂中获取数据库事务，它将在单个请求中使用，最后在请求完成后将其关闭

        函数的返回类型被注解为 AsyncGenerator[AsyncSession, None]
        其中 AsyncSession 是生成的值的类型，而 None 表示异步生成器没有终止条件。

        :return:
        """  # noqa E501
        if not self._engine or not self._session_factory:
            raise CustomException("未连接 SQLAlchemy ORM 数据库！")
        async with self._session_factory() as session:
            """
            开始一个新的事务，这个事务将在该异步块结束时自动关闭。
            如果块中的代码正常执行（没有引发异常），事务会在离开该异步上下文管理器时自动提交，也就是自动执行 commit。
            如果块中的代码引发异常，事务会自动回滚。
            因此，在这个上下文管理器中，你不需要手动调用 commit 方法；事务的提交或回滚将根据执行过程中是否发生异常自动进行。
            这是 session.begin() 上下文管理器的一个优点，因为它简化了事务的管理，确保事务能在适当的时机正确提交或回滚。
            """  # noqa E501
            async with session.begin():
                yield session

    def db_getter(self) -> AsyncSession:
        """
        获取数据库 session

        :return:
        """
        if not self._engine or not self._session_factory:
            raise CustomException("未连接 SQLAlchemy ORM 数据库！")
        return self._session_factory()

    async def test_connection(self) -> None:
        """
        测试数据库连接

        :return:
        """
        session = self.db_getter()
        try:
            result = await session.execute(text("SELECT now();"))
            log.info(f"ORM DB Ping successful: {result.scalar()}")
        except Exception as e:
            log.error(f"ORM DB Connection Fail, content: {e}")
            raise
        finally:
            await session.close()

    async def close_connection(self) -> None:
        """
        关闭数据库引擎

        :return:
        """
        if self._engine:
            await self._engine.dispose()
