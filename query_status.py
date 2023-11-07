import asyncio
import json
import re

import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
from hoshino import Service, aiorequests
from .bf2042 import bf_2042_gen_pic, bf_2042_simple_pic, bf_2042_gen_property, bf2042_total
from .data_tools import *
from .picture_tools import *
from .query_server import get_server_list
from .user_manager_cloud import *
from hoshino.util import FreqLimiter
from nonebot import *
from nonebot import permission as perm

sv = Service('2042战绩查询', help_='''
-----常规-----
[.盒+ID] PC战绩查询
[.数据+ID] 查询文字图片版本玩家数据
[.武器+ID] 查询武器数据
[.枪械+ID] 另一种查询武器数据的方法
[.载具] 查询载具数据
[.专家] 查询专家数据
[.模式] 查询游戏模式数据
[.地图] 查询地图游玩情况
[.装置] 查询配备数据
[.2042战绩+ID] PC战绩查询
[.绑定+ID] 绑定游戏ID到QQ（仅仅支持PC）
[.修改绑定+ID] 修改绑定的游戏id
[.2042门户+门户关键字] 查询门户服务器列表
-----主机-----
[.2042xbox端战绩+ID] xbox战绩查询
[.2042ps端战绩+ID] ps战绩查询
[.PS绑定+ID] 绑定游戏ID到QQ（仅仅支持PS）
[.XBOX绑定+ID] 绑定游戏ID到QQ（仅仅支持XBOX）
-----特权-----
[.上传图片] 上传自定义背景（需要请求bot管理员获得）
[.清空背景] 清空所有背景图片
-----入群检测-----
检测新加群的EA ID
'''.strip())
# 限频器 30S冷却
_freq_lmt = FreqLimiter(30)


@sv.on_prefix('.2042战绩')
async def query_player1(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    # 修改个人cd为群cd缓解接口压力
    uid = ev.user_id
    g_id = ev.group_id
    if not _freq_lmt.check(g_id):
        await bot.send(ev, f'[CQ:reply,id={mes_id}]冷却中，剩余时间{int(_freq_lmt.left_time(g_id)) + 1}秒，请适当使用，切勿影响正常聊天')
        return
    else:
        _freq_lmt.start_cd(g_id)
    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return
    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, ev, sv)
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


# 解决物品名称过长溢出问题
# 物品名称过滤，将过长物品名将简化
obj_filter = {
    "AH-64GX Apache Warchief": "Apache Warchief",
    "GOL Sniper Magnum": "GOL Magnum",
    "AH-6J Little Bird": "Little Bird",
    "Sd. Kfz 251 Halftrack": "251 Halftrack",
    "9K22 Tunguska-M": "Tunguska-M"
}


def str_filter(obj_str):
    # 遍历字典，替换字符串中的键为对应的值
    for key in obj_filter:
        obj_str = obj_str.replace(key, obj_filter[key])
    return obj_str


async def query_data(player, platform):
    url = f"https://api.gametools.network/bf2042/stats/?raw=false&format_values=true&name={player}&platform={platform}"
    headers = {
        'accept': 'application/json'
    }
    res = (False, "数据请求失败喵")
    retry_options = ExponentialRetry(attempts=2, exceptions=(aiohttp.ClientError,))
    async with RetryClient(retry_options=retry_options) as r_session:
        try:
            async with r_session.get(url, headers=headers, timeout=15) as response:
                rest = await response.text()
                # rest = str_filter(rest)
                if response.status == 200:
                    result = json.loads(rest)
                    # 判断是否查询到玩家数据
                    if 'userName' not in result:
                        res = (False, "未查询到该玩家")
                    else:
                        res = (True, result)
        except asyncio.TimeoutError as e:
            if e:
                res = (False, f"请求超时：{e}")
            else:
                res = (False, f"请求超时：玩家数据请求超时")
        except aiohttp.ClientError as e:
            if e:
                res = (False, f"请求异常：{e}")
            else:
                res = (False, f"请求异常：玩家数据请求异常")
    return res


