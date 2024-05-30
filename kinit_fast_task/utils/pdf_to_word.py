# @Version        : 1.0
# @Create Time    : 2024/4/22 15:27
# @File           : pdf_to_word.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息


from pdf2docx import Converter


def pdf_to_word(pdf_file_path, word_file_path):
    """
    将PDF文件转换为Word文件。
    :param pdf_file_path: PDF文件的路径
    :param word_file_path: 生成的Word文件的路径
    """
    # 创建一个转换器对象，传入PDF文件路径
    cv = Converter(pdf_file_path)

    # 开始转换过程，这里转换全部页面
    cv.convert(word_file_path, start=0, end=None)

    # 转换结束后清理并关闭文件
    cv.close()


if __name__ == "__main__":
    # 示例使用：将'example.pdf'文件转换为'output.docx'
    pdf_to_word("1.pdf", "1.docx")
