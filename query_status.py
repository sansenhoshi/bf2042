import json
import re
import logging
import requests
import aiohttp
from nonebot import CommandSession

from hoshino import Service, aiorequests
from hoshino.modules.bf2042.bf2042 import bf_2042_gen_pic, user_img_save
from hoshino.modules.bf2042.user_manager import bind_user, change_bind, check_user_bind, add_support_user, \
    query_user_bind, check_user_support
from hoshino.util import FreqLimiter

sv = Service('2042战绩查询', help_='''
-----常规-----
[.盒+ID] PC战绩查询
[.2042战绩+ID] PC战绩查询
[.2042xbox端战绩+ID] xbox战绩查询
[.2042ps端战绩+ID] ps战绩查询
[.绑定+ID] 绑定游戏id到QQ
[.修改绑定+ID] 修改绑定的游戏id

-----特权-----
[.上传图片] 上传自定义背景
'''.strip())

_freq_lmt = FreqLimiter(15)


@sv.on_prefix('.2042战绩')
async def query_player1(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)
    platform = "pc"
    if player == "":
        flag = await check_user_bind(uid)
        if flag[1]:
            player = flag[0]
        else:
            await bot.send(ev, "未检测到ID,请确认格式是否正确，如果你想快捷查询自己战绩，可以使用[.绑定+自己的游戏id]")
            return
    await bot.send(ev, '查询中，请稍等...')
    try:
        player_data = await query_data(player, platform)
        img_mes = await bf_2042_gen_pic(player_data, platform, bot, ev)
        if "未找到该玩家" in img_mes:
            await bot.send(ev, "未找到该玩家")
            return
        await bot.send(ev, f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]")
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议等等再查')
        print(val_ee)
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系bot维护组')
        print(con_ee)


