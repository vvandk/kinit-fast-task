# KINIT-FAST-TASK

## 以下文档在本项目中提供了重要的基础

FastAPI 官方文档：https://fastapi.tiangolo.com/zh/

Pydantic 官方文档：https://pydantic-docs.helpmanual.io/

Typer 官方文档：https://typer.tiangolo.com/

SQLAlchemy 2.0 async 官方文档：https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html

Alembic 官方文档：https://alembic.sqlalchemy.org/en/latest/

Poetry pyproject.toml 官方文档：https://python-poetry.org/docs/main/pyproject/

OpenAPI 规范官方文档：https://swagger.io/specification/

Ruff 官方文档：https://docs.astral.sh/ruff/

SQLAlchemy 2.0 中文官方文档：https://docs.sqlalchemy.org.cn/en/20/orm/quickstart.html



本项目为 KINIT 项目下的 基础定时任务版本，主推定时任务功能的使用：

1. 定时任务功能的实现依赖于 `APScheduler` 开源项目
2. 定时任务持久化依赖于 `MongoDB` 数据库
3. 主要为支持异步定时任务操作，目前数据库均为异步方式操作

定时任务使用禁忌：

1. 切勿在异步方法中使用同步操作，会造成阻塞，比如：`time.sleep`, `requests` 等操作
2. 在使用 `AddTask` 添加任务方式，切勿在任务类中的 `__init__` 中添加非序列化对象，比如 `mongo_db`




## 项目结构

```
kinit-fast-task
├── alembic                           # ORM 数据库迁移
├── kinit_fast_task   # 主应用程序目录
│   ├── app                           # 服务模块
│   │   ├── cruds                     # 全局数据库操作 CRUD
│   │   ├── depends                   # 全局服务依赖项
│   │   ├── models                    # 全局 ORM Model
│   │   ├── routers                   # 路由，接口，服务
│   │   │   └── app_name              # 单个应用服务
│   │   │   │   ├── schemas.py        # 应用独立 schema
│   │   │   │   ├── params.py         # 分页请求参数
│   │   │   │   ├── services.py       # 业务逻辑代码
│   │   │   │   └── views.py          # 应用路由接口文件
│   │   ├── schemas                   # 全局 Pydantic Schema 数据序列化
│   │   ├── system                    # 系统路由，接口，服务
│   │   └── tasks                     # 自定义定时任务
│   ├── core                          # 系统核心组件
│   │   ├── event.py                  # 系统事件
│   │   ├── exception.py              # 系统异常处理
│   │   ├── middleware.py             # 系统中间件
│   │   ├── register.py               # 系统注册项
│   │   └── types.py                  # 全局数据类型
│   ├── db                            # 数据库引擎封装
│   ├── logs                          # 系统日志
│   ├── scripts                       # 系统脚本
│   │   └── app_generate              # 基于 ORM Model 生成 app
│   ├── static                        # 静态文件
│   ├── task                          # 定时任务核心文件
│   ├── utils                         # 工具模块
│   ├── config.py                     # 系统配置项
│   └── main.py                       # 系统主应用
├── tests
├── .env                              # 系统环境变量
├── .gitignore
├── pyproject.toml                    # 系统依赖库，基础信息
├── main.py                           # 主程序入口
├── ruff.toml                         # 格式化代码
└── alembic.ini                       # ORM 迁移配置文件
```

## 开发环境

开发语言：Python 3.10

开发工具：Pycharm



**使用技术栈**