@sv.on_prefix('.盒')
async def query_player2(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    # 修改个人cd为群cd缓解接口压力
    uid = ev.user_id
    g_id = ev.group_id
    if not _freq_lmt.check(g_id):
        await bot.send(ev, f'[CQ:reply,id={mes_id}]冷却中，剩余时间{int(_freq_lmt.left_time(g_id)) + 1}秒，请适当使用，切勿影响正常聊天')
        return
    else:
        _freq_lmt.start_cd(g_id)

    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, ev, sv)
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix(('.武器', '.载具', '.专家', '.配备'), only_to_me=False)
async def query_player_weapon(bot, ev):
    query_type = {
        '.武器': 0,
        '.载具': 1,
        '.专家': 2,
        '.配备': 3
    }
    cmd = ev['prefix']
    match = query_type[cmd]
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    # 修改个人cd为群cd缓解接口压力
    uid = ev.user_id
    g_id = ev.group_id
    if not _freq_lmt.check(g_id):
        await bot.send(ev, f'[CQ:reply,id={mes_id}]冷却中，剩余时间{int(_freq_lmt.left_time(g_id)) + 1}秒，请适当使用，切勿影响正常聊天')
        return
    else:
        _freq_lmt.start_cd(g_id)

    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf2042_total(data[1], platform, ev, sv, match)
            # 发送图片
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('.数据')
async def query_player2(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    # 修改个人cd为群cd缓解接口压力
    uid = ev.user_id
    g_id = ev.group_id
    if not _freq_lmt.check(g_id):
        await bot.send(ev, f'[CQ:reply,id={mes_id}]冷却中，剩余时间{int(_freq_lmt.left_time(g_id)) + 1}秒，请适当使用，切勿影响正常聊天')
        return
    else:
        _freq_lmt.start_cd(g_id)

    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_simple_pic(data[1], platform, bot, sv)
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('/枪械')
async def query_player2(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)

    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请稍等...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_property(data[1], platform, bot, sv, 'weapons')
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('/载具')
async def query_player2(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)

    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请稍等...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_property(data[1], platform, bot, sv, 'vehicles')
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('/专家')
async def query_player2(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)

    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请稍等...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_property(data[1], platform, bot, sv, 'classes')
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('/模式')
async def query_player2(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)

    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请稍等...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_property(data[1], platform, bot, sv, 'gamemodes')
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('/地图')
async def query_player2(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)

    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请稍等...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_property(data[1], platform, bot, sv, 'maps')
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('/装置')
async def query_player2(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)

    platform = "pc"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请稍等...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_property(data[1], platform, bot, sv, 'gadgets')
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))

# @sv.on_prefix('.2042载具')
# async def query_vehicles(bot, ev):
#     uid = ev.user_id
#     if not _freq_lmt.check(uid):
#         await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒)', at_sender=True)
#         return
#     else:
#         _freq_lmt.start_cd(uid)
#     player = ev.message.extract_plain_text().strip()
#     platform = "pc"
#     await bot.send(ev, '查询中请稍等...')
#     mes = get_player_status(player, platform)
#     await bot.send(ev, mes[2])


@sv.on_prefix('.2042门户')
async def query_vehicles(bot, ev):
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)
    server_name = ev.message.extract_plain_text().strip()
    await bot.send(ev, '查询时间较长，请耐心等待...')
    try:
        # 获取服务器信息列表
        mes = await get_server_list(server_name, sv)
    except Exception as err:
        mes = f"异常:{err}"
    await bot.send(ev, mes)


