# @Version        : 1.0
# @Create Time    : 2022/11/3 17:23
# @File           : count.py
# @IDE            : PyCharm
# @Desc           : 计数


from redis.asyncio.client import Redis


class Count:
    """
    redis 计数
    """

    def __init__(self, rd: Redis, key):
        self.rd = rd
        self.key = key

    async def add(self, ex: int = None) -> int:
        """
        增加
        :param ex:
        :return: 总数
        """
        await self.rd.set(self.key, await self.get_count() + 1, ex=ex)
        return await self.get_count()

    async def subtract(self, ex: int = None) -> int:
        """
        减少
        :param ex:
        :return:
        """
        await self.rd.set(self.key, await self.get_count() - 1, ex=ex)
        return await self.get_count()

    async def get_count(self) -> int:
        """
        获取当前总数
        :return:
        """
        number = await self.rd.get(self.key)
        if number:
            return int(number)
        return 0

    async def reset(self) -> None:
        """
        重置计数
        :return:
        """
        await self.rd.set(self.key, 0)

    async def delete(self) -> None:
        """
        删除 key
        :return:
        """
        await self.rd.delete(self.key)
