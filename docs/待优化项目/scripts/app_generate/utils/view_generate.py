# ruff: noqa: E501
from pathlib import Path

from kinit_fast_task.app.models.base.orm import AbstractORMModel
from kinit_fast_task.core.logger import log
from .generate_base import GenerateBase


class ViewGenerate(GenerateBase):
    def __init__(
        self,
        *,
        model: type[AbstractORMModel],
        zh_name: str,
        en_name: str,
        base_class_name: str,
        schema_simple_out_class_name: str,
        crud_class_name: str,
        param_class_name: str,
        view_file_path: Path,
        **kwargs,
    ):
        """
        初始化工作
        :param model: 提前定义好的 ORM 模型
        :param zh_name: 功能中文名称，主要用于描述、注释
        :param base_class_name:
        :param schema_simple_out_class_name:
        :param crud_class_name:
        :param param_class_name:
        :param view_file_path:
        :param en_name: 功能英文名称
        """
        self.model = model
        self.base_class_name = base_class_name
        self.schema_simple_out_class_name = schema_simple_out_class_name
        self.crud_class_name = crud_class_name
        self.param_class_name = param_class_name
        self.zh_name = zh_name
        self.en_name = en_name
        self.view_file_path = view_file_path

    def write_generate_code(self):
        """
        生成 view 文件，以及代码内容
        :return:
        """
        if self.view_file_path.exists():
            log.info("Views 文件已存在，正在删除重新写入")
            self.view_file_path.unlink()
        else:
            self.view_file_path.parent.mkdir(parents=True, exist_ok=True)
            self.view_file_path.touch()
        self.view_file_path.touch()
        code = self.generate_code()
        self.view_file_path.write_text(code, encoding="utf-8")
        log.info("Views 代码创建完成")

    def generate_code(self) -> str:
        """
        生成代码
        :return:
        """
        code = self.generate_file_desc(self.view_file_path.name, "1.0", "路由，视图文件")
        code += self.generate_modules_code(self.get_base_module_config())
        router = self.en_name.replace("_", "/")
        code += f'\n\nrouter = APIRouter(prefix="/{router}", tags=["{self.zh_name}管理"])\n'
        code += self.get_base_code_content()

        return code.replace("\t", "    ")

    def get_base_module_config(self):
        """
        获取基础模块导入配置
        :return:
        """
        modules = {
            "sqlalchemy.ext.asyncio": ["AsyncSession"],
            "fastapi": ["APIRouter", "Depends", "Body", "Query"],
            "kinit_fast_task.utils.response": [
                "RestfulResponse",
                "ResponseSchema",
                "PageResponseSchema",
            ],
            "kinit_fast_task.db.orm.asyncio": ["orm_db"],
            f"kinit_fast_task.app.cruds.{self.en_name}": [self.crud_class_name],
            f"kinit_fast_task.app.schemas.{self.en_name}": [
                f"{self.base_class_name}Create",
                f"{self.base_class_name}Update",
                f"{self.base_class_name}SimpleOut",
            ],
            ".params": ["PageParams"],
            "kinit_fast_task.app.cruds.base.orm": ["ReturnType"],
        }
        return modules

    def get_base_code_content(self):
        """
        获取基础代码内容
        :return:
        """
        # fmt: off
        base_code = f'\n\n@router.post("/create", response_model=ResponseSchema[str], summary="创建{self.zh_name}")'
        base_code += f'\nasync def create(data: {self.base_class_name}Create, db: AsyncSession = Depends(orm_db.db_transaction_getter)):'
        base_code += f'\n\treturn RestfulResponse.success(await {self.crud_class_name}(db).create_data(data=data))\n'

        base_code += f'\n\n@router.put("/update", response_model=ResponseSchema[str], summary="更新{self.zh_name}")'
        base_code += f'\nasync def update(data_id: int = Body(..., description="{self.zh_name}编号"), data: {self.base_class_name}Update = Body(..., description="更新内容"), db: AsyncSession = Depends(orm_db.db_transaction_getter)):'
        base_code += f'\n\treturn RestfulResponse.success(await {self.crud_class_name}(db).put_data(data_id, data))\n'

        base_code += f'\n\n@router.delete("/delete", response_model=ResponseSchema[str], summary="批量删除{self.zh_name}")'
        base_code += f'\nasync def delete(data_ids: list[int] = Body(..., description="{self.zh_name}编号列表"), db: AsyncSession = Depends(orm_db.db_transaction_getter)):'
        base_code += f'\n\tawait {self.crud_class_name}(db).delete_datas(ids=data_ids)'
        base_code += '\n\treturn RestfulResponse.success("删除成功")\n'

        base_code += f'\n\n@router.get("/get/list", response_model=PageResponseSchema[list[{self.schema_simple_out_class_name}]], summary="获取{self.zh_name}列表")'
        base_code += '\nasync def get_list(params: PageParams = Depends(), db: AsyncSession = Depends(orm_db.db_transaction_getter)):'
        base_code += f'\n\tdatas = await {self.crud_class_name}(db).get_datas(**params.dict(), v_return_type=ReturnType.DICT)'
        base_code += f'\n\ttotal = await {self.crud_class_name}(db).get_count(**params.to_count())'
        base_code += '\n\treturn RestfulResponse.success(data=datas, total=total, page=params.page, limit=params.limit)\n'

        base_code += f'\n\n@router.get("/get/one", summary=\"获取{self.zh_name}信息\")'
        base_code += f'\nasync def get_one(data_id: int = Query(..., description="{self.zh_name}编号"), db: AsyncSession = Depends(orm_db.db_transaction_getter)):'
        base_code += f'\n\tdata = await {self.crud_class_name}(db).get_data(data_id, v_schema={self.schema_simple_out_class_name}, v_return_type=ReturnType.DICT)'
        base_code += '\n\treturn RestfulResponse.success(data=data)\n'
        base_code += '\n'
        # fmt: on
        return base_code.replace("\t", "    ")