@sv.on_prefix('.2042ps端战绩')
async def query_player3(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    # 修改个人cd为群cd缓解接口压力
    uid = ev.user_id
    g_id = ev.group_id
    if not _freq_lmt.check(g_id):
        await bot.send(ev, f'[CQ:reply,id={mes_id}]冷却中，剩余时间{int(_freq_lmt.left_time(g_id)) + 1}秒，请适当使用，切勿影响正常聊天')
        return
    else:
        _freq_lmt.start_cd(g_id)
    platform = "psn"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return
    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, ev, sv)
            # 发送图片
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('.2042xbox端战绩')
async def query_player4(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    # 修改个人cd为群cd缓解接口压力
    uid = ev.user_id
    g_id = ev.group_id
    if not _freq_lmt.check(g_id):
        await bot.send(ev, f'[CQ:reply,id={mes_id}]冷却中，剩余时间{int(_freq_lmt.left_time(g_id)) + 1}秒，请适当使用，切勿影响正常聊天')
        return
    else:
        _freq_lmt.start_cd(g_id)
    platform = "xbox"
    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return
    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, ev, sv)
            # 发送图片
            msg = f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]"
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = f"[CQ:reply,id={mes_id}]{reason}"
            await bot.send(ev, msg)
    except ValueError as val_ee:
        msg = '接口异常，建议稍后再查'
        await bot.send(ev, msg)
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        msg = '网络异常，请联系机器人维护组'
        await bot.send(ev, msg)
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('.绑定')
async def bind_player(bot, ev):
    platform = 'pc'
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查绑定状态
    res = await check_bind(uid)
    if res[0]:
        await bot.send(ev, f"[CQ:reply,id={mes_id}]您已经绑定 {res[1]}，如果你想修改绑定请发送：[.修改绑定 你的游戏id]")
        return
    # 检查id是否存在
    await bot.send(ev, f"收到绑定请求，正在检测 {player} 数据是否存在...请耐心等待")
    result = await query_data(player, platform)
    # 统一大写
    player = player.upper()
    if result[0]:
        if player == result[1]['userName'].upper():
            nucleusId = result[1]["userId"]
            personaId = result[1]["id"]
            platform = platform
            name = result[1]["userName"]
            info = (name, platform, uid, nucleusId, personaId, 0)
            sv.logger.info(f"绑定用户：{result[1]['userName']}")
            res = await bind_user(name=name, platform=platform, uid=uid, nucleusId=nucleusId, personaId=personaId)
            img_mes = await bf_2042_simple_pic(result[1], platform, bot, sv)
            msg = f"[CQ:reply,id={mes_id}]{res[1]}[CQ:image,file={img_mes}]"
            await bot.send(ev, msg)
        else:
            msg = f"[CQ:reply,id={mes_id}]失败：{result[1]}，使用[.绑定 游戏id]绑定"
            await bot.send(ev, msg)
    else:
        msg = f"[CQ:reply,id={mes_id}]失败：{result[1]}，使用[.绑定 游戏id]绑定"
        await bot.send(ev, msg)


@sv.on_prefix('.PS绑定')
async def bind_player(bot, ev):
    platform = 'psn'
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查绑定状态
    res = await check_bind(uid)
    if res[0]:
        await bot.send(ev, f"[CQ:reply,id={mes_id}]您已经绑定 {res[1]}，如果你想修改绑定请发送：[.修改绑定 你的游戏id]")
        return
    # 检查id是否存在
    await bot.send(ev, f"收到绑定请求，正在检测 {player} 数据是否存在...请耐心等待")
    result = await query_data(player, platform)
    # 统一大写
    player = player.upper()
    if result[0]:
        if player == result[1]['userName'].upper():
            nucleusId = result[1]["userId"]
            personaId = result[1]["id"]
            platform = platform
            name = result[1]["userName"]
            info = (name, platform, uid, nucleusId, personaId, 0)
            sv.logger.info(f"绑定用户：{result[1]['userName']}")
            res = await bind_user(name=name, platform=platform, uid=uid, nucleusId=nucleusId, personaId=personaId)
            img_mes = await bf_2042_simple_pic(result[1], platform, bot, sv)
            msg = f"[CQ:reply,id={mes_id}]{res[1]}[CQ:image,file={img_mes}]"
            await bot.send(ev, msg)
        else:
            msg = f"[CQ:reply,id={mes_id}]失败：{result[1]}，使用[.绑定 游戏id]绑定"
            await bot.send(ev, msg)
    else:
        msg = f"[CQ:reply,id={mes_id}]失败：{result[1]}，使用[.绑定 游戏id]绑定"
        await bot.send(ev, msg)


@sv.on_prefix('.XBOX绑定')
async def bind_player(bot, ev):
    platform = 'xbox'
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查绑定状态
    res = await check_bind(uid)
    if res[1]:
        await bot.send(ev, f"[CQ:reply,id={mes_id}]您已经绑定 {res[1]}，如果你想修改绑定请发送：[.修改绑定 你的游戏id]")
        return
    # 检查id是否存在
    await bot.send(ev, f"收到绑定请求，正在检测 {player} 数据是否存在...请耐心等待")
    result = await query_data(player, platform)
    # 统一大写
    player = player.upper()
    if result[0]:
        if player == result[1]['userName'].upper():
            nucleusId = result[1]["userId"]
            personaId = result[1]["id"]
            platform = platform
            name = result[1]["userName"]
            info = (name, platform, uid, nucleusId, personaId, 0)
            sv.logger.info(f"绑定用户：{result[1]['userName']}")
            res = await bind_user(name=name, platform=platform, uid=uid, nucleusId=nucleusId, personaId=personaId)
            img_mes = await bf_2042_simple_pic(result[1], platform, bot, sv)
            msg = f"[CQ:reply,id={mes_id}]{res[1]}[CQ:image,file={img_mes}]"
            await bot.send(ev, msg)
        else:
            msg = f"[CQ:reply,id={mes_id}]失败：{result[1]}，使用[.绑定 游戏id]绑定"
            await bot.send(ev, msg)
    else:
        msg = f"[CQ:reply,id={mes_id}]失败：{result[1]}，使用[.绑定 游戏id]绑定"
        await bot.send(ev, msg)


