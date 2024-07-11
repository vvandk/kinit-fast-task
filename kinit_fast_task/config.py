# @Version        : 1.0
# @Create Time    : 2024/3/23 22:30
# @File           : config.py
# @IDE            : PyCharm
# @Desc           : 项目全局配置信息
from pathlib import Path

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from pydantic import PostgresDsn, RedisDsn, MongoDsn
from ipaddress import IPv4Address

# 项目根目录
_BASE_PATH: Path = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """
    官方文档：https://docs.pydantic.dev/latest/concepts/pydantic_settings/#installation

    字段值优先级
    在多种方式指定同一个设置字段的值的情况下，选定值的确定顺序如下（按优先级降序排列）：

    1. init_settings：传递给 BaseSettings 类构造函数的参数
    2. dotenv_settings：从 dotenv（.env）文件加载的变量。
    3. env_settings：环境变量，例如上述的 my_prefix_special_function。
    4. settings_cls：BaseSettings 模型的默认字段值。
    """

    # 单体开发
    model_config = SettingsConfigDict(
        env_file=str(_BASE_PATH.parent / ".env"), env_file_encoding="utf-8", extra="ignore"
    )

    # 模块开发
    # model_config = SettingsConfigDict(env_file='.env', env_file_encoding="utf-8", extra="ignore")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return init_settings, dotenv_settings, env_settings


class DemoSettings(Settings):
    """
    项目演示环境配置
    """

    # 是否开启演示功能：取消所有POST,DELETE,PUT操作权限
    DEMO_ENV: bool = False

    # 演示功能白名单, 值为完整 API, 例子：/auth/user/create
    DEMO_WHITE_LIST_PATH: list[str] = []
    # 演示功能黑名单，黑名单优先级更高, 值为完整 API, 例子：/auth/user/create
    DEMO_BLACK_LIST_PATH: list[str] = []


class AuthSettings(Settings):
    """
    项目认证配置
    """

    """
    配置 OAuth2 密码流认证方式
    官方文档：https://fastapi.tiangolo.com/zh/tutorial/security/first-steps/#fastapi-oauth2passwordbearer
    auto_error:(bool) 可选参数, 默认为 True
    当验证失败时，如果设置为 True，FastAPI 将自动返回一个 401 未授权的响应，如果设置为 False，你需要自己处理身份验证失败的情况。
    """  # noqa: E501
    # OAUTH2_SCHEMA: OAuth2PasswordBearer | Callable[[], str] = (OAuth2PasswordBearer(tokenUrl="", auto_error=False))
    # 安全的随机密钥，该密钥将用于对 JWT 令牌进行签名
    SECRET_KEY: str = "vgb0tnl9d58+6n-6h-ea&u^1#s0ccp!794=kbvqacjq75vzps$"
    # 用于设定 JWT 令牌签名算法
    ALGORITHM: str = "HS256"
    # access_token 过期时间，一天
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 9999


class StorageSettings(Settings):
    """
    文件存储配置
    """

    """
    阿里云对象存储OSS配置
    OSS_ENABLE: 是否启用 OSS 文件存储功能
    OSS_ACCESS_KEY_ID: 通过阿里云控制台创建的AccessKey
    OSS_ACCESS_KEY_SECRET: 通过阿里云控制台创建的AccessSecret
    OSS_ENDPOINT: 填写Bucket所在地域对应的Endpoint, 以华东1（杭州）为例，Endpoint填写为https://oss-cn-hangzhou.aliyuncs.com
    OSS_BUCKET: 通过控制台或PutBucket创建的bucket
    OSS_BASE_URL: 填写OSS_ENDPOINT对应访问的URL
    """  # noqa: E501
    OSS_ENABLE: bool = True  # 是否开启 OSS 文件存储功能
    OSS_ACCESS_KEY_ID: str = "accessKeyId"
    OSS_ACCESS_KEY_SECRET: str = "accessKeySecret"
    OSS_ENDPOINT: str = "endpoint"
    OSS_BUCKET: str = "bucket"
    OSS_BASE_URL: str = "baseUrl"

    """
    挂载静态目录，并添加路由访问，此路由不会在接口文档中显示
    LOCAL_ENABLE：是否启用静态目录访问
    LOCAL_BASE_URL：路由访问
    LOCAL_PATH：静态文件目录绝对路径
    官方文档：https://fastapi.tiangolo.com/tutorial/static-files/
    """
    LOCAL_ENABLE: bool = True
    LOCAL_BASE_URL: str = "/media"
    LOCAL_PATH: str = str(_BASE_PATH / "static")

    """
    挂载系统临时文件目录, 只用于存储临时文件, 不允许外部访问
    TEMP_DIR：临时文件目录绝对路径
    """
    TEMP_ENABLE: bool = True
    TEMP_PATH: str = str(_BASE_PATH / "temp")


