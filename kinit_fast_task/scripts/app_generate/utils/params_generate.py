# ruff: noqa: E501
from pathlib import Path

from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.core.logger import log
from .generate_base import GenerateBase


class ParamsGenerate(GenerateBase):
    def __init__(
        self,
        *,
        model: type[AbstractORMModel],
        zh_name: str,
        en_name: str,
        param_file_path: Path,
        param_class_name: str,
        **kwargs,
    ):
        """
        初始化工作
        :param model: 提前定义好的 ORM 模型
        :param zh_name: 功能中文名称，主要用于描述、注释
        :param param_class_name:
        :param param_file_path:
        :param en_name: 功能英文名称
        """
        self.model = model
        self.param_class_name = param_class_name
        self.zh_name = zh_name
        self.en_name = en_name
        self.param_file_path = param_file_path

    def write_generate_code(self):
        """
        生成 params 文件，以及代码内容
        :return:
        """
        if self.param_file_path.exists():
            log.info("Params 文件已存在，正在删除重新写入")
            self.param_file_path.unlink()

        self.param_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.param_file_path.touch()

        code = self.generate_code()
        self.param_file_path.write_text(code, "utf-8")
        log.info("Params 代码创建完成")

    def generate_code(self) -> str:
        """
        生成 schema 代码内容
        :return:
        """
        code = self.generate_file_desc(self.param_file_path.name, "1.0", self.zh_name)

        modules = {
            "fastapi": ["Depends", "Query"],
            "kinit_fast_task.app.depends.Paging": ["Paging", "QueryParams"],
        }
        code += self.generate_modules_code(modules)

        base_code = f"\n\nclass {self.param_class_name}(QueryParams):"
        base_code += "\n\tdef __init__(self, params: Paging = Depends()):"
        base_code += "\n\t\tsuper().__init__(params)"
        base_code += "\n"
        code += base_code
        return code.replace("\t", "    ")