# def get_player_status(player_id, platform): try: url =
# f"https://api.gametools.network/bf2042/stats/?raw=false&format_values=true&name={player_id}&platform={platform}"
# payload = {} headers = { 'accept': 'application/json' } response = requests.request("GET", url, headers=headers,
# data=payload) result = json.loads(response.text) # 玩家ID playerName = result["userName"] # 总kd kd = result[
# "killDeath"] # 真实kd real_kd = result["infantryKillDeath"] # KPM kpm = result["killsPerMinute"] # 胜率
# winning_percentage = result["winPercent"] # 爆头率 headshots = result["headshots"] # 击杀数 kill = result["kills"] # 死亡数
# death = result["deaths"] # 助攻数 assists = result["killAssists"] # 治疗 healing = result["heals"] # 急救数 revives =
# result["revives"] # 造成伤害 damage = result["damage"] # 游玩时长 time_played = result["timePlayed"] # 最佳专家 best_class =
# result["bestClass"]
#
#         top3weapon = result["weapons"]
#
#         out_list = sorted(top3weapon, key=lambda k: k['kills'], reverse=True)
#         # 前三武器数据
#         # 第一武器
#         top1name = out_list[0]["weaponName"]
#         top1kill = out_list[0]["kills"]
#         top1acc = out_list[0]["accuracy"]
#         top1hs = out_list[0]["headshots"]
#
#         # 第二武器
#         top2name = out_list[1]["weaponName"]
#         top2kill = out_list[1]["kills"]
#         top2acc = out_list[1]["accuracy"]
#         top2hs = out_list[1]["headshots"]
#
#         # 第三武器
#         top3name = out_list[2]["weaponName"]
#         top3kill = out_list[2]["kills"]
#         top3acc = out_list[2]["accuracy"]
#         top3hs = out_list[2]["headshots"]
#
#         # 前三载具数据 载具名 击杀数 kpm 摧毁载具数
#         top3vehicles = result["vehicles"]
#         vehicles_out_list = sorted(top3vehicles, key=lambda k: k['kills'], reverse=True)
#
#         # 第一载具
#         vehicle1name = vehicles_out_list[0]["vehicleName"]
#         vehicle1kill = vehicles_out_list[0]["kills"]
#         vehicle1kpm = vehicles_out_list[0]["killsPerMinute"]
#         vehicle1destroyed = vehicles_out_list[0]["vehiclesDestroyedWith"]
#         # 第二载具
#         vehicle2name = vehicles_out_list[1]["vehicleName"]
#         vehicle2kill = vehicles_out_list[1]["kills"]
#         vehicle2kpm = vehicles_out_list[1]["killsPerMinute"]
#         vehicle2destroyed = vehicles_out_list[1]["vehiclesDestroyedWith"]
#         # 第三载具
#         vehicle3name = vehicles_out_list[2]["vehicleName"]
#         vehicle3kill = vehicles_out_list[2]["kills"]
#         vehicle3kpm = vehicles_out_list[2]["killsPerMinute"]
#         vehicle3destroyed = vehicles_out_list[2]["vehiclesDestroyedWith"]
#         # 挂钩检测，简易版
#         hacker_check(out_list)
#
#         if 2 in hacker_check(out_list):
#             final = random.choice(("rnm，挂钩414😓😓😓", "这人家里没户口本🤣👉🤡"))
#         elif 1 in hacker_check(out_list):
#             final = random.choice(("不好说，建议出他户口💻", "建议详查💻"))
#         elif kpm > 1.00:
#             final = random.choice(("我超，普肉鸽带带我🥰🥰🥰", "🍟：这是群里有名的Pro，请小心.jpg"))
#         else:
#             final = random.choice(("薯薯我呀，自卑起来了😭😭😭", "薯薯心里好苦🥲🥲", "↑这是本群有名的薯薯，请注意爱护"))
#
# message = f"玩家ID：{playerName}\n " \ f"总KD：{kd}\n 真实KD：{real_kd}\n KPM：{kpm}\n 胜率：{winning_percentage}\n 爆头率：{
# headshots} \n 击杀数：{kill}\n " \ f"死亡数：{death}\n 助攻数：{assists}\n 治疗：{healing}\n 急救数：{revives}\n 造成伤害：{damage} \n
# 游玩时长：{time_played}\n " \ f"最佳专家：{best_class} \n\n{final} \n" message2 = f"玩家ID：{playerName}\n TOP3武器数据：\n " \
# f"武器名：{top1name}\n 击杀数：{top1kill}\n 命中率：{top1acc}\n 爆头率：{top1hs}\n\n " \ f"武器名：{top2name}\n 击杀数：{top2kill}\n 命中率：{
# top2acc}\n 爆头率：{top2hs} \n\n " \ f"武器名：{top3name}\n 击杀数：{top3kill}\n 命中率：{top3acc}\n 爆头率：{top3hs}" message3 =
# f"玩家ID：{playerName}\n TOP3载具数据：\n " \ f"载具名：{vehicle1name}\n 击杀数：{vehicle1kill}\n KPM：{vehicle1kpm}\n 摧毁载具数：{
# vehicle1destroyed}\n\n " \ f"载具名：{vehicle2name}\n 击杀数：{vehicle2kill}\n KPM：{vehicle2kpm}\n 摧毁载具数：{
# vehicle2destroyed}\n\n " \ f"载具名：{vehicle3name}\n 击杀数：{vehicle3kill}\n KPM：{vehicle3kpm}\n 摧毁载具数：{
# vehicle3destroyed} " mes = [message, message2, message3]
#
#     except Exception as err:
#         message = "错误，请检查" + str(err) + "\n"
#         message2 = "请检查id是否正确\n"
#         message3 = "xbox请使用.2042xbox端战绩+id\nPS请使用.2042PS端战绩+id"
#         mes = [message, message2, message3]
#     return mes


