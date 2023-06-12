import sqlite3
import os
# 路径设置
_path = os.path.dirname(__file__).replace("\\", "/")


# 添加名单表结构
async def add_user_bind_db(bot, ev):
    uid = ev.user_id
    if uid == bot.config.SUPERUSERS[0]:
        connect = sqlite3.connect(database=f'{_path}/data/user.db')
        cursor = connect.cursor()
        sql = """CREATE TABLE user_bind(
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        player TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        qq_id TEXT NOT NULL,
                        support INTEGER NOT NULL 
                        );"""
        res = cursor.execute(sql)
        cursor.close()
        connect.commit()
        connect.close()
        if res.rowcount > 0:
            await bot.send(ev, "创建成功！")
    else:
        await bot.send(ev, "无权限")


# 查询白名单
async def query_user_bind(bot, ev):
    uid = ev.user_id
    mes = "=====名单=====\n"
    if uid == bot.config.SUPERUSERS[0]:
        connect = sqlite3.connect(database=f'{_path}/data/user.db')
        cursor = connect.cursor()
        sql = "SELECT player as 玩家名称,qq_id as QQ,platform as 平台 FROM user_bind"
        result = cursor.execute(sql)
        users = result.fetchall()
        for user in users:
            mes += "玩家名称：" + user[0] + "\n" + "QQ：" + user[1] + "\n" + "平台：" + user[2] + "\n\n"
        cursor.close()
        connect.commit()
        connect.close()
        await bot.send(ev, mes)
    else:
        await bot.send(ev, "无权限")


# 绑定用户
async def bind_user(uid, platform, player):
    mes = ''
    connect = sqlite3.connect(database=f'{_path}/data/user.db')
    cursor = connect.cursor()
    support = 0
    info = (player, platform, uid, support)
    sql = 'INSERT INTO user_bind(player,platform,qq_id,support) VALUES (?,?,?,?);'
    res = cursor.execute(sql, info)
    cursor.close()
    connect.commit()
    connect.close()
    if res.rowcount > 0:
        mes += f"绑定成功，用户{uid}当前绑定的游戏id为：\n{player}"
    return mes


# 添加支援者专属
async def add_support_user(bot, ev):
    # 获取指令发送者的qq
    su_uid = ev.user_id
    # 获取当前群号
    cu_gid = ev.group_id
    # 判断是否为bot管理员
    if su_uid == bot.config.SUPERUSERS[0]:
        # 判断是否为at消息
        if ev.message[0].type == 'at':
            white_id = ev.message[0].data['qq']
            data1 = await bot.get_group_member_info(group_id=cu_gid, user_id=white_id)
            nickname = data1['card'] if len(data1['card']) != 0 else data1['nickname']
            if await update_support(white_id, 1):
                await bot.send(ev, f"添加 {nickname}->成功")
        else:
            await bot.finish(ev, '添加失败')
    else:
        await bot.send(ev, "无权限")


# 添加支援者专属
async def update_support(uid, support):
    flag = False
    connect = sqlite3.connect(database=f'{_path}/data/user.db')
    cursor = connect.cursor()
    data = (support, uid)
    sql = 'UPDATE user_bind SET support =? WHERE qq_id =?'
    res = cursor.execute(sql, data)
    cursor.close()
    connect.commit()
    connect.close()
    save_path_dir = _path + f'/img/bg/user/{uid}'
    if res.rowcount > 0:
        if not os.path.exists(save_path_dir):
            os.makedirs(save_path_dir)
        flag = True
    else:
        print("更新失败")
    return flag


# 移除白名单
async def delete_user_bind(bot, ev):
    # 获取指令发送者的qq
    su_uid = ev.user_id
    # 获取当前群号
    cu_gid = ev.group_id
    # 判断是否为bot管理员
    if su_uid == bot.config.SUPERUSERS[0]:
        # 判断是否为at消息
        if ev.message[0].type == 'at':
            white_id = ev.message[0].data['qq']
            data1 = await bot.get_group_member_info(group_id=cu_gid, user_id=white_id)
            nickname = data1['card'] if len(data1['card']) != 0 else data1['nickname']
            connect = sqlite3.connect(database=f'{_path}/data/user.db')
            cursor = connect.cursor()
            sql = f"""DELETE FROM user_bind WHERE qq_id = '{white_id}'"""
            result = cursor.execute(sql)
            cursor.close()
            connect.commit()
            connect.close()
            if result.rowcount > 0:
                await bot.send(ev, f"{nickname}->移除成功")
    else:
        await bot.send(ev, "无权限")


async def change_bind(uid, player):
    flag = False
    connect = sqlite3.connect(database=f'{_path}/data/user.db')
    cursor = connect.cursor()
    data = (player, uid)
    sql = 'UPDATE user_bind SET player =? WHERE qq_id =?'
    res = cursor.execute(sql, data)
    cursor.close()
    connect.commit()
    connect.close()
    if res.rowcount > 0:
        flag = True
    else:
        print("更新失败")
    return flag


# 绑定检查
async def check_user_bind(uid):
    flag = False
    connect = sqlite3.connect(database=f'{_path}/data/user.db')
    cursor = connect.cursor()
    data = (uid,)
    sql = "SELECT player,platform FROM user_bind WHERE qq_id =?"
    result = cursor.execute(sql, data)
    users = result.fetchall()
    player = ""
    if len(users) > 0:
        player = users[0][0]
        print(player)
        flag = True
    cursor.close()
    connect.commit()
    connect.close()
    res = (player, flag)
    return res


# 支援者检查
async def check_user_support(uid):
    flag = False
    connect = sqlite3.connect(database=f'{_path}/data/user.db')
    cursor = connect.cursor()
    data = (uid,)
    sql = "SELECT support FROM user_bind WHERE qq_id =?"
    result = cursor.execute(sql, data)
    users = result.fetchall()
    if len(users) > 0:
        if users[0][0] == 1:
            print(users[0][0])
            flag = True
    cursor.close()
    connect.commit()
    connect.close()
    return flag


# 支援者检查2
async def check_user_support2(uid, user_name):
    flag = False
    connect = sqlite3.connect(database=f'{_path}/data/user.db')
    cursor = connect.cursor()
    data = (uid,)
    sql = "SELECT support,player FROM user_bind WHERE qq_id =?"
    result = cursor.execute(sql, data)
    users = result.fetchall()
    if len(users) > 0:
        if users[0][0] == 1:
            db_user = users[0][1]
            print(type(db_user))
            db_user = db_user.upper()
            data_user = user_name.upper()
            if db_user == data_user:
                flag = True
    cursor.close()
    connect.commit()
    connect.close()
    return flag
