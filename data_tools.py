import aiohttp
import requests

import base64
import os
import random
from decimal import Decimal
from io import BytesIO

filepath = os.path.dirname(__file__).replace("\\", "/")
bf_ban_url = "https://api.gametools.network/bfban/checkban"


ban_reason = {
    0: "未处理",
    1: "石锤",
    2: "待自证",
    3: "MOSS自证",
    4: "无效举报",
    5: "讨论中",
    6: "需要更多管理投票",
    7: "未知原因封禁",
    8: "刷枪"
}


def hacker_check(weapon_data):
    """
    简易外挂数据检测
    :param weapon_data: 武器数据
    :return: 返回检测的数据标记，
    击杀数大于300切爆头率大于30小于40标记1，
    击杀数大于100切爆头率大于40标记2（基本实锤）
    """
    ignore_type = ["DMR", "Bolt Action", "Railguns", "Lever-Action Carbines", "Sidearm", "Crossbows", "Shotguns"]
    sign = []
    for weapon in weapon_data:
        if weapon["type"] not in ignore_type:
            sign.append(headshot(weapon))
            continue
    return sign


def headshot(weapon):
    sign = 999
    if 30.00 <= float(weapon["headshots"].replace('%', "")) and float(weapon["kills"]) >= 100:
        if float(weapon["headshots"].replace('%', "")) <= 40.00:
            if float(weapon["kills"]) < 200:
                sign = 1
            else:
                sign = 0
        elif float(weapon["headshots"].replace('%', "")) > 40.00:
            if float(weapon["kills"]) < 200:
                sign = 2
            else:
                sign = 3
    return sign


async def get_bf_ban_check(user_name, userids, personaids):
    url = "https://api.gametools.network/bfban/checkban/"
    params = {
        "names": user_name,
        "userids": userids,
        "personaids": personaids
    }
    headers = {'accept': 'application/json'}
    trans = "未查询到相关封禁信息"
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
                        trans = ban_reason[res_data]
    return trans


def search_field_in_json(obj, field_name):
    """
    递归搜索 JSON 对象中的指定字段名
    :param obj: JSON 对象
    :param field_name: 指定的字段名
    :return: 找到的字段值，未找到时返回 None
    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == field_name:
                return value
            else:
                result = search_field_in_json(value, field_name)
                if result is not None:
                    return result
    elif isinstance(obj, list):
        for item in obj:
            result = search_field_in_json(item, field_name)
            if result is not None:
                return result
    else:
        return None
