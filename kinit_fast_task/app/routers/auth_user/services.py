# @Version        : 1.0
# @Create Time    : 2024/5/29 下午3:43
# @File           : services.py
# @IDE            : PyCharm
# @Desc           : 文件描述信息
import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from kinit_fast_task.app.models.auth_user_model import AuthUserModel
from kinit_fast_task.db.database_factory import DatabaseFactory
from kinit_fast_task.app.cruds.auth_user_crud import AuthUserCRUD
from kinit_fast_task.app.schemas import auth_user_schema


class UserService:
    """
    业务逻辑处理，应该为单独的 service 文件，只有通用的处理 才会放在 crud 中
    """

    def __init__(self, session: AsyncSession = None):
        self.session = session

    async def get_recent_users_count(self):
        """
        获取最近一个月的用户新增情况

        :return:
        """
        one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)

        # 查询近一个月用户新增数据量
        stmt = (
            select(func.date(AuthUserModel.create_datetime).label('date'), func.count(AuthUserModel.id).label('count'))
            .where(AuthUserModel.create_datetime >= one_month_ago)
            .group_by(func.date(AuthUserModel.create_datetime))
        )
        result = await self.session.execute(stmt)
        records = result.all()

        # 生成一个完整的日期范围
        start_date = one_month_ago.date()
        end_date = datetime.datetime.utcnow().date()
        date_range = [start_date + datetime.timedelta(days=x) for x in range((end_date - start_date).days + 1)]

        # 创建一个包含所有日期的字典，并将计数初始化为0
        user_count_by_date = {str(date): 0 for date in date_range}

        # 更新字典中的计数值
        for record in records:
            user_count_by_date[str(record.date)] = record.count

        return user_count_by_date

    async def orm_db_getter_01_test(self):
        """
        orm db 手动事务示例

        :return:
        """
        orm_db: AsyncSession = DatabaseFactory.get_db_instance("orm").db_getter()

        # 手动开启一个事务，事务在关闭时会自动 commit ，请勿在事务中使用 commit
        # 不关联的两种操作，请开启两个事务进行处理，比如第二个失败，不影响第一个 commit
        async with orm_db.begin():

            # 创建一个用户
            new_user = auth_user_schema.AuthUserCreateSchema(
                name="orm_db_test",
                telephone="19920240505",
                is_active=True,
                age=3,
                role_ids=[1]
            )
            user = await AuthUserCRUD(orm_db).create_data(new_user, v_return_obj=True)
            print("用户创建成功", user)

            # 更新一个用户
            user = await AuthUserCRUD(orm_db).update_data(user.id, {"is_active": False}, v_return_obj=True)
            print("用户更新成功", user.is_active)

            # 会触发回滚操作, 或者可以说, 该事务还未结束, 并没有触发 commit 操作, 所以以上操作都会回滚
            # raise ValueError("事务内抛出异常, 测试回滚操作")

        # 事务外触发异常, 因为以上事务已经 commit , 所以这里不会回滚, 以上事务内操作都会进入到数据库
        # raise ValueError("抛出异常，测试回滚操作")

    async def orm_db_getter_02_test(self):
        """
        orm db 示例

        :return:
        """
        orm_db: AsyncSession = DatabaseFactory.get_db_instance("orm").db_getter()

        # 查询不需要事务

        # 获取 id=1 的用户，没有获取到会返回 None
        user = await orm_db.get(AuthUserModel, 2)
        if user is None:
            print("未获取到指定用户")
        else:
            print("获取用户成功", user)
