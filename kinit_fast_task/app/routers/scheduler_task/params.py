# @Version        : 1.0
# @Create Time    : 2024/05/17 14:37
# @File           : params.py
# @IDE            : PyCharm
# @Desc           :

from fastapi import Depends
from kinit_fast_task.app.depends.Paging import Paging, QueryParams


class PageParams(QueryParams):
    def __init__(self, params: Paging = Depends()):
        super().__init__(params)
