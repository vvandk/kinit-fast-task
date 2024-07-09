# @Version        : 1.0
# @Create Time    : 2024/7/8
# @File           : temp.py
# @IDE            : PyCharm
# @Desc           : 临时文件存储

import os
import uuid

from aiopathlib import AsyncPath
from fastapi import UploadFile

from kinit_fast_task.utils.storage import AbstractStorage
from kinit_fast_task.config import settings


class TempStorage(AbstractStorage):
    async def save(self, file: UploadFile, *, path: str | None = None, accept: list = None, max_size: int = 50) -> str:
        """
        保存通用文件

        :param file: 文件
        :param path: 上传路径
        :param accept: 支持的文件类型
        :param max_size: 支持的文件最大值，单位 MB
        :return: 文件保存地址，POSIX 风格路径, 示例：/temp/word/test.docs
        """
        await self.validate_file(file, max_size=max_size, mime_types=accept)
        if path is None:
            path = self.get_today_timestamp()

        # 生成随机文件名称
        filename = f"{uuid.uuid4().hex}{os.path.splitext(file.filename)[1]}"

        save_path = AsyncPath(settings.storage.TEMP_PATH) / path / filename
        if not await save_path.parent.exists():
            await save_path.parent.mkdir(parents=True, exist_ok=True)
        await save_path.write_bytes(await file.read())
        return save_path.as_posix()
