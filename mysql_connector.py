from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, DisconnectionError
from sqlalchemy import exc
from datetime import datetime
from .config import *
from hoshino import log

logger = log.new_logger('BF2042-MySQL')


# 创建数据库连接引擎，配置连接池参数
engine = create_engine(
    f'mysql+pymysql://{USERNAME}:{PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?charset=utf8mb4',
    pool_size=500, max_overflow=500, pool_pre_ping=True)

# 创建会话工厂
Session = sessionmaker(bind=engine)
# 声明模型类
Base = declarative_base()


class UserBind(Base):
    __tablename__ = 'user_bind'
    id = Column(Integer, primary_key=True)
    player = Column(String(50))
    platform = Column(String(50))
    qq_id = Column(String(50))
    nucleusId = Column(String(50))
    personaId = Column(String(50))
    support = Column(Integer)


class WhiteList(Base):
    __tablename__ = 'white_list'
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer)
    approve = Column(Integer)


# 创建会话对象并执行查询操作
session = Session()


# 分页查询
async def query_page(page_number=1, page_size=10):
    # 执行查询操作
    query = session.query(UserBind)
    total_count = query.count()
    user_binds = query.offset((page_number - 1) * page_size).limit(page_size)
    mes = "=====名单=====\n"
    for user in user_binds:
        mes += "玩家名称：" + user.player + "\n" + "QQ：" + user.qq_id + "\n" + "平台：" + user.platform + "\n\n"
    # 添加总记录数信息
    mes += f"\n当前页为{page_number}，总记录数为{total_count}"
    print(mes)
    # 关闭会话
    session.close()
    return mes


# 执行修改绑定
async def update_user_player_by_qq_id(uid, player, nucleusId, personaId):
    try:
        # 查询要更新的用户绑定记录
        user_bind = session.query(UserBind).filter_by(qq_id=uid).first()
        # 获取连接对象
        connection = session.connection()
        if user_bind:
            # 获取原始记录的id
            original_id = user_bind.id
            # 修改模型对象的属性值
            user_bind.player = player
            user_bind.nucleusId = nucleusId
            user_bind.personaId = personaId
            # 提交事务
            session.commit()
            # 获取更新后的记录对象
            updated_user_bind = session.query(UserBind).get(original_id)
            # 输出更新后的记录信息
            update_res = (True, f"修改成功，{updated_user_bind.qq_id}玩家名称由{updated_user_bind.player}修改为{new_player_name}")
        else:
            update_res = (False, f"找不到用户{qq_id}绑定记录")
    except (exc.DisconnectionError, exc.TimeoutError) as e:
        logger.warn(f"数据库连接失败：{str(e)},重试中...")
        return await update_user_player_by_qq_id(uid, player, nucleusId, personaId)
    except Exception as e:
        update_res = (False, f"异常：{e}")
    session.close()
    return update_res


# 执行新增绑定
async def create_new_user_bind(player, platform, qq_id, nucleusId, personaId, support):
    # 创建模型对象
    new_user_bind = UserBind(
        player=player,
        platform=platform,
        qq_id=qq_id,
        nucleusId=nucleusId,
        personaId=personaId,
        support=support
    )
    try:
        # 获取连接对象
        connection = session.connection()
        # 添加模型对象到会话
        session.add(new_user_bind)
        # 提交事务
        session.commit()
        # 输出新增记录信息
        create_res = (True, f"用户 {new_user_bind.qq_id} 绑定至 {new_user_bind.player}")
    except (exc.DisconnectionError, exc.TimeoutError) as e:
        logger.warn(f"数据库连接失败：{str(e)},重试中...")
        return await create_new_user_bind(player, platform, qq_id, nucleusId, personaId, support)
    except IntegrityError as error:
        # 捕捉唯一键冲突异常
        session.rollback()
        # MySQL 唯一键冲突情况下的处理
        if error.orig.args[0] == 1062:  # MySQL 的错误码
            error_message = error.orig.args[1]
            # 从错误消息中提取冲突的值
            conflict_value = error_message.split("'")[1]
            logger.info(f"绑定失败！已存在绑定记录：{conflict_value}")
            create_res = (False, f"绑定失败！已存在绑定记录：{conflict_value}")
        else:
            logger.warn("插入失败！已存在绑定记录：{error.orig}")
            create_res = (False, f"插入失败！已存在绑定记录：{error.orig}")
    session.close()
    return create_res


# 根据条件查询记录
async def check_user_bind_exist(qq_id):
    try:
        result = session.query(UserBind).filter_by(qq_id=qq_id).first()
        # 获取连接对象
        connection = session.connection()
        if result:
            check_res = (True, result.player)
            logger.info(f"QQ号为{qq_id}的绑定记录存在，用户ID为：{result.player}")
        else:
            check_res = (False, 0)
            logger.info(f"QQ号为{qq_id}的没有绑定记录")
    # 添加重连方法
    except (exc.DisconnectionError, exc.TimeoutError) as e:
        logger.warn(f"数据库连接失败：{str(e)},重试中...")
        # 递归调用
        return await check_user_bind_exist(qq_id)
    except Exception as error:
        check_res = (False, -1)
        logger.warn(f"查询失败！{error}")
    session.close()
    return check_res


