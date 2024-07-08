# @Version        : 1.0
# @Create Time    : 2024/7/1
# @File           : abs.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息
import datetime
from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile

from kinit_fast_task.core import CustomException


class AbstractStorage(ABC):
    """
    数据库操作抽象类
    """

    IMAGE_ACCEPT = ["image/png", "image/jpeg", "image/gif", "image/x-icon"]
    VIDEO_ACCEPT = ["video/mp4", "video/mpeg"]
    AUDIO_ACCEPT = ["audio/wav", "audio/mp3", "audio/m4a", "audio/wma", "audio/ogg", "audio/mpeg", "audio/x-wav"]
    ALL_ACCEPT = [*IMAGE_ACCEPT, *VIDEO_ACCEPT, *AUDIO_ACCEPT]

    async def save_image(self, file: UploadFile, *, path: str | None = None, max_size: int = 10) -> str:
        """
        保存图片文件
        """
        return await self.save(file, path=path, accept=self.IMAGE_ACCEPT, max_size=max_size)

    async def save_audio(self, file: UploadFile, *, path: str | None = None, max_size: int = 50) -> str:
        """
        保存音频文件
        """
        return await self.save(file, path=path, accept=self.AUDIO_ACCEPT, max_size=max_size)

    async def save_video(self, file: UploadFile, *, path: str | None = None, max_size: int = 50) -> str:
        """
        保存视频文件
        """
        return await self.save(file, path=path, accept=self.VIDEO_ACCEPT, max_size=max_size)

    @abstractmethod
    async def save(self, file: UploadFile, *, path: str | None = None, accept: list = None, max_size: int = 50) -> str:
        """
        保存通用文件

        :param file: 文件
        :param path: 上传路径
        :param accept: 支持的文件类型
        :param max_size: 支持的文件最大值，单位 MB
        :return: 文件访问地址，POSIX 风格路径, 示例：/media/word/test.docs
        """

    @classmethod
    async def validate_file(cls, file: UploadFile, *, max_size: int = None, mime_types: list = None) -> bool:
        """
        验证文件是否符合格式

        :param file: 文件
        :param max_size: 文件最大值，单位 MB
        :param mime_types: 支持的文件类型
        """
        if mime_types is None:
            mime_types = cls.ALL_ACCEPT
        if max_size:
            size = len(await file.read()) / 1024 / 1024
            if size > max_size:
                raise CustomException(f"上传文件过大，不能超过{max_size}MB")
            await file.seek(0)
        if mime_types:
            if file.content_type not in mime_types:
                raise CustomException(f"上传文件格式错误，只支持 {','.join(mime_types)} 格式!")
        return True

    @classmethod
    def get_today_timestamp(cls) -> str:
        """
        获取当天时间戳
        :return:
        """
        return str(int((datetime.datetime.now().replace(hour=0, minute=0, second=0)).timestamp()))
