# @Version        : 1.0
# @Create Time    : 2024/7/1
# @File           : kodo.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息
from fastapi import UploadFile

from kinit_fast_task.utils.storage import AbstractStorage


class KodoStorage(AbstractStorage):
    async def save(self, file: UploadFile, *, path: str | None = None, accept: list = None, max_size: int = 50) -> str:
        """
        保存通用文件

        :param file: 文件
        :param path: 上传路径
        :param accept: 支持的文件类型
        :param max_size: 支持的文件最大值，单位 MB
        :return: 文件访问地址
        """
        raise NotImplementedError("未实现七牛云文件上传功能")