async def update_user_support_by_qq_id(qq_id, support):
    try:
        # 查询要更新的用户绑定记录
        user_bind = session.query(UserBind).filter_by(qq_id=qq_id).first()
        # 获取连接对象
        connection = session.connection()
        if user_bind:
            # 获取原始记录的id
            original_id = user_bind.id
            # 修改模型对象的属性值
            user_bind.support = support
            # 提交事务
            session.commit()
            # 获取更新后的记录对象
            updated_user_bind = session.query(UserBind).get(original_id)
            flag = "失败"
            if support == 0:
                flag = "取消添加"
            elif support == 1:
                flag = "成功添加"
            # 输出更新后的记录信息
            update_res = (True, f"{flag} {user_bind.qq_id} 成功")
        else:
            update_res = (False, f"找不到 {user_bind.qq_id} 绑定记录")
    except (exc.DisconnectionError, exc.TimeoutError) as e:
        logger.warn(f"数据库连接失败：{str(e)},重试中...")
        return await update_user_support_by_qq_id(qq_id, support)
    except Exception as error:
        update_res = (False, -1)
        print(error)
    session.close()
    return update_res


async def delete_user_bind_by_qq_id(qq_id):
    try:
        result = session.query(UserBind).filter_by(qq_id=qq_id).first()
        # 获取连接对象
        connection = session.connection()
        if result:
            session.delete(result)
            session.commit()
            logger.info(f"成功删除QQ号为{qq_id}的绑定记录")
        else:
            logger.info(f"QQ号为{qq_id}的绑定记录不存在")
    except (exc.DisconnectionError, exc.TimeoutError) as e:
        logger.warn(f"数据库连接失败：{str(e)},重试中...")
        connection.connection.ping(reconnect=True)
        return await delete_user_bind_by_qq_id(qq_id)
    except Exception as error:
        print(error)
    session.close()


async def check_user_support_by_qq_id(uid):
    try:
        result = session.query(UserBind).filter_by(qq_id=uid).first()
        # 获取连接对象
        connection = session.connection()
        if result.support == 1:
            check_res = (True, result.player)
        else:
            check_res = (False, 0)
    except (exc.DisconnectionError, exc.TimeoutError) as e:
        logger.warn(f"数据库连接失败：{str(e)},重试中...")
        return await check_user_support_by_qq_id(uid)
    except Exception as error:
        check_res = (False, -1)
        logger.warn(f"查询失败！{error}")
    session.close()
    return check_res


async def check_group_approve(group_id):
    try:
        result = session.query(WhiteList).filter_by(group_id=group_id).first()
        # 获取连接对象
        connection = session.connection()
        if result.approve == 1:
            check_res = (True, result.group_id)
        else:
            check_res = (False, 0)
    except (exc.DisconnectionError, exc.TimeoutError) as e:
        logger.warn(f"数据库连接失败：{str(e)},重试中...")
        return await check_group_approve(group_id)
    except Exception as error:
        check_res = (False, -1)
        logger.warn(f"查询失败！{error}")
    session.close()
    return check_res


# 修改群审批
async def change_group_approve(group_id, approve):
    result = session.query(WhiteList).filter_by(group_id=group_id).first()
    if result:
        original_id = result.id
        result.approve = approve
        session.commit()
        create_res = (True, f"群 {result.group_id} 审批状态 {result.approve}")
    else:
        new_white_list = WhiteList(
            group_id=group_id,
            approve=approve
        )
        # 添加模型对象到会话
        session.add(new_white_list)
        # 提交事务
        session.commit()
        # 输出新增记录信息
        create_res = (True, f"群 {new_white_list.group_id} 审批状态 {new_white_list.approve}")
        session.close()


class QueryRecord(Base):
    __tablename__ = 'total_record'
    id = Column(Integer, primary_key=True)
    player = Column(String(50))
    qq_id = Column(String(50))
    create_time = Column(DateTime)


async def create_query_record(player, qq_id):
    # 获取当前时间
    create_time = datetime.now()
    # 创建模型对象
    new_record = QueryRecord(
        player=player,
        qq_id=qq_id,
        create_time=create_time
    )
    try:
        # 添加模型对象到会话
        session.add(new_record)
        # 获取连接对象
        connection = session.connection()
        # 提交事务
        session.commit()
    except (exc.DisconnectionError, exc.TimeoutError) as e:
        logger.warn(f"数据库连接失败：{str(e)},重试中...")
        return await create_query_record(player, qq_id)
    except IntegrityError as error:
        # 捕捉唯一键冲突异常
        session.rollback()
        print(f"{error}")
