# @Version        : 1.0
# @Update Time    : 2024/6/30
# @File           : file_factory.py
# @IDE            : PyCharm
# @Desc           : 文件上传工厂类
from typing import Literal

from kinit_fast_task.utils.storage import AbstractStorage
from kinit_fast_task.utils.singleton import Singleton
from kinit_fast_task.utils.storage import LocalStorage
from kinit_fast_task.utils.storage import OSSStorage
from kinit_fast_task.utils.storage import KodoStorage


class StorageFactory(metaclass=Singleton):

    _config_loader: dict[str, AbstractStorage] = {}

    @classmethod
    def get_instance(cls, loader_type: Literal["local", "oss", "kodo"]) -> AbstractStorage:
        """
        获取指定类型和加载器名称的文件存储实例，如果实例不存在则创建并加载到配置加载器
        """
        if loader_type in cls._config_loader:
            return cls._config_loader[loader_type]

        if loader_type == "local":
            loader = LocalStorage()
        elif loader_type == "kodo":
            loader = KodoStorage()
        elif loader_type == "oss":
            loader = OSSStorage()
        else:
            raise ValueError(f"不存在的文件存储类型: {loader_type}")
        cls.register(loader_type, loader)
        return loader

    @classmethod
    def register(cls, loader_name: str, loader: AbstractStorage) -> None:
        """
        在配置加载管理器中注册一个配置加载器

        :param loader_name: 配置加载器名称
        :param loader: 配置加载器实例
        :return:
        """
        cls._config_loader[loader_name] = loader

    @classmethod
    async def remove(cls, loader_name) -> bool:
        """
        从配置加载管理器中删除加载器

        :param loader_name: 配置加载器名称
        :return: 删除成功返回 True
        """
        if loader_name in cls._config_loader:
            cls._config_loader.pop(loader_name)

        return True

    @classmethod
    async def clear(cls) -> bool:
        """
        清空加载器

        :return: 清空成功返回 True
        """
        cls._config_loader.clear()

        return True
