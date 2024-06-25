# @Version        : 1.0
# @Create Time    : 2022/11/3 17:23
# @File           : ip_manage.py
# @IDE            : PyCharm
# @Desc           : 获取IP地址归属地

"""
文档：https://user.ip138.com/ip/doc
IP查询第三方服务，有1000次的免费次数

JSONP请求示例（IPv4）
https://api.ip138.com/ip/?ip=58.16.180.3&datatype=jsonp&token=cc87f3c77747bccbaaee35006da1ebb65e0bad57

aiohttp 异步请求文档：https://docs.aiohttp.org/en/stable/client_quickstart.html
"""

import aiohttp
from kinit_fast_task.core import log
from pydantic import BaseModel


class IPLocationOut(BaseModel):
    ip: str | None = None
    address: str | None = None
    country: str | None = None
    province: str | None = None
    city: str | None = None
    county: str | None = None
    operator: str | None = None
    postal_code: str | None = None
    area_code: str | None = None


class IPManage:
    def __init__(self, token: str):
        self.token = token

    async def parse(self, ip: str):
        """
        IP 数据解析
        :param ip:
        :return: {'ret': 'ok', 'ip': '114.222.121.253','data': ['中国', '江苏', '南京', '秦淮区', '电信', '211100', '025']}
        """  # noqa E501
        out = IPLocationOut()
        out.ip = ip
        url = f"https://api.ip138.com/ip/?ip={ip}&datatype=jsonp&token={self.token}"
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.get(url) as resp:
                body = await resp.json()
                if body.get("ret") != "ok":
                    log.error(f"获取IP所属地失败：{body}")
                    return out
                data = body.get("data")
                out.address = f"{''.join(data[i] for i in range(0, 4))} {data[4]}"
                out.country = data[0]
                out.province = data[1]
                out.city = data[2]
                out.county = data[3]
                out.operator = data[4]
                out.postal_code = data[5]
                out.area_code = data[6]
                return out
