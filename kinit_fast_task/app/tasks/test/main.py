#!/usr/bin/python
# @version        : 1.0
# @Create Time    : 2023/6/21 10:08
# @File           : mian.py
# @IDE            : PyCharm
# @desc           : 测试任务
import asyncio
import datetime


class Test:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    async def main(self, *args, **kwargs) -> str:
        """
        主入口函数
        :return:
        """
        now_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{now_datetime}, 定时任务测试实例，实例参数为: {self.name}, {self.age}")

        # 增加异步耗时
        await asyncio.sleep(2)

        print(f"{now_datetime}, 定时任务测试实例，方法参数为: {args}, {kwargs}")
        return "任务执行完成"


if __name__ == "__main__":
    # 调试任务脚本，测试任务脚本功能
    # 推荐使用 PyCharm 执行, 执行时需设置工作目录为 kinit-fast-task 为根目录
    # 直接执行该脚本, 最方便的调试任务方法：
    #   - 确保执行工作目录为项目根目录：kinit-fast-task
    task = Test(name="kinit-fast-task", age=2)
    asyncio.run(task.main())
