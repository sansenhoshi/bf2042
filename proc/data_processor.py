import asyncio
import json

import aiohttp
from aiohttp_retry import RetryClient, ExponentialRetry
from .bf_object_dict import *


# 获取玩家数据
async def query_player_data(player_name, nucleusId, personaId, platform):
    """
    :param player_name: 玩家名称
    :param nucleusId: 平台id
    :param personaId: 平台个人id
    :param platform: 游玩平台
    :return:
    """
    # 源数据
    url = f"https://api.gametools.network/bf2042/stats/?raw=true&format_values=false&name={player}&platform={platform}&skip_battlelog=false"
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
                elif response.status == 404:
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


# 简易外挂数据检测
def hacker_check(weapon_data):
    """
    简易外挂数据检测
    :param weapon_data: 武器数据
    :return: 返回检测的数据标记，
    击杀数大于100小于切爆头率大于30小于40标记1，
    击杀数大于100切爆头率大于40标记2（基本实锤）
    """
    ignore_type = ["DMR", "Bolt Action", "Railguns", "Lever-Action Carbines", "Sidearm", "Crossbows", "Shotguns"]
    sign = []
    abnormal_weapon = []
    for weapon in weapon_data:
        if weapon["type"] not in ignore_type:
            weapon_sign, weapon_info = headshot(weapon)
            sign.append(weapon_sign)
            abnormal_weapon.append(weapon_info)
            continue
    return sign, abnormal_weapon


def headshot(weapon):
    sign = 999
    abnormal_weapon = ""
    if 30.00 <= float(weapon["headshots"].replace('%', "")) and float(weapon["kills"]) >= 100:
        if float(weapon["headshots"].replace('%', "")) <= 40.00:
            if float(weapon["kills"]) < 200:
                sign = 1
                abnormal_weapon = weapon
            else:
                sign = 0
                abnormal_weapon = weapon
        elif float(weapon["headshots"].replace('%', "")) > 40.00:
            if float(weapon["kills"]) < 200:
                sign = 2
                abnormal_weapon = weapon
            else:
                sign = 3
                abnormal_weapon = weapon
    return sign, abnormal_weapon


# 获取联ban信息
async def get_bf_ban_check(user_name, userids, personaids):
    url = "https://api.gametools.network/bfban/checkban/"
    params = {
        "names": user_name,
        "userids": userids,
        "personaids": personaids
    }
    headers = {'accept': 'application/json'}
    trans = "未查询到相关信息"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                res = await response.json()
                hacker_name = res["names"][user_name.lower()]["hacker"]
                hacker_userids = res["userids"][f"{userids}"]["hacker"]
                hacker_personaids = res["personaids"][f"{personaids}"]["hacker"]
                if hacker_name:
                    ban_result = res["names"][user_name.lower()]["status"]
                    trans = ban_reason[ban_result]
                elif hacker_userids:
                    ban_result = res["userids"][f"{userids}"]["status"]
                    trans = ban_reason[ban_result]
                elif hacker_personaids:
                    ban_result = res["personaids"][f"{personaids}"]["status"]
                    trans = ban_reason[ban_result]
                else:
                    if "status" in str(res):
                        res_data = search_field_in_json(res, "status")
                        trans = banReason[res_data]
    return trans


# 源数据处理
async def raw_data_proc(raw_data):
    print(raw_data)
    return raw_data
