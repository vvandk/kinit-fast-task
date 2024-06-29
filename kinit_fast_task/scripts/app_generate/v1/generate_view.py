# ruff: noqa: E501
from pathlib import Path

from kinit_fast_task.config import settings
from kinit_fast_task.core import log
from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase
from kinit_fast_task.scripts.app_generate.v1.json_config_schema import JSONConfigSchema


class ViewGenerate(GenerateBase):

    def __init__(self, json_config: JSONConfigSchema):
        """
        初始化工作

        :param json_config:
        """
        self.json_config = json_config
        self.file_path = Path(settings.router.APPS_PATH) / self.json_config.views.filename
        self.project_name = settings.system.PROJECT_NAME

    def write_generate_code(self):
        """
        生成 view 文件，以及代码内容
        """
        if self.file_path.exists():
            log.info("Views 文件已存在，正在删除重新写入")
            self.file_path.unlink()
        else:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.touch()
        self.file_path.touch()
        code = self.generate_code()
        self.file_path.write_text(code, encoding="utf-8")
        log.info("Views 代码创建完成")

    def generate_code(self) -> str:
        """
        生成代码
        """
        code = self.generate_file_desc(self.file_path.name, "1.0", "路由，视图文件")
        code += self.generate_modules_code(self.get_base_module_config())
        router = self.json_config.app_name.replace("_", "/")
        code += f'\n\nrouter = APIRouter(prefix="/{router}", tags=["{self.json_config.app_desc}管理"])\n'
        code += self.get_base_code_content()

        return code.replace("\t", "    ")

    def get_base_module_config(self):
        """
        获取基础模块导入配置
        """
        modules = {
            "sqlalchemy.ext.asyncio": ["AsyncSession"],
            "fastapi": ["APIRouter", "Depends", "Body", "Query"],
            f"{self.project_name}.utils.response": [
                "RestfulResponse",
                "ResponseSchema",
                "PageResponseSchema",
            ],
            f"{self.project_name}.db.orm.asyncio": ["orm_db"],
            f"{self.project_name}.app.cruds.{self.json_config.crud.filename}": [self.json_config.crud.class_name],
            f"{self.project_name}.app.schemas.": [
                {self.json_config.schemas.filename},
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
        zh_name = self.json_config.app_desc
        create_schema = f"{self.json_config.schemas.filename}.{self.json_config.schemas.create_class_name}"
        update_schema = f"{self.json_config.schemas.filename}.{self.json_config.schemas.update_class_name}"
        simple_out_schema = f"{self.json_config.schemas.filename}.{self.json_config.schemas.simple_out_class_name}"
        session = 'session: AsyncSession = Depends(DBFactory.get_db_instance("orm").db_transaction_getter)'
        crud = self.json_config.crud.class_name

        base_code = f'\n\n@router.post("/create", response_model=ResponseSchema[str], summary="创建{zh_name}")'
        base_code += f'\nasync def create(data: {create_schema}, {session}):'
        base_code += f'\n\treturn RestfulResponse.success(await {crud}(session).create_data(data=data))\n'

        base_code += f'\n\n@router.put("/update", response_model=ResponseSchema[str], summary="更新{zh_name}")'
        base_code += f'\nasync def update(data_id: int = Body(..., description="{zh_name}编号"), data: {update_schema}, {session}):'
        base_code += f'\n\treturn RestfulResponse.success(await {crud}(session).put_data(data_id, data))\n'

        base_code += f'\n\n@router.delete("/delete", response_model=ResponseSchema[str], summary="批量删除{zh_name}")'
        base_code += f'\nasync def delete(data_ids: list[int] = Body(..., description="{zh_name}编号列表"), {session}):'
        base_code += f'\n\tawait {crud}(session).delete_datas(ids=data_ids)'
        base_code += '\n\treturn RestfulResponse.success("删除成功")\n'

        base_code += f'\n\n@router.get("/list/query", response_model=PageResponseSchema[list[{simple_out_schema}]], summary="获取{zh_name}列表")'
        base_code += f'\nasync def list_query(params: PageParams = Depends(), {session}):'
        base_code += f'\n\tdatas = await {crud}(session).get_datas(**params.dict(), v_return_type="dict")'
        base_code += f'\n\ttotal = await {crud}(session).get_count(**params.to_count())'
        base_code += '\n\treturn RestfulResponse.success(data=datas, total=total, page=params.page, limit=params.limit)\n'

        base_code += f'\n\n@router.get("/one/query", summary=\"获取{zh_name}信息\")'
        base_code += f'\nasync def one_query(data_id: int = Query(..., description="{zh_name}编号"), {session}):'
        base_code += f'\n\tdata = await {crud}(session).get_data(data_id, v_schema={simple_out_schema}, v_return_type="dict")'
        base_code += '\n\treturn RestfulResponse.success(data=data)\n'
        base_code += '\n'
        # fmt: on
        return base_code.replace("\t", "    ")
