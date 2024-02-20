import os
import json
import aiohttp

filepath = os.path.dirname(__file__).replace("\\", "/")
bf_ban_url = "https://proxy.sansenhoshi.top/bfban/checkban"

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


async def get_bf_ban_check(user_name, userids, personaids):
    url = "https://proxy.sansenhoshi.top/bfban/checkban/"
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


async def set_approve(group_id, enable):
    check_res = await check_approve(group_id)
    if check_res:
        return f"群：{group_id}已经存在与审批名单中"
    else:
        res = await write_list(group_id, enable)
        if res:
            return f"群：{group_id}已添加至审批名单中"
        else:
            return f"群：{group_id}添加失败"


async def check_approve(group_id):
    path = filepath + "/data/config.json"
    # 读取JSON文件
    with open(path, 'r') as f:
        data = json.load(f)
    # 取出特定键的值
    white_list = data['white_list']
    if group_id in white_list:
        return True
    else:
        return False


async def write_list(group_id, enable):
    try:
        path = filepath + "/data/config.json"
        # 读取JSON文件
        with open(path, 'r') as f:
            data = json.load(f)

        # 更新特定键的值
        white_list = data['white_list']
        if enable:
            white_list.append(group_id)
        else:
            white_list.remove(group_id)
        data['white_list'] = white_list
        print(f"白名单：{white_list}")
        # 将更新后的数据写入JSON文件
        with open(path, 'w') as f:
            json.dump(data, f)
            f.flush()  # 刷新文件缓冲区
            f.close()  # 手动关闭文件

        return True
    except Exception as e:
        return False
