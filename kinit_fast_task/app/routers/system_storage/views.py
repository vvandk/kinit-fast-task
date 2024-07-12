# @Version        : 1.0
# @Create Time    : 2024/7/8
# @File           : views.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息


from fastapi import APIRouter, UploadFile, File

from kinit_fast_task.utils.response import RestfulResponse, ResponseSchema
from kinit_fast_task.utils.storage import StorageFactory

router = APIRouter(prefix="/system/storage", tags=["系统存储管理"])


@router.post("/local/image/create", response_model=ResponseSchema[str], summary="上传图片到本地目录")
async def local_image_create(file: UploadFile = File(..., description="图片文件")):
    storage = StorageFactory.get_instance("local")
    result = await storage.save_image(file, path="image")
    return RestfulResponse.success(data=result)


@router.post("/local/audio/create", response_model=ResponseSchema[str], summary="上传音频到本地目录")
async def local_audio_create(file: UploadFile = File(..., description="音频文件")):
    storage = StorageFactory.get_instance("local")
    path = f"audio/{storage.get_today_timestamp()}"
    result = await storage.save_audio(file, path=path)
    return RestfulResponse.success(data=result)


@router.post("/local/video/create", response_model=ResponseSchema[str], summary="上传视频到本地目录")
async def local_video_create(file: UploadFile = File(..., description="视频文件")):
    storage = StorageFactory.get_instance("local")
    path = f"video/{storage.get_today_timestamp()}"
    result = await storage.save_video(file, path=path)
    return RestfulResponse.success(data=result)


@router.post("/local/create", response_model=ResponseSchema[str], summary="上传文件到本地目录")
async def local_create(file: UploadFile = File(..., description="上传文件")):
    storage = StorageFactory.get_instance("local")
    result = await storage.save(file)
    return RestfulResponse.success(data=result)


@router.post("/oss/image/create", response_model=ResponseSchema[str], summary="上传图片到 OSS")
async def oss_image_create(file: UploadFile = File(..., description="图片文件")):
    storage = StorageFactory.get_instance("oss")
    result = await storage.save(file)
    return RestfulResponse.success(data=result)


@router.post("/temp/image/create", response_model=ResponseSchema[str], summary="上传临时文件到本地临时目录")
async def temp_image_create(file: UploadFile = File(..., description="上传文件")):
    storage = StorageFactory.get_instance("temp")
    result = await storage.save(file)
    return RestfulResponse.success(data=result)
