import os
import sqlite3

import aiohttp

# 路径设置
_path = os.path.dirname(__file__).replace("\\", "/")

DATABASE = _path + '/data/user.db'

_database = None


def get_db():
    global _database
    if _database is None:
        _database = sqlite3.connect(DATABASE)
    return _database


def close_db(exception):
    global _database
    if _database is not None:
        _database.close()


# 添加名单表结构
async def add_user_bind(bot, ev):
    uid = ev.user_id
    if uid == bot.config.SUPERUSERS[0]:
        connect = get_db()
        cursor = connect.cursor()
        sql = """CREATE TABLE user_bind(
                        ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        player TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        qq_id TEXT NOT NULL,
                        nucleusId TEXT,
                        personaId TEXT,
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
async def query_user_bind(bot, ev, page_number=1, page_size=10):
    uid = ev.user_id
    mes = "=====名单=====\n"
    if uid == bot.config.SUPERUSERS[0]:
        connect = get_db()
        cursor = connect.cursor()
        offset = (page_number - 1) * page_size
        sql = f"SELECT player as 玩家名称, qq_id as QQ, platform as 平台 FROM user_bind LIMIT {page_size} OFFSET {offset}"
        cursor.execute(sql)
        users = cursor.fetchall()
        connect.commit()
        for user in users:
            mes += "玩家名称：" + user[0] + "\n" + "QQ：" + user[1] + "\n" + "平台：" + user[2] + "\n\n"
        await bot.send(ev, mes + f"\n 当前页为{page_number}")
    else:
        await bot.send(ev, "无权限")


# 绑定用户
async def bind_user(uid, player):
    mes = ''
    connect = get_db()
    cursor = connect.cursor()
    try:
        info = await get_user_info(player, uid)
    except KeyError as e:
        mes += f"异常：{e}\n"
        return mes
    sql = 'INSERT INTO user_bind(player,platform,qq_id,nucleusId,personaId,support) VALUES (?,?,?,?,?,?);'
    cursor.execute(sql, info)

    connect.commit()
    if cursor.rowcount > 0:
        mes += f"绑定成功，用户{uid}当前绑定的游戏id为：{player}"
    return mes


async def get_user_info(player_name, uid):
    url = f"https://api.gametools.network/bf2042/player/?name={player_name}"
    headers = {
        'accept': 'application/json'
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as response:
                results = await response.json()
        except aiohttp.ClientError as e:
            # 处理网络请求异常
            print(f"网络请求异常: {e}")
            return None

    result = results["results"]
    player_name = player_name.upper()
    index = -1
    for i, player_info in enumerate(result):
        if player_info['name'].upper() == player_name:
            index = i
            break
    if result:
        res = result[index]
        nucleusId = res["nucleusId"]
        personaId = res["personaId"]
        platform = res["platform"]
        name = res["name"]
        info = (name, platform, uid, nucleusId, personaId, 0)
        return info
    else:
        # 抛出自定义异常
        raise KeyError("nucleusId not found")


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
    connect = get_db()
    cursor = connect.cursor()
    data = (support, uid)
    sql = 'UPDATE user_bind SET support =? WHERE qq_id =?'
    cursor.execute(sql, data)

    connect.commit()
    save_path_dir = _path + f'/img/bg/user/{uid}'
    if cursor.rowcount > 0:
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
            connect = get_db()
            cursor = connect.cursor()
            sql = "DELETE FROM user_bind WHERE qq_id = ?"
            result = cursor.execute(sql, (white_id,))

            connect.commit()
            if cursor.rowcount > 0:
                await bot.send(ev, f"{nickname}->移除成功")
    else:
        await bot.send(ev, "无权限")


async def change_bind(uid, player):
    flag = False
    connect = get_db()
    cursor = connect.cursor()
    try:
        info = await get_user_info(player, uid)
    except Exception as e:
        print(f"异常：{e}\n")
        return e
    name = info[0]
    nucleusId = info[3]
    personaId = info[4]
    data = (name, nucleusId, personaId, uid)
    sql = 'UPDATE user_bind SET player = ?, nucleusId = ?, personaId = ? WHERE qq_id = ?'
    cursor.execute(sql, data)

    connect.commit()
    if cursor.rowcount > 0:
        flag = True
    else:
        print("更新失败")
    return flag


# 绑定检查
async def check_user_bind(uid):
    flag = False
    connect = get_db()
    cursor = connect.cursor()
    data = (uid,)
    sql = "SELECT player,platform FROM user_bind WHERE qq_id =?"
    result = cursor.execute(sql, data)
    users = result.fetchall()
    player = ""
    if len(users) > 0:
        player = users[0][0]
        flag = True
    connect.commit()
    res = (player, flag)
    return res


# 支援者检查
async def check_user_support(uid):
    flag = False
    connect = get_db()
    cursor = connect.cursor()
    data = (uid,)
    sql = "SELECT support FROM user_bind WHERE qq_id =?"
    result = cursor.execute(sql, data)
    users = result.fetchall()
    if len(users) > 0:
        if users[0][0] == 1:
            flag = True
    connect.commit()
    return flag


# 支援者检查2
async def check_user_support2(uid, user_name):
    flag = False
    connect = get_db()
    cursor = connect.cursor()
    data = (uid,)
    sql = "SELECT support,player FROM user_bind WHERE qq_id =?"
    result = cursor.execute(sql, data)
    users = result.fetchall()
    if len(users) > 0:
        if users[0][0] == 1:
            db_user = users[0][1]
            db_user = db_user.upper()
            data_user = user_name.upper()
            if db_user == data_user:
                flag = True
    connect.commit()
    return flag
