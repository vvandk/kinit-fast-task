# @Version        : 1.0
# @Create Time    : 2024/7/1
# @File           : local.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息
import os
import uuid

from aiopathlib import AsyncPath
from fastapi import UploadFile

from kinit_fast_task.utils.storage import AbstractStorage
from kinit_fast_task.config import settings


class LocalStorage(AbstractStorage):

    async def save_image(self, file: UploadFile, path: str | None = None) -> None:
        """
        保存图片文件
        """
        await self.save(file, path, accept=self.IMAGE_ACCEPT, max_size=10)

    async def save_audio(self, file: UploadFile, path: str | None = None) -> None:
        """
        保存音频文件
        """
        await self.save(file, path, accept=self.AUDIO_ACCEPT, max_size=50)

    async def save_video(self, file: UploadFile, path: str | None = None) -> None:
        """
        保存视频文件
        """
        await self.save(file, path, accept=self.VIDEO_ACCEPT, max_size=50)

    async def save(self, file: UploadFile, path: str | None = None, *, accept: list = None, max_size: int = 50) -> None:
        """
        保存通用文件
        """
        if accept is None:
            accept = self.ALL_ACCEPT
        await self.validate_file(file, max_size=max_size, mime_types=accept)
        if path is None:
            path = self.get_today_timestamp()
        filename = f"{uuid.uuid4()}.{os.path.splitext(file.filename)[1]}"
        path = AsyncPath(settings.system.STATIC_PATH) / path / filename
        if not await path.parent.exists():
            await path.parent.mkdir(parents=True, exist_ok=True)
        await path.write_bytes(await file.read())
        return
