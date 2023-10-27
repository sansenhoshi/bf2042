import asyncio
import json
import re

import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
from hoshino import Service, aiorequests
from hoshino.modules.bf2042.bf2042 import bf_2042_gen_pic, bf_2042_simple_pic, bf2042_weapon
from hoshino.modules.bf2042.data_tools import *
from hoshino.modules.bf2042.picture_tools import user_img_save
from hoshino.modules.bf2042.query_server import get_server_list
from hoshino.modules.bf2042.user_manager import bind_user, change_bind, check_user_bind, add_support_user, \
    query_user_bind, check_user_support
from hoshino.util import FreqLimiter
from nonebot import *
from nonebot import permission as perm

sv = Service('2042战绩查询', help_='''
-----常规-----
[.盒+ID] PC战绩查询
[.数据+ID] 查询文字图片版本玩家数据
[.武器+ID] 查询武器数据
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
[.上传图片] 上传自定义背景
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
        flag = await check_user_bind(uid)
        if flag[1]:
            player = flag[0]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID,请确认格式是否正确，如果你想快捷查询自己战绩，可以使用[.绑定 游戏id]")
            return
    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, bot, ev, sv)
            msg = (MessageSegment.reply(mes_id), MessageSegment.image(img_mes))
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = (MessageSegment.reply(mes_id),MessageSegment.text(reason))
            await bot.send(ev, msg)
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议稍后再查')
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系机器人维护组')
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
    async with RetryClient(retry_options=retry_options) as session:
        try:
            async with session.get(url, headers=headers, timeout=15) as response:
                rest = await response.text()
                rest = str_filter(rest)
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
        flag = await check_user_bind(uid)
        if flag[1]:
            player = flag[0]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, bot, ev, sv)
            msg = (MessageSegment.reply(mes_id), MessageSegment.image(img_mes))
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(reason))
            await bot.send(ev, msg)
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议稍后再查')
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系机器人维护组')
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('.武器')
async def query_player_weapon(bot, ev):
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
        flag = await check_user_bind(uid)
        if flag[1]:
            player = flag[0]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, bot, ev, sv)
            msg = (MessageSegment.reply(mes_id), MessageSegment.image(img_mes))
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(reason))
            await bot.send(ev, msg)
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议稍后再查')
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系机器人维护组')
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
        flag = await check_user_bind(uid)
        if flag[1]:
            player = flag[0]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, bot, ev, sv)
            msg = (MessageSegment.reply(mes_id), MessageSegment.image(img_mes))
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(reason))
            await bot.send(ev, msg)
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议稍后再查')
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系机器人维护组')
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
        flag = await check_user_bind(uid)
        if flag[1]:
            player = flag[0]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID,请确认格式是否正确，如果你想快捷查询自己战绩，可以使用[.绑定 游戏id]")
            return
    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, bot, ev, sv)
            msg = (MessageSegment.reply(mes_id), MessageSegment.image(img_mes))
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(reason))
            await bot.send(ev, msg)
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议稍后再查')
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系机器人维护组')
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
        flag = await check_user_bind(uid)
        if flag[1]:
            player = flag[0]
            sv.logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID,请确认格式是否正确，如果你想快捷查询自己战绩，可以使用[.绑定 游戏id]")
            return
    await bot.send(ev, '查询中，请耐心等待...')
    try:
        data = await query_data(player, platform)
        # 检查玩家是否存在
        if data[0]:
            img_mes = await bf_2042_gen_pic(data[1], platform, bot, ev, sv)
            msg = (MessageSegment.reply(mes_id), MessageSegment.image(img_mes))
            # 发送图片
            await bot.send(ev, msg)
        # 判断是否存在错误
        else:
            reason = data[1]
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(reason))
            await bot.send(ev, msg)
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议稍后再查')
        sv.logger.error(f"异常：{str(val_ee)}")
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系机器人维护组')
        sv.logger.error("异常：" + str(con_ee))


@sv.on_prefix('.绑定')
async def bind_player(bot, ev):
    platform = 'pc'
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查绑定状态
    res = await check_user_bind(uid)
    if res[1]:
        await bot.send(ev, "您已经绑定过了，如果你想修改绑定请发送：[.修改绑定 你的游戏id]")
        return
    # 检查id是否存在
    await bot.send(ev, f"收到绑定请求，正在检测 {player} 数据是否存在...请耐心等待")
    result = await query_data(player, platform)
    player = player.upper()
    if result[0]:
        if player == result['userName'].upper():
            nucleusId = result["userId"]
            personaId = result["id"]
            platform = platform
            name = result["userName"]
            info = (name, platform, uid, nucleusId, personaId, 0)
            sv.logger.info(f"绑定用户：{result['userName']}")
            res = await bind_user(info)
            img_mes = await bf_2042_simple_pic(result, platform, bot, ev, sv)
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"绑定成功！"), MessageSegment.image(img_mes))
            await bot.send(ev, msg)
        else:
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"{result[1]}，使用[.绑定 游戏id]即可完成绑定"))
            await bot.send(ev, msg)
    else:
        msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"{result[1]}，使用[.绑定 游戏id]即可完成绑定"))
        await bot.send(ev, msg)


@sv.on_prefix('.PS绑定')
async def bind_player(bot, ev):
    platform = 'psn'
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查绑定状态
    res = await check_user_bind(uid)
    if res[1]:
        await bot.send(ev, "您已经绑定过了，如果你想修改绑定请发送：[.修改绑定 你的游戏id]")
        return
    # 检查id是否存在
    await bot.send(ev, f"收到绑定请求，正在检测 {player} 数据是否存在...请耐心等待")
    result = await query_data(player, platform)
    player = player.upper()
    if result[0]:
        if player == result['userName'].upper():
            nucleusId = result["userId"]
            personaId = result["id"]
            platform = platform
            name = result["userName"]
            info = (name, platform, uid, nucleusId, personaId, 0)
            sv.logger.info(f"绑定用户：{result['userName']}")
            res = await bind_user(info)
            img_mes = await bf_2042_simple_pic(result, platform, bot, ev, sv)
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"绑定成功！"), MessageSegment.image(img_mes))
            await bot.send(ev, msg)
        else:
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"{result[1]}，使用[.绑定 游戏id]即可完成绑定"))
            await bot.send(ev, msg)
    else:
        msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"{result[1]}，使用[.绑定 游戏id]即可完成绑定"))
        await bot.send(ev, msg)


@sv.on_prefix('.XBOX绑定')
async def bind_player(bot, ev):
    platform = 'xbox'
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查绑定状态
    res = await check_user_bind(uid)
    if res[1]:
        await bot.send(ev, "您已经绑定过了，如果你想修改绑定请发送：[.修改绑定 你的游戏id]")
        return
    # 检查id是否存在
    await bot.send(ev, f"收到绑定请求，正在检测 {player} 数据是否存在...请耐心等待")
    result = await query_data(player, platform)
    player = player.upper()
    if result[0]:
        if player == result['userName'].upper():
            nucleusId = result["userId"]
            personaId = result["id"]
            platform = platform
            name = result["userName"]
            info = (name, platform, uid, nucleusId, personaId, 0)
            sv.logger.info(f"绑定用户：{result['userName']}")
            res = await bind_user(info)
            img_mes = await bf_2042_simple_pic(result, platform, bot, ev, sv)
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"绑定成功！"), MessageSegment.image(img_mes))
            await bot.send(ev, msg)
        else:
            msg = (MessageSegment.reply(mes_id),MessageSegment.text(f"{result[1]}，使用[.绑定 游戏id]即可完成绑定"))
            await bot.send(ev, msg)
    else:
        msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"{result[1]}，使用[.绑定 游戏id]即可完成绑定"))
        await bot.send(ev, msg)


@sv.on_prefix('.修改绑定')
async def change_bind_player(bot, ev):
    flag = await check_user_bind(ev.user_id)
    platform = flag[2]
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查绑定状态
    res = await check_user_bind(uid)
    if not res[1]:
        await bot.send(ev, "您还未绑定，发送  [.绑定 您的游戏ID]  将游戏ID与你的QQ绑定")
        return
    # 检查id是否存在
    await bot.send(ev, f"收到修改绑定请求，正在检测 {player} 数据是否存在...请耐心等待")
    result = await query_data(player, platform)
    player = player.upper()
    sv.logger.info(f"数据库绑定结果：{flag}")
    if result[0]:
        if player == result['userName'].upper():
            nucleusId = result["userId"]
            personaId = result["id"]
            platform = platform
            name = result["userName"]
            info = (name, platform, uid, nucleusId, personaId, 0)
            sv.logger.info(f"绑定用户：{result['userName']}")
            res = await change_bind(info)
            img_mes = await bf_2042_simple_pic(result, platform, bot, sv)
            if res:
                msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"{uid} 成功修改ID {name}"), MessageSegment.image(img_mes))
                await bot.send(ev, msg)
            else:
                await bot.send(ev, f"[CQ:reply,id={mes_id}]失败！请联系维护组")
            return info
        else:
            msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"{result[1]}"))
            await bot.send(ev, msg)
    else:
        msg = (MessageSegment.reply(mes_id), MessageSegment.text(f"{result[1]}"))
        await bot.send(ev, msg)


@sv.on_prefix('.添加名单')
async def add_white_user(bot, ev):
    uid = ev.user_id
    # 检测是否绑定
    is_bind, _ = await check_user_bind(uid)
    if not is_bind:
        await bot.send(ev, "未绑定")
        return
    await add_support_user(bot, ev)


@sv.on_prefix('.查询名单')
async def query_user(bot, ev):
    num = ev.message.extract_plain_text().strip()
    num = int(num)
    await query_user_bind(bot, ev, num)


# 上传图片
@sv.on_command('upload_img', aliases=['.上传图片'], only_to_me=False)
async def upload_img(session: CommandSession):
    # 获取用户信息
    uid = session.event['user_id']

    # 检测是否绑定
    is_bind, _ = await check_user_bind(uid)
    if not is_bind:
        await session.send("未绑定")
        return
    # 检测是否有权限
    if not await check_user_support(uid):
        await session.send("无权限")
        return

    # 获取用户上传的图片并检查格式
    session.get('org_img', prompt="请发送一张16:9宽高比的图片：")
    org_img = session.state['org_img']
    match = re.search("(?<=url=).*?(?=])", str(org_img))
    if not match:
        await session.send("无效的图片链接")
        return

    # 获取图片流
    try:
        pic_response = await aiorequests.get(match.group())
        pic_stream = await pic_response.content
    except Exception as e:
        await session.send("图片获取失败")
        return
    # 保存图片
    try:
        await user_img_save(pic_stream, uid)
        await session.send("上传成功")
    except Exception as e:
        await session.send("图片保存失败")


nb_bot = get_bot()

sv2 = Service('入群数据检索', help_='''
入群检测对应ID的游戏数据检索
'''.strip())


@sv2.on_request('bf_group.add')
async def data_check(session: RequestSession):
    ev = session.event
    self_id = session.event['self_id']
    sub_type = session.event['sub_type']
    group_id = session.event['group_id']
    user_id = session.event['user_id']
    comment = session.event['comment']
    flag = session.event['flag']
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
                    msg = (MessageSegment.text(message), MessageSegment.image(img_mes))
                    await nb_bot.send_group_msg(group_id=group_id, message=msg, self_id=self_id)
                else:
                    message = f"用户{user_id}\n" \
                              f"数据获取失败，可能是ID不正确\n"\
                              f"请管理员核实\n" \
                              f"申请内容:{comment}，"\
                              f"查询数据时的报错{data[1]}"
                    msg = MessageSegment.text(message)
                    await nb_bot.send_group_msg(group_id=group_id, message=msg, self_id=self_id)


@on_command('bf_enable', aliases=('.启用审批', '.开启审批'), permission=perm.GROUP, only_to_me=False)
async def enable_approve(session: CommandSession):
    group_id = session.event['group_id']
    await set_approve(group_id, True)
    await session.send(f'已将群{group_id} 的加群审批设置为 {True}')


@on_command('bf_disable', aliases=('.禁用审批', '.关闭审批'), permission=perm.GROUP, only_to_me=False)
async def disable_approve(session: CommandSession):
    group_id = session.event['group_id']
    await set_approve(group_id, False)
    await session.send(f'已将群{group_id} 的加群审批设置为 {False}')
