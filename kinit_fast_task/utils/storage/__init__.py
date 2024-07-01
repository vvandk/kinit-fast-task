# @Version        : 1.0
# @Update Time    : 2024/6/30
# @File           : __init__.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息

from kinit_fast_task.utils.storage.storage_factory import StorageFactory
from kinit_fast_task.utils.storage.abs import AbstractStorage
from kinit_fast_task.utils.storage.local.local import LocalStorage
from kinit_fast_task.utils.storage.oss.oss import OSSStorage
from kinit_fast_task.utils.storage.kodo.kodo import KodoStorage
