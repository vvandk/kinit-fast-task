# @Version        : 1.0
# @Create Time    : 2024/4/16 15:34
# @File           : base_model.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr


class AsyncBaseORMModel(AsyncAttrs, DeclarativeBase):
    """
    创建声明式基本映射类
    稍后，我们将继承该类，创建每个 ORM 模型
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        将表名改为小写
        如果有自定义表名就取自定义，没有就取小写类名
        """
        table_name = cls.__tablename__
        if not table_name:
            model_name = cls.__name__
            ls = []
            for index, char in enumerate(model_name):
                if char.isupper() and index != 0:
                    ls.append("_")
                ls.append(char)
            table_name = "".join(ls).lower()
        return table_name
