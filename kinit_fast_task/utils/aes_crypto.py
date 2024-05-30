# @Version        : 1.0
# @Create Time    : 2022/11/3 17:23
# @File           : count.py
# @IDE            : PyCharm
# @Desc           : AES 加解密工具
import base64
from Crypto.Cipher import AES  # 需要先通过poetry add pycryptodome安装此库


class AESEncryption:
    """
    AES加解密工具类，采用CBC模式，并结合Base64进行编码和解码
    """

    def __init__(self, key: str = "0CoJUm6Qywm6ts68", iv: str = "0102030405060708"):
        """
        初始化AES加解密器，设置密钥和初始化向量（IV）
        :param key: 密钥，此处为默认密钥，用户可根据实际情况自定义
        :param iv: 初始化向量（IV），此处为默认值，CBC模式下需固定且长度为16字节
        """
        self.key = key.encode("utf8")  # 将密钥转换为字节类型
        self.iv = iv.encode("utf8")  # 将初始向量转换为字节类型

    @staticmethod
    def pad(s: str):
        """
        字符串填充函数，使得字符串长度能被16整除
        :param s: 需要填充的字符串
        :return: 填充后的字符串
        """
        return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

    @staticmethod
    def un_pad(s: bytes):
        """
        移除字符串填充，恢复原始数据
        :param s: 经过填充的字节数据
        :return: 去除填充后的原始字符串对应的字节数据
        """
        return s[0 : -s[-1]]

    def encrypt(self, plaintext: str):
        """
        对给定明文字符串进行AES加密，并返回Base64编码后的密文字符串
        :param plaintext: 待加密的明文字符串
        :return: Base64编码后的密文字符串
        """
        padded_data = self.pad(plaintext)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        encrypted_bytes = cipher.encrypt(padded_data.encode("utf8"))
        encoded_str = base64.urlsafe_b64encode(encrypted_bytes).decode("utf8")
        return encoded_str

    def decrypt(self, ciphertext: str):
        """
        对Base64解码后的密文进行AES解密，并返回原始明文字符串
        :param ciphertext: Base64编码的密文字符串
        :return: 解密后的原始明文字符串
        """
        decoded_bytes = base64.urlsafe_b64decode(ciphertext.encode("utf8"))
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        decrypted_bytes = cipher.decrypt(decoded_bytes)
        return self.un_pad(decrypted_bytes).decode("utf8")


# 示例使用
if __name__ == "__main__":
    _plaintext = "16658273438153332588-95YEUPJR"  # 需要加密的内容

    aes_helper = AESEncryption()
    encrypted_text = aes_helper.encrypt(_plaintext)
    print(f"加密后的文本: {encrypted_text}")

    decrypted_text = aes_helper.decrypt(encrypted_text)
    print(f"解密后的文本: {decrypted_text}")
