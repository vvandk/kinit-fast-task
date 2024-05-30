# @Version        : 1.0
# @Create Time    : 2023/6/14 15:26
# @File           : aliyun.py
# @IDE            : PyCharm
# @Desc           : 最新版阿里云短信服务发送程序（Python版本）2022-11-08

"""
短信 API 官方文档：https://help.aliyun.com/document_detail/419298.html?spm=5176.25163407.help.dexternal.6ff2bb6ercg9x3
发送短信 官方文档：https://help.aliyun.com/document_detail/419273.htm?spm=a2c4g.11186623.0.0.36855d7aRBSwtP
Python SDK 官方文档：https://help.aliyun.com/document_detail/215764.html?spm=a2c4g.11186623.0.0.6a0c4198XsBJNW

环境要求
Python 3
安装 SDK 核心库 OpenAPI ，使用pip安装包依赖:
poetry add alibabacloud_tea_openapi
poetry add alibabacloud_dysmsapi20170525
"""

import random
import re
from kinit_fast_task.core.exception import CustomException
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from kinit_fast_task.core.logger import log
import datetime


class AliyunSMS:
    # 返回错误码对应：
    docs = "https://help.aliyun.com/document_detail/101346.html"

    def __init__(
        self,
        telephones: list[str],
        access_key_id: str,
        access_key_secret: str,
        sign_name: str,
        template_code: str,
        send_interval: int = 60,
        valid_time: int = 180,
    ) -> None:
        """
        初始化配置
        :param telephones: 接收手机号列表
        :param access_key_id: 阿里云账号 AccessKey ID
        :param access_key_secret: 阿里云账号 AccessKey Secret
        :param sign_name: 短信签名
        :param template_code: 短信模板 code
        :param send_interval: 发送频率
        :param valid_time: 有效时间
        """
        super().__init__()
        self.telephones = self.check_telephones_format(telephones)
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.sign_name = sign_name
        self.template_code = template_code
        self.send_interval = send_interval
        self.valid_time = valid_time
        self.client = self.create_client()

    async def main_async(self, **kwargs) -> list[bool]:
        """
        主程序入口，异步方式
        :param kwargs: 模板格式化参数
        :return:
        """
        result = []
        for telephone in self.telephones:
            result.append(await self._send_async(telephone, **kwargs))
        return result

    async def _send_async(self, telephone: str, **kwargs) -> bool:
        """
        发送短信
        :param telephone: 接收手机号
        :param kwargs: 模板格式化参数
        :return:
        """
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=telephone,
            sign_name=self.sign_name,
            template_code=self.template_code,
            template_param=self._get_template_param(**kwargs),
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            resp = await self.client.send_sms_with_options_async(send_sms_request, runtime)
            return self._validation(telephone, resp)
        except Exception as e:
            print(e.__str__())
            return False

    def _get_template_param(self, **kwargs) -> str:
        """
        获取模板参数
        可以被子类继承的受保护的私有方法
        """
        raise NotImplementedError("该方法应该被重写！")

    def _validation(self, telephone: str, resp: dysmsapi_20170525_models.SendSmsResponse) -> bool:
        """
        验证结果并返回
        """
        send_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if resp.body.code == "OK":
            log.info(f"{send_time} {telephone} 短信发送成功，返回code：{resp.body.code}")
            return True
        else:
            log.error(f"{send_time} {telephone} 短信发送失败，返回code：{resp.body.code}，请参考文档：{self.doc}")
            return False

    @staticmethod
    def get_code(length: int = 6, blend: bool = False) -> str:
        """
        随机获取短信验证码
        短信验证码只支持数字，不支持字母及其他符号
        :param length: 验证码长度
        :param blend: 是否 字母+数字 混合
        """
        code = ""  # 创建字符串变量,存储生成的验证码
        for _i in range(length):  # 通过for循环控制验证码位数
            num = random.randint(0, 9)  # 生成随机数字0-9
            if blend:  # 需要字母验证码,不用传参,如果不需要字母的,关键字alpha=False
                upper_alpha = chr(random.randint(65, 90))
                lower_alpha = chr(random.randint(97, 122))
                # 随机选择其中一位
                num = random.choice([num, upper_alpha, lower_alpha])
            code = code + str(num)
        return code

    @classmethod
    def check_telephones_format(cls, telephones: list[str]) -> list[str]:
        """
        同时检查多个手机号格式是否合法
        不合法就会抛出异常
        :param telephones:
        :return:
        """
        for telephone in telephones:
            cls.check_telephone_format(telephone)
        return telephones

    @staticmethod
    def check_telephone_format(telephone: str) -> str:
        """
        检查手机号格式是否合法
        不合法就会抛出异常
        :param telephone:
        :return:
        """
        regex_telephone = r"^1(3\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8[0-9]|9[0-9])\d{8}$"

        if not telephone:
            raise CustomException(msg=f"手机号码（{telephone}）不能为空", code=400)
        elif not re.match(regex_telephone, telephone):
            raise CustomException(msg=f"手机号码（{telephone}）格式不正确", code=400)
        return telephone

    def create_client(
        self,
    ) -> Dysmsapi20170525Client:
        """
        使用AK&SK初始化账号Client
        :return: Client
        :throws Exception
        """
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret,
        )
        # 访问的域名
        config.endpoint = "dysmsapi.aliyuncs.com"
        return Dysmsapi20170525Client(config)