async def query_data(player, platform):
    url = f"https://api.gametools.network/bf2042/stats/?raw=false&format_values=true&name={player}&platform={platform}"
    headers = {
        'accept': 'application/json'
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            rest = await response.text()
            if "AH-64GX Apache Warchief" in rest:
                rest = rest.replace("AH-64GX ", "")
            result = json.loads(rest)
            return result


async def check_user_status(username):
    flag = False
    url = f"https://api.gametools.network/bf2042/player/?name={username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            play_status = await response.json()

    results = play_status["results"]
    length = len(results)
    if length < 1:
        flag = True
    print(flag)
    return flag


@sv.on_prefix('.盒')
async def query_player2(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)
    platform = "pc"
    if player == "":
        flag = await check_user_bind(uid)
        if flag[1]:
            player = flag[0]
            print(player)
        else:
            await bot.send(ev, "未检测到ID,请确认格式是否正确，如果你想快捷查询自己战绩，可以使用[.绑定+自己的游戏id]")
            return
    await bot.send(ev, '查询中，请稍等...')
    try:
        player_data = await query_data(player, platform)
        img_mes = await bf_2042_gen_pic(player_data, platform, bot, ev)
        if "未找到该玩家" in img_mes:
            await bot.send(ev, "未找到该玩家")
            return
        await bot.send(ev, f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]")
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议等等再查')
        print(val_ee)
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系bot维护组')
        print(con_ee)


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


@sv.on_prefix('.2042ps端战绩')
async def query_player3(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)
    platform = "psn"
    await bot.send(ev, '查询中，请稍等...')
    try:
        player_data = await query_data(player, platform)
        img_mes = await bf_2042_gen_pic(player_data, platform, bot, ev)
        if "未找到该玩家" in img_mes:
            await bot.finish(ev, "未找到该玩家")
        await bot.send(ev, f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]")
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议等等再查')
        print(val_ee)
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系bot维护组')
        print(con_ee)


@sv.on_prefix('.2042xbox端战绩')
async def query_player4(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    if not _freq_lmt.check(uid):
        await bot.send(ev, f'冷却中，剩余时间{int(_freq_lmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    else:
        _freq_lmt.start_cd(uid)
    platform = "xbl"
    await bot.send(ev, '查询中，请稍等...')
    try:
        player_data = await query_data(player, platform)
        img_mes = await bf_2042_gen_pic(player_data, platform, bot, ev)
        if "未找到该玩家" in img_mes:
            await bot.finish(ev, "未找到该玩家")
        await bot.send(ev, f"[CQ:reply,id={mes_id}][CQ:image,file={img_mes}]")
    except ValueError as val_ee:
        await bot.send(ev, '接口异常，建议等等再查')
        print(val_ee)
    except ConnectionError as con_ee:
        await bot.send(ev, '网络异常，请联系bot维护组')
        print(con_ee)


@sv.on_prefix('.绑定')
async def bind_player(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查id是否存在
    if await check_user_status(player):
        await bot.send(ev, "ID不存在，请检查ID")
        return
    # 检查绑定状态
    res = await check_user_bind(uid)
    if res[1]:
        await bot.send(ev, "您已经绑定过了，如果你想修改绑定请发送：[.修改绑定+你的游戏id]")
        return
    res = await bind_user(uid, 'pc', player)
    await bot.send(ev, f"[CQ:reply,id={mes_id}]{res}")


@sv.on_prefix('.修改绑定')
async def change_bind_player(bot, ev):
    mes_id = ev['message_id']
    player = ev.message.extract_plain_text().strip()
    uid = ev.user_id
    # 检查id是否存在
    if await check_user_status(player):
        await bot.send(ev, "ID不存在，请检查ID")
        return
    res = await check_user_bind(uid)
    if not res[1]:
        await bot.send(ev, "您还未绑定，发送  [.绑定 您的游戏ID]  将游戏ID与你的QQ绑定")
        return
    res = await change_bind(uid, player)
    if res:
        await bot.send(ev, f"[CQ:reply,id={mes_id}]成功")
    else:
        await bot.send(ev, f"[CQ:reply,id={mes_id}]失败！请联系维护组")


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
    await query_user_bind(bot, ev)


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