- [Python3](https://gitee.com/link?target=https%3A%2F%2Fwww.python.org%2Fdownloads%2Fwindows%2F)：熟悉 python3 基础语法
- [FastAPI](https://gitee.com/link?target=https%3A%2F%2Ffastapi.tiangolo.com%2Fzh%2F) - 熟悉后台接口 Web 框架
- [SQLAlchemy 2.0](https://gitee.com/link?target=https%3A%2F%2Fdocs.sqlalchemy.org%2Fen%2F20%2Findex.html) - 数据数据库操作
- [APScheduler](https://apscheduler.readthedocs.io/en/3.x/userguide.html)：定时任务框架
- [Pydantic 2](https://docs.pydantic.dev/latest/) - 数据验证库
- [Typer](https://gitee.com/link?target=https%3A%2F%2Ftyper.tiangolo.com%2F) - 熟悉命令行工具的使用
- [MySQL](https://gitee.com/link?target=https%3A%2F%2Fwww.mysql.com%2F) 和 [MongoDB](https://gitee.com/link?target=https%3A%2F%2Fwww.mongodb.com%2F) 和 [Redis](https://gitee.com/link?target=https%3A%2F%2Fredis.io%2F) - 熟悉数据存储数据库

### 数据库依赖情况

**MongoDB**

在该版本中主要依赖于 MongoDB 数据库

并且在部署时，必须为复制集模式，单节点也可以开启，因为只有开启复制集模式，才能使用 MongoDB 事务功能

部署方式可参考：https://gitee.com/ktianc/docker_env

MongoDB 的主要功能为：

1. 存储系统操作记录
2. 定时任务持久化存储
3. 定时任务管理列表
4. 定时任务执行记录

**Redis**

系统中暂未提供 Redis 数据库使用示例

**PostgreSQL**

业务逻辑功能全部会在 PostgreSQL 数据库中存储

目前只提供了 PostgreSQL 使用示例：

1. 用户管理
2. 角色管理

以上数据库均可在 `.env` 文件中选择开启或者关闭，只是关闭后会无法使用对应功能，但不会影响其他未关联功能

## 源码地址

gitee地址(主推)：https://gitee.com/ktianc/kinit-fast-task

github地址：https://github.com/vvandk/kinit-fast-task



**KINIT 完整版**

gitee地址(主推)：https://gitee.com/ktianc/kinit

github地址：[https://github.com/vvandk/kinit](https://gitee.com/link?target=https%3A%2F%2Fgithub.com%2Fvvandk%2Fkinit)

## 微信群

目前群聊已经达到 200 人，只能通过邀请进群，不能再直接扫描群二维码进群，需要进群的可以先加我，备注进群，我就拉你进群。

<img src="https://ktianc.oss-cn-beijing.aliyuncs.com/resource/images/20240703/1719969784NPMyq0Jv.jpg" alt="logo" style="zoom: 33%;" />

## 首次使用

```shell
# 安装依赖库
pip3 install poetry -i https://mirrors.aliyun.com/pypi/simple/
poetry install
```

### 配置

复制项目根目录下的 `.env.example` 到新文件 `.env`

并根据您的需要自定义配置该项目

### 运行启动

```shell
# 直接运行main文件
python main.py run
```

### 接口文档

Swagger UI Docs：

```
http://127.0.0.1:9000/docs
```

Redoc HTML Docs：

```
http://127.0.0.1:9000/redoc
```

## 代码规范

### 代码检查与格式化

```shell
# 代码格式化
ruff format

# 代码规范检查：
ruff check

# 代码格式修复
ruff check --fix
```

### 接口定义

1. 前置接口地址应提前定义在 `APIRouter` 中
2. 接口地址的最后一项应该为本接口的实际操作，通常有：`query`, `create`, `update`, `delete`, `upload`
3. 不再推荐使用路径参数，应该使用查询参数代替

### 命名规范

`cruds`, `models`, `schemas` 的命名方式为：开头为模块名称，中间为 `app` 名称，最后为各功能名称

`routers` 命名方式为：开头为模块名称，中间为 `app` 名称

比如用户管理：模块名称为 `auth`, `app` 名称为 `user`

- cruds：auth_user_crud
- models：auth_user_model
- schemas：auth_user_schema
- routers：auth_user

## 与 KINIT 有什么不同

1. 新增了包管理工具： `poetry`
2. 新增了代码检查格式化工具：`ruff`
3. 新增了项目配置管理工具：`pydantic-settings`
4. 内置了定时任务框架：`APScheduler`
5. 项目结构重新调整
6. 整体类型提示优化
7. 重新封装数据库管理模块
8. `orm` 与 `MongoDB` 操作优化，`MongoDB` 操作支持事务处理
9. 对生成接口文档更加友好
10. 日志模块优化
11. 响应数据模块优化
12. 新增 `schema` 基类，在基类中实现 `hidden=True` 的字段不会在接口文档中出现
13. 将默认使用的 `Mysql` 改为了 `PostgreSQL`

## 其他

### 开发工具

Pycharm 2022.3.2

代码样式配置：

![image-20230315194534959](https://ktianc.oss-cn-beijing.aliyuncs.com/kinit/public/images/image-20230315194534959.png)

文件代码模板：

```python
# @Version        : 1.0
# @Update Time    : ${DATE}
# @File           : ${NAME}.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息
```

![image-20240518230529195](images/image-20240518230154682.png)
