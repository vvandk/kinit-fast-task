# @Version        : 1.0
# @Create Time    : 2023/3/27 9:48
# @File           : send_email.py
# @IDE            : PyCharm
# @Desc           : 发送邮件封装类


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from kinit_fast_task.core import CustomException


class EmailSender:
    def __init__(self, email: str, password: str, smtp_server: str, smtp_port: int) -> None:
        """
        初始化配置
        :param email:
        :param password:
        :param smtp_server:
        :param smtp_port:
        """
        self.email = email
        self.password = password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.server = self.__get_settings()

    def __get_settings(self) -> smtplib.SMTP:
        """
        获取配置信息
        :return:
        """
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        try:
            server.login(self.email, self.password)
            return server
        except smtplib.SMTPAuthenticationError as exc:
            raise CustomException("邮件发送失败，邮箱服务器认证失败！") from exc
        except AttributeError as exc:
            raise CustomException("邮件发送失败，邮箱服务器认证失败！") from exc

    def send_email(self, to_emails: list[str], subject: str, body: str, attachments: list[str] = None) -> bool:
        """
        发送邮件
        :param to_emails: 收件人，一个或多个
        :param subject: 主题
        :param body: 内容
        :param attachments: 附件
        """
        message = MIMEMultipart()
        message["From"] = self.email
        message["To"] = ", ".join(to_emails)
        message["Subject"] = subject
        body = MIMEText(body)
        message.attach(body)
        if attachments:
            for attachment in attachments:
                with open(attachment, "rb") as f:
                    file_data = f.read()
                filename = attachment.split("/")[-1]
                attachment = MIMEApplication(file_data, Name=filename)
                attachment["Content-Disposition"] = f'attachment; filename="{filename}"'
                message.attach(attachment)
        try:
            result = self.server.sendmail(self.email, to_emails, message.as_string())
            self.server.quit()
            print("邮件发送结果", result)
            return not result
        except smtplib.SMTPException as e:
            self.server.quit()
            print("邮件发送失败！错误信息：", e)
            return False
