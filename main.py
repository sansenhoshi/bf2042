import asyncio
import json
import re

import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
from hoshino import Service, aiorequests, log
from .bf2042 import bf_2042_gen_pic, bf_2042_simple_pic, bf_2042_gen_property, bf2042_total
from .data_tools import *
from .picture_tools import *
from .query_server import get_server_list
from .user_manager_cloud import *
from hoshino.util import FreqLimiter
from nonebot import *
from nonebot import permission as perm
from .proc.stats_pic_generator import *

sv = Service('2042战绩查询-改', help_='''
常规----------
[.查  ID]  PC战绩查询
[.武器+ID] 查询武器数据
[.枪械+ID] 另一种查询武器数据的方法
[.载具+ID] 查询载具数据
[.专家+ID] 查询专家数据
[.模式+ID] 查询游戏模式数据
[.地图+ID] 查询地图游玩情况
[.配备+ID] 查询配备数据
另一种查询方式----------
[.数据+ID] 查询文字图片版本玩家数据
[/枪械+ID] 另一种查询武器数据的方法
[/载具+ID] 查询载具数据
[/专家+ID] 查询专家数据
[/模式+ID] 查询游戏模式数据
[/地图+ID] 查询地图游玩情况
[.装置+ID] 查询配备数据
其他操作----------
[.2042战绩+ID] PC战绩查询
[.绑定+ID] 绑定游戏ID到QQ（仅仅支持PC）
[.修改绑定+ID] 修改绑定的游戏id
[.2042门户+门户关键字] 查询门户服务器列表
主机----------
[.2042xbox端战绩+ID] xbox战绩查询
[.2042ps端战绩+ID] ps战绩查询
[.PS绑定+ID] 绑定游戏ID到QQ（仅仅支持PS）
[.XBOX绑定+ID] 绑定游戏ID到QQ（仅仅支持XBOX）
特色----------
[.上传图片] 上传自定义背景（需要请求bot管理员获得）
[.清空背景] 清空所有背景图片
入群检测-----
检测新加群的EA ID
------------------------
感谢帕科的支持 B站关注直播间：850164 谢谢喵
'''.strip())

logger = log.new_logger('bf2042')

# 限频器 30S冷却
_freq_lmt = FreqLimiter(30)

# 限频器白名单
white_group = [630082682]


@sv.on_prefix(('.查', '.武器', '.载具', '.专家', '.配备', '.地图', '.模式'), only_to_me=False)
async def query_player_weapon(bot, ev):
    # 计时器
    start_time = time.time()
    # 设置指令类型字典
    query_type = {
        '.武器': 0,
        '.载具': 1,
        '.专家': 2,
        '.配备': 3,
        '.地图': 4,
        '.模式': 5,
        '.查': 6
    }
    # 指令
    cmd = ev['prefix']
    # 指令匹配值
    match = query_type[cmd]

    cmd_type = "数据" if match == 6 else cmd
    cmd_type = str(cmd_type).replace(".", "")

    mes_id = ev['message_id']
    # 默认平台为pc
    platform = "pc"
    # 获取玩家名称
    player = ev.message.extract_plain_text().strip()
    # 修改个人cd为群cd缓解接口压力
    uid = ev.user_id
    g_id = ev.group_id
    if g_id not in white_group:
        if not _freq_lmt.check(g_id):
            await bot.send(ev, f'[CQ:reply,id={mes_id}]冷却中，剩余时间{int(_freq_lmt.left_time(g_id)) + 1}秒，请适当使用，切勿影响正常聊天')
            return
        else:
            _freq_lmt.start_cd(g_id)

    if player == "":
        flag = await check_bind(uid)
        if flag[0]:
            player = flag[1]
            logger.info(f"用户：{player}")
        else:
            await bot.send(ev, "未检测到ID，请确认格式是否正确。如果你想快捷查询自己的战绩，请使用 [.绑定 游戏ID]")
            return

    await bot.send(ev, f'正在查询 {player} {cmd_type} 数据，请耐心等待...')
    # 添加一条查询记录
    await add_query_record(player=player, qq_id=uid)
    # 获取玩家数据
    data = await query_data(player, platform)
    # 获取联ban结果
    bf_ban_info = ''
    # 获取外挂鉴定结果
    hack_info = get_bf_ban_check()
    # 获取生成数据图片
    img_mes = await pic_generator(data, match, uid, bf_ban_info, hack_info)
    # 获取异常武器图片
    hacker_check(data.weapon_list)
    # 检查玩家是否存在
    if data[0]:
        img_mes, abnormal_weapon = await bf_2042_gen_pic(data[1], platform, ev, sv)
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 3)
        if abnormal_weapon:
            img_mes2 = await abnormal_weapon_img(abnormal_weapon)
            msg = f"[CQ:reply,id={mes_id}]本次查询耗时：{elapsed_time}s[CQ:image,file={img_mes}]\n[CQ:image,file={img_mes2}]"
        else:
            msg = f"[CQ:reply,id={mes_id}]本次查询耗时：{elapsed_time}s[CQ:image,file={img_mes}]"
        # 发送图片
        await bot.send(ev, msg)

    # 检查玩家是否存在
    if data[0]:
        img_mes = await bf2042_total(data[1], platform, ev, sv, match)
        # 发送图片
        end_time = time.time()
        elapsed_time = round(end_time - start_time, 3)
        msg = f"[CQ:reply,id={mes_id}]本次查询耗时：{elapsed_time}s[CQ:image,file={img_mes}]"
        await bot.send(ev, msg)
    # 判断是否存在错误
    else:
        reason = data[1]
        msg = f"[CQ:reply,id={mes_id}]{reason}"
        await bot.send(ev, msg)