@sv.on_prefix('.修改绑定')
async def change_bind_player(bot, ev):
    flag = await check_bind(ev.user_id)
    platform = 'pc'
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查绑定状态
    res = await check_bind(uid)
    if not res[0]:
        await bot.send(ev, f"[CQ:reply,id={mes_id}]您还未绑定，发送  [.绑定 您的游戏ID]  将游戏ID与你的QQ绑定")
        return
    # 检查id是否存在
    await bot.send(ev, f"收到修改绑定请求，正在检测 {player} 数据是否存在...请耐心等待")
    result = await query_data(player, platform)
    player = player.upper()
    sv.logger.info(f"数据库绑定结果：{flag[0]}")
    if result[0]:
        if player == result[1]['userName'].upper():
            nucleusId = result[1]["userId"]
            personaId = result[1]["id"]
            platform = platform
            name = result[1]["userName"]
            info = (name, platform, uid, nucleusId, personaId, 0)
            sv.logger.info(f"绑定用户：{result[1]['userName']}")
            res = await change_user_bind(uid=uid, player=name, nucleusId=nucleusId, personaId=personaId)
            img_mes = await bf_2042_simple_pic(result[1], platform, bot, sv)
            if res:
                msg = f"[CQ:reply,id={mes_id}]{uid} 成功修改绑定ID {name}[CQ:image,file={img_mes}]"
                await bot.send(ev, msg)
            else:
                await bot.send(ev, f"[CQ:reply,id={mes_id}]失败！请联系维护组")
            return info
        else:
            msg = f"[CQ:reply,id={mes_id}]失败：{result[1]}，请稍后再试"
            await bot.send(ev, msg)
    else:
        msg = f"[CQ:reply,id={mes_id}]失败：{result[1]}，请稍后再试"
        await bot.send(ev, msg)


@sv.on_prefix('.添加名单')
async def add_white_user(bot, ev):
    mes_id = ev.message_id
    uid = ev.user_id
    # 检测是否绑定
    res = await check_bind(uid)
    if not res[0]:
        await bot.send(ev, f"[CQ:reply,id={mes_id}]{uid}未绑定")
        return
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
            if await change_user_support(white_id, 1):
                await bot.send(ev, f"[CQ:reply,id={mes_id}] 添加 {nickname}->成功")
        else:
            await bot.finish(ev, f'[CQ:reply,id={mes_id}] 添加失败')
    else:
        await bot.send(ev, f"[CQ:reply,id={mes_id}] 无权限")


@sv.on_prefix('.清空背景')
async def delete_bg(bot, ev):
    msg_id = ev.message_id
    uid = ev.user_id
    # 检测是否绑定
    res = await check_bind(uid)
    if not res[0]:
        await bot.send(ev, f"[CQ:reply,id={mes_id}]{uid}未绑定")
        return
    is_support = await check_user_support(uid)
    if not is_support[0]:
        await bot.send(ev, f"[CQ:reply,id={msg_id}]{uid}无权限")
        return
    # 保存图片
    try:
        await user_img_delete(uid)
        await bot.send(ev, f"[CQ:reply,id={msg_id}] 清空成功")
    except Exception as e:
        await bot.send(ev, f"[CQ:reply,id={msg_id}] 图片清空失败{e}")