class DBSettings(Settings):
    """
    项目关联数据库配置
    """

    # postgresql 数据库配置项
    # 数据库链接配置说明：postgresql+asyncpg://数据库用户名:数据库密码@数据库地址:数据库端口/数据库名称
    ORM_DB_ENABLE: bool
    ORM_DATABASE_URL: PostgresDsn
    # 是否输出执行 SQL
    ORM_DB_ECHO: bool = False

    # Redis 数据库配置
    # 格式："redis://:密码@地址:端口/数据库名称"
    REDIS_DB_ENABLE: bool = False
    REDIS_DB_URL: RedisDsn = "redis://:admin@127.0.0.1:6379/0"

    # MongoDB 数据库配置
    # 格式：mongodb://用户名:密码@地址:端口/?authSource=数据库名称
    MONGO_DB_ENABLE: bool = False
    MONGO_DB_URL: MongoDsn = "mongodb://admin:admin@127.0.0.1:27017/?authSource=test"


class SystemSettings(Settings):
    """
    系统默认配置

    主要为系统默认配置，一般情况下不涉及改变
    """

    # 项目监听主机IP，默认开放给本网络所有主机
    SERVER_HOST: IPv4Address
    # 项目监听端口
    SERVER_PORT: int

    PROJECT_NAME: str = "kinit_fast_task"

    # 是否将日志打印在控制台
    LOG_CONSOLE_OUT: bool = True
    # 日志目录地址
    LOG_PATH: str = str(_BASE_PATH / "logs")
    # 请求日志文件地址
    REQUEST_LOG_FILE_PATH: str = str(_BASE_PATH / "logs" / "requests.log")

    """
    跨域解决
    详细解释：https://cloud.tencent.com/developer/article/1886114
    官方文档：https://fastapi.tiangolo.com/tutorial/cors/
    """
    # 是否启用跨域
    CORS_ORIGIN_ENABLE: bool = True
    # 只允许访问的域名列表，* 代表所有
    ALLOW_ORIGINS: list[str] = ["*"]
    # 是否支持携带 cookie
    ALLOW_CREDENTIALS: bool = True
    # 设置允许跨域的http方法，比如 get、post、put等。
    ALLOW_METHODS: list[str] = ["*"]
    # 允许携带的headers，可以用来鉴别来源等作用。
    ALLOW_HEADERS: list[str] = ["*"]

    # 全局事件配置
    EVENTS: list[str | None] = [f"{PROJECT_NAME}.core.event.close_db_event"]

    # 是否开启保存每次请求日志到本地
    REQUEST_LOG_RECORD: bool = True
    # 是否开启每次操作日志记录到MongoDB数据库
    OPERATION_LOG_RECORD: bool = True
    # 只记录包括的请求方式操作到MongoDB数据库
    OPERATION_RECORD_METHOD: list[str] = ["POST"]
    # 忽略的操作接口函数名称, 列表中的函数名称不会被记录到操作日志中
    IGNORE_OPERATION_ROUTER: list[str] = []

    # 中间件配置
    MIDDLEWARES: list[str | None] = [
        # 请求日志记录中间件
        f"{PROJECT_NAME}.core.middleware.register_request_log_middleware" if REQUEST_LOG_RECORD else None,
        # 操作日志记录中间件 - 保存入 MongoDB 数据库
        f"{PROJECT_NAME}.core.middleware.register_operation_record_middleware" if OPERATION_LOG_RECORD else None,
        # 演示环境中间件
        f"{PROJECT_NAME}.core.middleware.register_demo_env_middleware" if DemoSettings().DEMO_ENV else None,
    ]


class RouterSettings(Settings):
    """
    路由配置，这里单独拿出来的原因是，可能因为 APPS 会有很多，为了不影响其他配置观看，所以单独拿出来

    APPS 少的情况下推荐在 .env 文件中配置 很多的情况下经测试在 .env 文件中无法换行，所以可以配置在这里，但是配置文件谨慎改动
    """  # noqa E501

    # 应用路由文件目录
    APPS_PATH: str = str(_BASE_PATH / "app" / "routers")
    # 需要启用的 app router，该顺序也是文档展示顺序
    APPS: list[str]


class TaskSettings(Settings):
    """
    项目定时任务配置
    """

    # 是否开启任务引擎
    TASK_ENABLE: bool
    # 运行中任务集合
    SCHEDULER_TASK_JOBS: str = "scheduler_task_jobs"
    # 任务脚本目录
    TASK_PAG: str = f"{SystemSettings().PROJECT_NAME}.app.tasks"


class GlobalSettings(BaseSettings):
    """
    全局统一配置入口
    """

    BASE_PATH: Path = _BASE_PATH
    # 项目定时任务配置
    task: TaskSettings = TaskSettings()
    # 项目演示环境配置
    demo: DemoSettings = DemoSettings()
    # 项目认证配置
    auth: AuthSettings = AuthSettings()
    # 项目关联数据库配置
    db: DBSettings = DBSettings()
    # 文件存储配置
    storage: StorageSettings = StorageSettings()
    # 系统基础配置
    system: SystemSettings = SystemSettings()
    # 系统路由
    router: RouterSettings = RouterSettings()


settings = GlobalSettings()
