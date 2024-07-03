# @Version        : 1.0
# @Create Time    : 2024/7/1
# @File           : oss.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息
import os
import uuid
from urllib.parse import urljoin

import oss2
from fastapi import UploadFile
from oss2.models import PutObjectResult

from kinit_fast_task.core import CustomException
from kinit_fast_task.utils.storage import AbstractStorage
from kinit_fast_task.config import settings
from kinit_fast_task.utils import log


class OSSStorage(AbstractStorage):
    """
    阿里云对象存储

    常见报错：https://help.aliyun.com/document_detail/185228.htm?spm=a2c4g.11186623.0.0.6de530e5pxNK76#concept-1957777
    官方文档：https://help.aliyun.com/document_detail/32026.html

    使用Python SDK时，大部分操作都是通过oss2.Service和oss2.Bucket两个类进行
    oss2.Service类用于列举存储空间
    oss2.Bucket类用于上传、下载、删除文件以及对存储空间进行各种配置
    """

    def __init__(self):
        # 阿里云账号AccessKey拥有所有API的访问权限，风险很高
        # 官方建议创建并使用RAM用户进行API访问或日常运维, 请登录RAM控制台创建RAM用户
        auth = oss2.Auth(settings.oss.ACCESS_KEY_ID, settings.oss.ACCESS_KEY_SECRET)
        # 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
        self.bucket = oss2.Bucket(auth, settings.oss.ENDPOINT, settings.oss.BUCKET)
        self.baseUrl = settings.oss.BASE_URL

    async def save(self, file: UploadFile, path: str | None = None, *, accept: list = None, max_size: int = 50) -> str:
        """
        保存通用文件

        :param file: 文件
        :param path: 上传路径
        :param accept: 支持的文件类型
        :param max_size: 支持的文件最大值，单位 MB
        :return: 文件访问地址，POSIX 风格路径, 示例：https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/20240703/1719969784NPMyq0Jv.jpg
        """
        await self.validate_file(file, max_size=max_size, mime_types=accept)
        if path is None:
            path = self.get_today_timestamp()

        # 生成随机文件名称
        filename = f"{uuid.uuid4().hex}.{os.path.splitext(file.filename)[1]}"

        file_path = f"{path}/{filename}"
        result = self.bucket.put_object(file_path, await file.read())
        assert isinstance(result, PutObjectResult)
        if result.status != 200:
            log.error(f"文件上传到OSS失败, 状态码：{result.status}")
            raise CustomException("文件上传到OSS失败！")
        return urljoin(self.baseUrl, file_path)
