# @Version        : 1.0
# @Create Time    : 2023/6/14 15:55
# @File           : code.py
# @IDE            : PyCharm
# @Desc           : 发送验证码短信

import datetime
from redis.asyncio import Redis
from .aliyun import AliyunSMS
from kinit_fast_task.utils import log
from kinit_fast_task.core import CustomException


class CodeSMS(AliyunSMS):
    def __init__(
        self,
        rd: Redis,
        telephone: str,
        access_key_id: str,
        access_key_secret: str,
        sign_name: str,
        template_code: str,
        send_interval: int = 60,
        valid_time: int = 180,
    ):
        """
        :param rd:
        :param telephone:
        :param access_key_id:
        :param access_key_secret:
        :param sign_name:
        :param template_code:
        :param send_interval:
        :param valid_time:
        """
        super().__init__(
            [telephone], access_key_id, access_key_secret, sign_name, template_code, send_interval, valid_time
        )
        self.rd = rd
        self.telephone = telephone

    async def main_async(self) -> bool:
        """
        主程序入口，异步方式

        redis 对象必填
        """

        send_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if await self.rd.get(self.telephone + "_flag_"):
            log.error(f"{send_time} {self.telephone} 短信发送失败，短信发送过于频繁")
            raise CustomException(msg="短信发送频繁", code=400)
        result = await self._send_async(self.telephone)
        if result:
            await self.rd.set(self.telephone, self.code, self.valid_time)
            await self.rd.set(self.telephone + "_flag_", self.code, self.send_interval)
        return result

    async def check_sms_code(self, code: str) -> bool:
        """
        检查短信验证码是否正确
        """
        if code and code == await self.rd.get(self.telephone):
            await self.rd.delete(self.telephone)
            await self.rd.delete(self.telephone + "_flag_")
            return True
        return False

    def _get_template_param(self, **kwargs) -> str:
        """
        获取模板参数

        可以被子类继承的受保护的私有方法
        """
        self.code = kwargs.get("code", self.get_code())
        template_param = f'{"code":"{self.code}"}'
        return template_param
