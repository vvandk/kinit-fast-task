# 单节点 MongoDB 数据库开启副本集

使用Motor操作MongoDB事务时需要MongoDB启用副本集

MongoDB的事务功能（尤其是多文档事务）依赖于副本集来保证数据的一致性和原子性

因此，即使是单节点MongoDB实例，要使用事务也需要配置为副本集

## 使用 Docker 部署

工作目录：/opt/mongo

数据目录：/opt/mongo/db

```
mkdir -p /opt/mongo/db

chmod -R 755 /opt/mongo/db
```

### 步骤1：新建配置文件

```shell
vim /opt/mongo/mongod.conf
```

配置文件内容：

```yaml
# 存储相关设置
storage:
  dbPath: /data/db            # 数据存储路径

# 网络相关设置
net:
  bindIp: 0.0.0.0             # 绑定 IP 地址，0.0.0.0 表示所有 IP
  port: 27017                 # MongoDB 监听端口

# 副本集相关设置
replication:
  replSetName: rs0            # 副本集名称

# 安全相关设置
security:
  authorization: enabled      # 启用授权，设置用户访问控制
  keyFile: /data/conf/keyfileone  # 密钥文件路径
```

### 步骤2：创建密钥文件

```shell
# 使用 OpenSSL 或其他工具生成一个 base64 编码的随机字符串作为密钥
openssl rand -base64 756 > keyfileone

# 确保密钥文件的权限设置为 400，这意味着只有文件所有者可以读取它
chmod 400 keyfileone

# 确保文件所有者是 MongoDB 用户（通常是 UID 999）
# 在 Docker 容器中，MongoDB 通常以 UID 999 运行
# 如果不确定，也可以先启动一个没有配置的容器查看一下：
# docker run --rm -it mongo:latest --name mongo
# docker exec -it mongo id mongodb
chown 999:999 /opt/mongo/keyfileone
```

### 步骤3：启动容器

```
# 用于测试 --rm 停止后会自动删除容器
docker run --rm -it \
--name kinit-mongo \
-v /opt/mongo:/data/conf \
-v /opt/mongo/db:/data/db \
-p 27017:27017 \
-e MONGO_INITDB_ROOT_USERNAME=admin \
-e MONGO_INITDB_ROOT_PASSWORD=123456 \
mongo:latest \
mongod --config /data/conf/mongod.conf
```

### 步骤4：初始化副本集

```shell
# 进入容器 mongosh 命令行
docker exec -it kinit-mongo mongosh -u admin -p 123456

# 初始化副本集 - 使用默认配置
rs.initiate()

# 返回：
# test> rs.initiate()
# {
#   info2: 'no configuration specified. Using a default configuration for the set',
#   me: '92cb97763019:27017',
#   ok: 1
# }
```

现在，你的单节点MongoDB实例已经配置为副本集并支持事务操作了。

## 使用事务的示例代码

在配置好副本集之后，你可以使用事务操作，例如：

```python
import motor.motor_asyncio
import asyncio
from pymongo.errors import PyMongoError

# 连接MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017')
db = client['your_database']

async def insert_with_transaction():
    async with await client.start_session() as session:
        async with session.start_transaction():
            try:
                collection = db['your_collection']
                
                # 插入文档
                await collection.insert_one({"name": "John", "age": 30}, session=session)
                print("Inserted document.")
                
                # 插入另一个文档（可选）
                await collection.insert_one({"name": "Jane", "age": 25}, session=session)
                print("Inserted another document.")
                
                # 提交事务
                await session.commit_transaction()
                print("Transaction committed.")
            except PyMongoError as e:
                print(f"Transaction aborted due to an error: {e}")
                await session.abort_transaction()

# 运行异步函数
asyncio.run(insert_with_transaction())
```