@sv.on_prefix('.移除名单')
async def rm_white_user(bot, ev):
    mes_id = ev.message_id
    uid = ev.user_id
    # 检测是否绑定
    res = await check_bind(uid)
    if not res[0]:
        await bot.send(ev, f"[CQ:reply,id={mes_id}]{uid}未绑定")
        return
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
            if await change_user_support(white_id, 0):
                await bot.send(ev, f"[CQ:reply,id={mes_id}] 移除 {nickname}->成功")
        else:
            await bot.finish(ev, f'[CQ:reply,id={mes_id}] 移除失败')
    else:
        await bot.send(ev, f"[CQ:reply,id={mes_id}] 无权限")


# 上传图片
@sv.on_command('upload_img', aliases=['.上传图片'], only_to_me=False)
async def upload_img(u_session: CommandSession):
    # 获取用户信息
    uid = u_session.event['user_id']
    # 获取消息id
    msg_id = u_session.event['message_id']
    # 检测是否绑定
    is_bind = await check_bind(uid)
    if not is_bind[0]:
        await u_session.send("未绑定")
        return
    #
    is_support = await check_user_support(uid)
    if not is_support[0]:
        await u_session.send(f"[CQ:reply,id={msg_id}]无权限")
        return

    # 获取用户上传的图片并检查格式
    u_session.get('org_img', prompt="请发送一张图片(推荐使用16:9宽高比，效果最好)：")
    org_img = u_session.state['org_img']
    match = re.search("(?<=url=).*?(?=])", str(org_img))
    if not match:
        await u_session.send("无效的图片链接")
        return

    # 获取图片流
    try:
        pic_response = await aiorequests.get(match.group())
        pic_stream = await pic_response.content
    except Exception as e:
        await u_session.send(f"[CQ:reply,id={msg_id}] 图片获取失败{e}")
        return
    # 保存图片
    try:
        await user_img_save(pic_stream, uid)
        await u_session.send(f"[CQ:reply,id={msg_id}] 上传成功")
    except Exception as e:
        await u_session.send(f"[CQ:reply,id={msg_id}] 图片保存失败{e}")


nb_bot = get_bot()

sv2 = Service('入群数据检索', help_='''
入群检测对应ID的游戏数据检索
'''.strip())


@sv2.on_request('bf_group.add')
async def data_check(g_session: RequestSession):
    ev = g_session.event
    self_id = g_session.event['self_id']
    sub_type = g_session.event['sub_type']
    group_id = g_session.event['group_id']
    user_id = g_session.event['user_id']
    comment = g_session.event['comment']
    flag = g_session.event['flag']
    log.info(f"事件id：{flag}")
    mes = f"收到用户：{user_id} \n" \
          f"请求加群\n" \
          f"{comment}"
    mes2 = f"正在获取该用户的游戏数据~"
    await nb_bot.send_group_msg(group_id=group_id, message=mes, self_id=self_id)
    await nb_bot.send_group_msg(group_id=group_id, message=mes2, self_id=self_id)
    if await check_approve(group_id):
        if sub_type == 'add':
            pattern = r"答案：(\w+)"
            match = re.search(pattern, comment)
            if match:
                answer = match.group(1)
                data = await query_data(answer, 'pc')
                if data[0]:
                    img_mes = await bf_2042_gen_pic(data[1], 'pc', nb_bot, ev, sv)
                    message = f"用户：“{user_id}”\n" \
                              f"玩家：“{answer}”\n" \
                              f"游戏数据：\n"
                    msg = f"{message}[CQ:image,file={img_mes}"
                    await nb_bot.send_group_msg(group_id=group_id, message=msg, self_id=self_id)
                else:
                    message = f"用户{user_id}\n" \
                              f"数据获取失败，可能是ID不正确\n" \
                              f"请管理员核实\n" \
                              f"申请内容:{comment}，" \
                              f"查询数据时的报错{data[1]}"
                    await nb_bot.send_group_msg(group_id=group_id, message=message, self_id=self_id)


@on_command('bf_enable', aliases=('.启用审批', '.开启审批'), permission=perm.GROUP, only_to_me=False)
async def enable_approve(a_session: CommandSession):
    group_id = a_session.event['group_id']
    await set_approve(group_id, True)
    await a_session.send(f'已将群{group_id} 的加群审批设置为 {True}')


@on_command('bf_disable', aliases=('.禁用审批', '.关闭审批'), permission=perm.GROUP, only_to_me=False)
async def disable_approve(d_session: CommandSession):
    group_id = d_session.event['group_id']
    await set_approve(group_id, False)
    await d_session.send(f'已将群{group_id} 的加群审批设置为 {False}')
