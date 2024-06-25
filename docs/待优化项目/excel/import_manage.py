# @Version        : 1.0
# @Create Time    : 2021/12/5 8:45
# @File           : import_manage.py
# @IDE            : PyCharm
# @Desc           : 数据导入管理

from fastapi import UploadFile
from kinit_fast_task.core import CustomException
from .excel_manage import ExcelManage
from kinit_fast_task.file.file_manage import FileManage
from .write_xlsx import WriteXlsx
from kinit_fast_task.utils.tools import list_dict_find
from enum import Enum


class FieldType(Enum):
    list = "list"
    str = "str"


class ImportManage(ExcelManage):
    """
    数据导入管理

    只支持 XLSX 类型文件：application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

    1. 判断文件类型
    2. 保存文件为临时文件
    3. 获取文件中的数据
    4. 逐行检查数据，通过则创建数据
    5. 不通过则添加到错误列表
    6. 统计数量并返回
    """

    file_type = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

    def __init__(self, file: UploadFile, headers: list[dict]):
        super().__init__()
        self.__table_data = None
        self.__table_header = None
        self.errors = []
        self.success = []
        self.success_number = 0
        self.error_number = 0
        self.check_file_type(file)
        self.file = file
        self.headers = headers

    @classmethod
    def check_file_type(cls, file: UploadFile) -> None:
        """
        验证文件类型
        :param file: 上传文件
        :return:
        """
        if file.content_type not in cls.file_type:
            raise CustomException(message="文件类型必须为xlsx类型")

    async def get_table_data(
        self, file_path: str = None, sheet_name: str = None, header_row: int = 1, data_row: int = 2
    ) -> None:
        """
        获取表格数据与表头
        :param file_path:
        :param sheet_name:
        :param header_row: 表头在第几行
        :param data_row: 数据开始行
        :return:
        """
        if file_path:
            __filename = file_path
        else:
            __filename = await FileManage.async_save_temp_file(self.file)
        self.open_sheet(sheet_name=sheet_name, file=__filename, read_only=True)
        self.__table_header = self.get_header(header_row, len(self.headers), asterisk=True)
        self.__table_data = self.readlines(min_row=data_row, max_col=len(self.headers))
        self.close()

    def check_table_data(self) -> None:
        """
        检查表格数据
        :return:
        """
        for row in self.__table_data:
            result = self.__check_row(row)
            if not result[0]:
                row.append(result[1])
                self.errors.append(row)
                self.error_number += 1
            else:
                self.success_number += 1
                self.success.append(result[1])

    def __check_row(self, row: list) -> tuple:
        """
        检查行数据

        检查条件：
        1. 检查是否为必填项
        2. 检查是否为选项列表
        3. 检查是否符合规则
        :param row: 数据行
        :return:
        """
        data = {}
        for index, cell in enumerate(row):
            value = cell
            field = self.headers[index]
            label = self.__table_header[index]
            if not cell and field.get("required", False):
                return False, f"{label}不能为空！"
            elif field.get("options", []) and cell:
                item = list_dict_find(field.get("options", []), "label", cell)
                if item:
                    value = item.get("value")
                else:
                    return False, f"请选择正确的{label}"
            elif field.get("rules", []) and cell:
                rules = field.get("rules")
                for validator in rules:
                    try:
                        validator(str(cell))
                    except ValueError as e:
                        return False, f"{label}：{e.__str__()}"
            if value:
                field_type = field.get("type", FieldType.str)
                if field_type == FieldType.list:
                    data[field.get("field")] = [value]
                elif field_type == FieldType.str:
                    data[field.get("field")] = str(value)
            else:
                data[field.get("field")] = value
        data["old_data_list"] = row
        return True, data

    def generate_error_url(self) -> str:
        """
        成功错误数据的文件链接
        :return:
        """
        if self.error_number <= 0:
            return ""
        em = WriteXlsx()
        em.create_excel(sheet_name="用户导入失败数据", save_static=True)
        em.generate_template(self.headers, max_row=self.error_number)
        em.write_list(self.errors)
        em.close()
        return em.get_file_url()

    def add_error_data(self, row: dict) -> None:
        """
        增加错误数据
        :param row: 错误的数据行
        :return:
        """
        self.errors.append(row)
        self.error_number += 1
        self.success_number -= 1
