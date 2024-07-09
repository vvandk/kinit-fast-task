# @Version        : 1.0
# @Create Time    : 2024/07/09
# @File           : params.py
# @IDE            : PyCharm
# @Desc           : 测试

from fastapi import Depends
from kinit_fast_task.app.depends.Paging import Paging, QueryParams


class PageParams(QueryParams):
    def __init__(self, params: Paging = Depends()):
        super().__init__(params)
