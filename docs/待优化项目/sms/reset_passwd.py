# @Version        : 1.0
# @Create Time    : 2023/6/14 16:58
# @File           : reset_passwd.py
# @IDE            : PyCharm
# @Desc           : 重置密码

from .aliyun import AliyunSMS


class ResetPasswordSMS(AliyunSMS):
    async def main_async(self, password: str) -> list[bool]:
        """
        主程序入口，异步方式
        :param password: 新密码
        """
        return await super().main_async(password=password)

    def _get_template_param(self, **kwargs) -> str:
        """
        获取模板参数

        可以被子类继承的受保护的私有方法
        """
        password = kwargs.get("password")
        template_param = f'{"password":"{password}"}'
        return template_param
