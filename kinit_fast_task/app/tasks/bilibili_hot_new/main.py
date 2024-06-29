# @Version        : 1.0
# @Create Time    : 2024/5/20 上午9:59
# @File           : main.py
# @IDE            : PyCharm
# @Desc           : demo 任务
import asyncio

import httpx
import orjson
from kinit_fast_task.app.cruds.bilibili_hot_new import BilibiliHotNewListCURD
from kinit_fast_task.utils import log


class BilibiliHotNew:
    def __init__(self, task_id: str):
        """
        初始化 Demo 任务
        """
        self.task_id = task_id
        self.api_url = "https://v.api.aa1.cn/api/bilibili-rs/"

    async def __request_api(self):
        """
        异步请求 API 接口

        数据返回示例：

        {
            "code": 1,
            "msg": "获取成功",
            "time": "2024-05-10",
            "data": [
                {
                    "title": "吃亏是福？我爸总吃亏，被上汽大众赞助一台车",
                    "heat": "233.4万",
                    "link": "https://www.bilibili.com/video/av1754031639/"
                },
                ...
            ]
        }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, timeout=10, follow_redirects=True)
            if response.is_error:
                raise ValueError(f"任务：请求链接（{self.api_url}）失败, 状态码为：{response.status_code}")
            return orjson.loads(response.text)

    async def main(self, *args, **kwargs) -> str:
        """
        主入口函数
        :return:
        """
        try:
            response = await self.__request_api()
        except ValueError as e:
            log.error(e)
            return e.__str__()
        if response.get("code", 0) != 1:
            content = f"任务执行失败, code: {response.get('code', 0)}, msg: {response.get('msg', '')}"
            log.error(content)
            return content
        datas = response.get("data", [])
        if datas:
            # 数据入库
            await BilibiliHotNewListCURD().create_datas(datas)
        log.info("任务执行完成")
        return "任务执行完成"


if __name__ == "__main__":
    # 调试任务脚本，测试任务脚本功能
    # 推荐使用 PyCharm 执行, 执行时需设置工作目录为 kinit-fast-task 为根目录
    # 直接执行该脚本, 最方便的调试任务方法：
    #   - 确保执行工作目录为项目根目录：kinit-fast-task
    task = BilibiliHotNew("bilibili_hot_new")
    asyncio.run(task.main())
