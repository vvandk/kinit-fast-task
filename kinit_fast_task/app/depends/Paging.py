# @Version        : 1.0
# @Create Time    : 2024/3/24 12:07
# @File           : Paging.py
# @IDE            : PyCharm
# @Desc           : 描述信息

"""
类依赖项-官方文档：https://fastapi.tiangolo.com/zh/tutorial/dependencies/classes-as-dependencies/
"""

import copy

from fastapi import Query


class QueryParams:
    def __init__(self, params=None):
        if params:
            self.page = params.page
            self.limit = params.limit
            self.v_order = params.v_order
            self.v_order_field = params.v_order_field

    def dict(self, exclude: list[str] = None) -> dict:
        """
        属性转字典
        :param exclude: 需排除的属性
        :return:
        """
        result = copy.deepcopy(self.__dict__)
        if exclude:
            for item in exclude:
                try:
                    del result[item]
                except KeyError:
                    pass
        return result

    def to_count(self, exclude: list[str] = None) -> dict:
        """
        去除基础查询参数
        :param exclude: 另外需要去除的属性
        :return:
        """
        params = self.dict(exclude=exclude)
        del params["page"]
        del params["limit"]
        del params["v_order"]
        del params["v_order_field"]
        return params


class Paging(QueryParams):
    """
    列表分页
    """

    def __init__(
        self,
        page: int = Query(1, description="当前页数"),
        limit: int = Query(10, description="每页多少条数据"),
        v_order_field: str = Query(None, description="排序字段"),
        v_order: str = Query(None, description="排序规则"),
    ):
        super().__init__()
        self.page = page
        self.limit = limit
        self.v_order = v_order
        self.v_order_field = v_order_field
