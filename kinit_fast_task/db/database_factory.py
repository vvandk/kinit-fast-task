# @Version        : 1.0
# @Create Time    : 2024/5/27 上午11:13
# @File           : database_factory.py
# @IDE            : PyCharm
# @Desc           : 数据库工厂类

from kinit_fast_task.db.async_base import AsyncAbstractDatabase
from kinit_fast_task.db.mongo.asyncio import MongoDatabase
from kinit_fast_task.db.orm.asyncio import ORMDatabase
from kinit_fast_task.db.redis.asyncio import RedisDatabase
from kinit_fast_task.utils.singleton import Singleton
from typing import Literal


class DBFactory(metaclass=Singleton):
    """
    数据库工厂类，使用单例模式来管理数据库实例的创建和获取

    :ivar _config_db: 存储数据库实例的字典，键为数据库类型和加载器名称的组合，值为数据库实例

    Methods
    -------
    get_db_instance(db_type, loader_name='default', db_url=None)
        获取指定类型和加载器名称的数据库实例，如果实例不存在则创建并加载到配置加载器

    register(loader_name, loader)
        在配置加载管理器中注册一个配置加载器

    remove(loader_name)
        从配置加载管理器中删除加载器

    clear()
        清空配置加载管理器
    """

    _config_db: dict[str, AsyncAbstractDatabase] = {}

    @classmethod
    def get_db_instance(
        cls, db_type: Literal["orm", "mongo", "redis"], *, loader_name: str = "default", db_url: str = None
    ) -> AsyncAbstractDatabase:
        """
        获取指定类型和加载器名称的数据库实例，如果实例不存在则创建并加载到配置加载器

        :param db_type: 数据库类型，可选值为 "orm", "mongo", "redis"
        :param loader_name: 配置加载器名称，第一次创建连接成功后，存入 _config_db，存入方式默认与 db_type 拼接
        :param db_url: 数据库连接地址
        :return:
        """
        db_key = f"{db_type}-{loader_name}"
        if db_key in cls._config_db:
            return cls._config_db[db_key]

        if db_type == "mongo":
            loader = MongoDatabase()
        elif db_type == "orm":
            loader = ORMDatabase()
        elif db_type == "redis":
            loader = RedisDatabase()
        else:
            raise ValueError(f"不存在的数据库类型: {db_type}")
        loader.create_connection(db_url)
        cls.register(db_key, loader)
        return loader

    @classmethod
    def register(cls, loader_name: str, loader: AsyncAbstractDatabase) -> None:
        """
        在配置加载管理器中注册一个配置加载器

        :param loader_name: 配置加载器名称
        :param loader: 配置加载器实例
        :return:
        """
        cls._config_db[loader_name] = loader

    @classmethod
    async def remove(cls, loader_name) -> bool:
        """
        从配置加载管理器中删除加载器

        :param loader_name: 配置加载器名称
        :return: 删除成功返回 True
        """
        if loader_name in cls._config_db:
            loader = cls._config_db.pop(loader_name)
            await loader.close_connection()

        return True

    @classmethod
    async def clear(cls) -> bool:
        """
        清空加载器

        :return: 清空成功返回 True
        """
        for loader in cls._config_db.values():
            await loader.close_connection()

        return True
