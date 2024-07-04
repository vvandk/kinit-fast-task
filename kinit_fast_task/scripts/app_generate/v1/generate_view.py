# ruff: noqa: E501
from pathlib import Path
from kinit_fast_task.config import settings
from kinit_fast_task.scripts.app_generate.utils.generate_base import GenerateBase
from kinit_fast_task.scripts.app_generate.v1.json_config_schema import JSONConfigSchema
from kinit_fast_task.utils.logger import TaskLogger


class ViewGenerate(GenerateBase):
    def __init__(self, json_config: JSONConfigSchema, task_log: TaskLogger):
        """
        初始化工作

        :param json_config:
        """
        self.json_config = json_config
        self.file_path = Path(settings.router.APPS_PATH) / json_config.app_name / self.json_config.views.filename
        self.project_name = settings.system.PROJECT_NAME
        self.task_log = task_log
        self.task_log.info("开始生成 Views 代码, Views 文件地址为：", self.file_path, is_verbose=True)

    def write_generate_code(self, overwrite: bool = False):
        """
        生成 view 文件，以及代码内容
        """
        if self.file_path.exists():
            if overwrite:
                self.task_log.warning("Views 文件已存在, 已选择覆盖, 正在删除重新写入.")
                self.file_path.unlink()
            else:
                self.task_log.warning("Views 文件已存在, 未选择覆盖, 不再进行 Views 代码生成.")
                return False
        else:
            self.create_pag(self.file_path.parent)

        self.file_path.touch()
        code = self.generate_code()
        self.file_path.write_text(code, encoding="utf-8")
        self.task_log.success("Views 代码写入完成")

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
        crud_file_name = Path(self.json_config.crud.filename).stem
        schema_file_name = Path(self.json_config.schemas.filename).stem
        modules = {
            "sqlalchemy.ext.asyncio": ["AsyncSession"],
            "fastapi": ["APIRouter", "Depends", "Body", "Query"],
            f"{self.project_name}.utils.response": [
                "RestfulResponse",
                "ResponseSchema",
                "PageResponseSchema",
            ],
            f"{self.project_name}.db.database_factory": ["DBFactory"],
            f"{self.project_name}.app.cruds.{crud_file_name}": [self.json_config.crud.class_name],
            f"{self.project_name}.app.schemas": [schema_file_name],
            ".params": ["PageParams"],
        }
        return modules

    def get_base_code_content(self):
        """
        获取基础代码内容
        :return:
        """
        # fmt: off
        zh_name = self.json_config.app_desc
        schema_file_name = Path(self.json_config.schemas.filename).stem

        create_schema = f"{schema_file_name}.{self.json_config.schemas.create_class_name}"
        update_schema = f'{schema_file_name}.{self.json_config.schemas.update_class_name} = Body(..., description="更新内容")'
        simple_out_schema = f"{schema_file_name}.{self.json_config.schemas.simple_out_class_name}"

        session = 'session: AsyncSession = Depends(DBFactory.get_db_instance("orm").db_transaction_getter)'
        crud = self.json_config.crud.class_name

        base_code = f'\n\n@router.post("/create", response_model=ResponseSchema[str], summary="创建{zh_name}")'
        base_code += f'\nasync def create(data: {create_schema}, {session}):'
        base_code += f'\n\treturn RestfulResponse.success(await {crud}(session).create_data(data=data))\n'

        base_code += f'\n\n@router.put("/update", response_model=ResponseSchema[str], summary="更新{zh_name}")'
        base_code += f'\nasync def update(data_id: int = Body(..., description="{zh_name}编号"), data: {update_schema}, {session}):'
        base_code += f'\n\treturn RestfulResponse.success(await {crud}(session).update_data(data_id, data))\n'

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
