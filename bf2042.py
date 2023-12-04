import base64
import os
import random
from decimal import Decimal
from io import BytesIO

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from .data_tools import hacker_check, get_bf_ban_check
from .picture_tools import draw_rect, circle_corner, png_resize, \
    get_top_object_img, \
    image_paste, get_favorite_image, get_user_avatar, paste_ic_logo, get_avatar, get_special_icon, draw_point_line
from .user_manager_cloud import *

classesList = {
    "Mackay": "   麦凯",
    "Angel": "   天使",
    "Falck": "  法尔克",
    "Paik": "  白智秀",
    "Sundance": "   日舞",
    "Dozer": "  推土机",
    "Rao": "   拉奥",
    "Lis": "   莉丝",
    "Irish": "爱尔兰佬",
    "Crawford": "克劳福德",
    "Boris": "  鲍里斯",
    "Zain": "   扎因",
    "Casper": "  卡斯帕",
    "Blasco": "布拉斯科",
    "BF3 Recon": "BF3 侦察",
    "BF3 Support": "BF3 支援",
    "BF3 Assault": "BF3 突击",
    "BF3 Engineer": "BF3 工程",
    "BC2 Recon": "BC2 侦察",
    "BC2 Medic": "BC2 医疗",
    "BC2 Assault": "BC2 突击",
    "BC2 Engineer": "BC2 工程",
    "1942 Anti-tank": "1942 反坦克",
    "1942 Assault": "1942 突击",
    "1942 Medic": "1942 医疗",
    "1942 Engineer": "1942 工程",
    "1942 Scout": "1942 侦察",
}

classes_type_list = {
    "Assault": "突击兵",
    "Support": "支援兵",
    "Recon": "侦察兵",
    "Engineer": "工程兵"
}

bf_object_dice = {
    "PP-29": "PP-29",
    "MP9": "MP9",
    "K30": "K30",
    "PBX-45": "PBX-45",
    "SWS-10": "SWS-10",
    "NTW-50": "NTW-50",
    "DXR-1": "DXR-1",
    "AM40": "AM40",
    "VCAR": "VCAR",
    "Ghostmaker R10": "鬼魂制造者",
    "BSV-M": "BSV-M",
    "G57": "G57",
    "M44": "M44",
    "MCS-880": "MCS-880",
    "12M Auto": "12M Auto",
    "MP28": "MP28",
    "Rorsch Mk-4": "罗氏 Mk-4",
    "Avancys": "阿凡西斯",
    "PKP-BP": "PKP-BP",
    "LCMG": "LCMG",
    "M24 Sniper": "M24 狙击",
    "M16A3": "M16A3",
    "GVT 45-70": "GVT杠杆步枪",
    "P90": "P90",
    "PF51": "PF51",
    "AC-42": "AC-42",
    "AK-24": "AK-24",
    "M5A3": "M5A3",
    "SFAR-M GL": "SFAR-M GL",
    "K98 Sniper": "K98 狙击",
    "DM7": "DM7",
    "AKS-74u": "AKS-74u",
    "M240B": "M240B",
    "MP412 REX": "MP412 REX",
    "MP443": "MP443",
    "M93R": "M93R",
    "SPAS-12": "SPAS-12",
    "M60E4": "M60E4",
    "M39 EMR": "M39 EMR",
    "A-91": "A-91",
    "SVD": "SVD",
    "ACW-R": "ACW-R",
    "M98B": "M98B",
    "M416": "M416",
    "SCAR-H": "SCAR-H",
    "AEK-971": "AEK-971",
    "NVK-P125": "NVK-P125",
    "NVK-S22": "NVK-S22",
    "SVK": "SVK",
    "XM8 Compact": "XM8紧凑型",
    "StG 44": "StG 44",
    "M2 Carbine": "M2 卡宾",
    "PP-2000": "PP-2000",
    "M1911": "M1911",
    "DAO-12": "DAO-12",
    "Type 88": "88式",
    "M249 SAW": "M249 SAW",
    "XM8 LMG": "XM8 轻机枪",
    "GOL Sniper Magnum": "GOL马格南",
    "M60": "M60",
    "M1 Garand": "M1 加兰德",
    "M95 Sniper": "M95 狙击",
    "XM8 Prototype": "XM8原型",
    "MP 40": "MP 40",
    "Walther P38": "瓦尔特P38",
    "BAR 1918": "BAR 1918",
    "Bren LMG": "布伦轻机枪",
    "AN94": "AN94",
    "K98": "K98",
    "G3A3": "G3A3",
    "AS Val": "AS Val",
    "M1 Garand Sniper": "M1加兰德 狙击",
    "M16A2": "M16A2",
    "No 4": "No 4",
    "No 4 Sniper": "4号 狙击",
    "Gewerhr 43 ZF4": "格韦尔43 ZF4",
    "Gewerhr 43": "格韦尔43",
    "Thompson": "汤普森冲锋枪",
    "RPT-3": "RPT-3",
    "AC9": "AC9",
    "Super 500": "超级500",
    "RM68": "RM68",
    "MTAR-21": "MTAR-21",
    "Mk VI Revolver": "MkVI 左轮",
    "RPK-74M": "RPK-74M",
    "XCE BAR": "XCE BAR",
    "GEW-46": "GEW-46",
    "BFP.50": "BFP.50",
    "12G Automatic": "12G Automatic",
    "Sten": "斯登冲锋枪",
    "Melee": "近战",
    "G3": "G3",
    "Panzerschreck": "坦克杀手",
    "VHX D3": "VHX D3",
    "MD540 Nightbird": "MD540 夜莺",
    "F-35E Panther": "F-35E 黑豹",
    "M5C Bolte": "M5C 博尔特",
    "AH-64GX Apache Warchief": "阿帕奇",
    "MV-38 Condor": "MV-38 鱼鹰",
    "EBAA Wildcat": "EBAA 小野猫",
    "M1A5": "M1A5",
    "RAH-68 Huron": "RAH-68 休伦",
    "LATV4 Recon": "LATV4 侦察",
    "AH-6J Little Bird": "AH-6J 小鸟",
    "LCAA Hovercraft": "LCAA气垫船",
    "EBLC-Ram": "EBLC-Ram",
    "MAV": "MAV",
    "EMKV90-TOR": "EMKV90-TOR",
    "UH-60": "UH-60",
    "LAV-AD": "LAV-AD",
    "M1A2": "M1A2",
    "M1114": "M1114",
    "M1161 ITV": "M1161 ITV",
    "LAV-25": "LAV-25",
    "AH-64 Apache": "AH-64 阿帕奇",
    "AAV-7A1 AMTRAC": "AAV-7A1 AMTRAC",
    "M3A3 Bradley": "布拉德利步战车",
    "M4 Sherman": "M4 谢尔曼",
    "Willys MB": "威利斯吉普",
    "M10 Wolverine": "M10 狼獾",
    "Spitfire": "喷火",
    "B-17 Bomber": "B-17 轰炸机",
    "M3 Halftrack": "M3 半履带装甲车",
    "F/A-18": "F/A-18",
    "A-10 Warthog": "A-10 疣猪",
    "SU-57 FELON": "SU-57 重罪犯",
    "Mi-240 Super Hind": "Mi-240 雌鹿",
    "YG-99 Hannibal": "YG-99 汉尼拔",
    "Ju-87 Stuka": "Ju-87 斯图卡",
    "Bf 109": "BF 109",
    "BMP-2": "BMP-2",
    "Su-35BM": "Su-35BM",
    "Tiger I": "虎式 I",
    "VDV Buggy": "VDV 越野",
    "Sd. Kfz 251 Halftrack": "1942 德 半履带装甲车",
    "Kubelwagen": "库伯沃格",
    "9K22 Tunguska-M": "通古斯卡-M",
    "T-90": "T-90",
    "3937 Vodnik": "3937 沃德尼克",
    "Z-11W": "直-11W",
    "Mi-28 Havoc": "Mi-28 浩劫",
    "Panzer IV": "四号坦克",
    "KA-520 Super Hokum": "卡520",
    "T28": "T28",
    "CAV-BRAWLER": "CAV-格斗士",
    "9M133 Kornet": "9M133 短号",
    "Polaris Sportsman": "北极星Sportsman",
    "Polaris RZR": "北极星RZR",
    "Su-25TM Frogfoot": "Su-25TM 蛙足",
    "Mi-24 Hind": "Mi-24 雌鹿",
    "BMD-3": "BMD3步兵车",
    "Tuk-Tuk": "嘟嘟车",
    "4x4 Utility": "固定防空炮",
    "UAV-1": "UAV-1",
    "Flak 38": "Flak 38",
    "HMG": "HMG",
    "KORD HMG": "Kord重机枪",
    "Quadbike - BC2": "四轮摩托车 - BC2",
    "RHIB - BF3": "汽艇 - BF3",
    "C5 Explosive [Kingston]": "C5 炸药",
    "SOB-8 Ballistic Shield": "SOB-8 防弹盾",
    "Carl Gustaf M5": "M5无后座力炮",
    "Frag Grenade": "破片手雷",
    "Anti Armor": "反装甲",
    "Scatter Grenade": "分裂手雷-日舞",
    "Repair Tool": "修理工具",
    "SG-36 Sentry Gun": "SG-36 哨兵机枪",
    "EMP Grenade": "EMP 手雷",
    "Anti-Tank Grenade": "反坦克手雷",
    "Mini Grenade": "迷你手雷",
    "Ammo Box BF3 (Portal)": "弹药箱 BF3",
    "Ammo Box BC2 (Portal)": "弹药箱 BC2",
    "Grappling Hook": "抓钩",
    "Cyber Warfare Suite (Signal Hacker)": "网络战套件",
    "Medkit BF3 (Portal)": "医疗箱 BF3",
    "Medkit BF1942 (Portal)": "医疗箱 BF1942",
    "Medkit BF2 (Portal)": "医疗箱 BF2",
    "Motion Sensor (Portal)": "运动传感器",
    "OV-P Recon Drone": "OV-P 侦察无人机",
    "Repair Tool BF3 (Portal)": "修理工具 BF3",
    "Repair Tool BF1942 (Portal)": "修理工具BF1942",
    "Repair Tool BC2 (Portal)": "修理工具 BC2",
    "S21 Syrette Pistol": "S21注射器手枪",
    "T-UGS (Portal)": "无线地面传感器 (门户)",
    "Ammo Crate": "弹药箱",
    "IBA Armor Plate": "装甲板",
    "C4 [Portal]": "C4炸药",
    "M18 Claymore": "M18 阔剑",
    "Defibrillator": "除颤器",
    "Defibrillator (BC2)": "除颤器 BC2",
    "Defibrillator (BF3)": "除颤器 BF3",
    "FGM-148 Javelin": "FGM-148 标枪",
    "Medical Crate": "医疗箱",
    "Med-Pen (Self-heal)": "医疗针 (自回复)",
    "AT Mine [Kingston]": "反坦克地雷",
    "Mortar Strike": "迫击炮打击",
    "Insertion Beacon (Spawn) (Portal)": "插入重生信标 (门户)",
    "RPG-7": "RPG-7",
    "SMAW": "SMAW",
    "ExpPack": "炸药包",
    "Concussion Grenade": "震荡手雷",
    "Incendiary Grenade": "燃烧弹",
    "Smoke Grenade": "烟雾弹",
    "Prox Sensor (Motion)": "接近传感器（运动）",
    "Throwing Knife": "飞刀",
    "Smoke Grenade Launcher": "烟雾榴弹发射器",
    "Lindmine": "地雷",
    "XM370A": "XM370A空爆",
    "FXM-33 AA Missile": "FXM-33 毒刺",
    "Smoke Grenade Launchers": "烟雾榴弹发射器",
    "M136 AT4": "AT-4",
    "G-84 TGM": "G-84 TV导弹",
    "Bazooka": "巴祖卡",
    "SA-18 Igla": "SA-18 针式",
    "Binoculars BF1942": "双筒望远镜 BF1942",
    "Crate": "Crate",
    "Pouch": "Pouch",
    "Insertion Beacon (Spawn)": "插入重生信标",
    "BF1942 Grenade": "BF1942 手雷",
    "BC2 Grenade": "BC2 手雷",
    "BF3 Grenade": "BF3 手雷",
    "Mounted Vulcan": "火神加特林",
    "RPG-7v2": "RPG-7v2",
    "SPH Explosive Launcher": "SPH 发射器",
    "Spring Grenade": "弹跳手雷",
    "EOD Bot - BF3": "排爆机器人 BF3",
    "Call In Tablet": "平板电脑",
    "Intel Scanner": "扫描套件",
    "AT-Mine": "反坦克地雷",
    "Stick Grenade": "手榴弹",
    "G428": "G428"
}

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

nameList = {
    'weapons': 'weaponName',
    'vehicles': 'vehicleName',
    'gamemodes': 'gamemodeName',
    'maps': 'mapName',
    'gadgets': 'gadgetName',
    'classes': 'characterName'
}

parse_content = {
    'weapons': ['weaponName', 'kills', 'killsPerMinute', 'headshots', 'accuracy'],
    'vehicles': ['vehicleName', 'kills', 'killsPerMinute', 'destroyed'],
    'classes': ['characterName', 'kills', 'kpm', 'revives', 'secondsPlayed'],
    'gamemodes': ['gamemodeName', 'kills', 'kpm', 'winPercent'],
    'maps': ['mapName', 'wins', 'winPercent', 'secondsPlayed'],
    'gadgets': ['gadgetName', 'kills', 'uses', 'vehiclesDestroyedWith']
}

parse_size = {
    'weapons': [(52, 26), (5, 2)],
    'vehicles': [(50, 13), (5, 8)],
    'classes': [(23, 26), (17, 2)],
    'gamemodes': [(26, 26), (17, 2)],
    'maps': [(52, 21), (5, 4)],
    'gadgets': [(26, 26), (17, 2)]
}

parse_str = {
    'weaponName': '武器:',
    'kills': '击杀:',
    'killsPerMinute': 'KPM:',
    'headshots': '爆头率:',
    'accuracy': '精准度:',
    'vehicleName': '载具:',
    'characterName': '专家:',
    'gamemodeName': '模式:',
    'mapName': '地图:',
    'gadgetName': '装置:',
    'destroyed': '摧毁:',
    'kpm': 'KPM:',
    'killDeath': 'KD:',
    'winPercent': '胜率:',
    'wins': '胜场:',
    'secondsPlayed': '游玩时长(h):',
    'uses': '使用次数:',
    'vehiclesDestroyedWith': '摧毁载具:',
    'revives': '急救数:',
    'weapons': '武器',
    'vehicles': '载具',
    'gamemodes': '模式',
    'maps': '地图',
    'gadgets': '装置',
    'classes': '专家'
}

map_list = {
    "Renewal": "涅槃（复兴）",
    "Orbital": "航天发射中心",
    "Manifest": "货物仓单",
    "Discarded": "废弃之地",
    "Kaleidescope": "万花筒",
    "Breakaway": "分崩离析",
    "Hourglass": "沙漏",
    "Spearhead": "急先锋",
    "Exposure": "曝光",
    "Stranded": "搁浅",
    "Noshahr Canals": "诺沙运河",
    "Caspian Border": "里海边境",
    "Valparaiso": "瓦尔帕莱索",
    "Arica Harbor": "阿里卡港",
    "Battle of the Bulge": "突出部之役",
    "El Alamein": "阿拉曼",
    "Flashpoint": "焦点",
    "Reclaimed": "重生",
    "Redacted": "删隐地区"
}

game_mode = {
    "Breakthrough": "突破",
    "Breakthrough Small": "突破（小型）",
    "Breakthrough Large": "突破（大型）",
    "Conquest": "征服",
    "Conquest Small": "征服（小型）",
    "Conquest Large": "征服（大型）",
    "Rush": "突袭模式",
    "Modbuilder Custom": "门户自定义",
    "Hazard Zone": "危险地带",
    "Hazard Zone Large": "危险地带（大）",
    "Hazard Zone Small": "危险地带（小）",
    "Custom": "自定义模式"
}

'''2042图片战绩生成'''
filepath = os.path.dirname(__file__).replace("\\", "/")
bf_ban_url = "https://api.gametools.network/bfban/checkban"


async def bf_2042_gen_pic(data, platform, ev, sv):
    # 1.创建黑色板块 1920*1080
    new_img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 1000))
    # 2.获取头像图片 150*150
    platform_id = 1
    nucleus_id = data['userId']
    persona_id = data['id']
    # 调用接口获取正确的头像(由于某些人的自爆头像，现在获取ea头像仅对绑定用户生效，其他的一律不显示ea头像)
    res = await check_bind(ev.user_id)
    if res[0] and res[1].upper() == data["userName"].upper():
        avatar = await get_avatar(platform_id, persona_id, nucleus_id, sv)
    else:
        avatar = Image.open(filepath + "/img/class_icon/No-Pats.png")
    avatar = png_resize(avatar, new_width=145, new_height=145)
    avatar = circle_corner(avatar, 10)
    # 3.获取背景 并 模糊
    # 判断是否为support
    support_res = await check_user_support(ev.user_id)
    if support_res[0]:
        sv.logger.info("用户特权：自定义背景图片")
        img = get_favorite_image(ev.user_id)
    else:
        sv.logger.info("普通用户：常规背景图片")
        bg_name = os.listdir(filepath + "/img/bg/common/")
        index = random.randint(0, len(bg_name) - 1)
        img = Image.open(filepath + f"/img/bg/common/{bg_name[index]}").convert('RGBA').resize((1920, 1080))
    # img_filter = img.filter(ImageFilter.GaussianBlur(radius=3))
    # 4.拼合板块+背景+logo
    new_img.paste(img, (0, 0))
    if support_res[0] and support_res[1].upper() == data["userName"].upper():
        logo = get_user_avatar(ev.user_id)
    else:
        logo = Image.open(filepath + "/img/bf2042_logo/bf2042logo.png").convert('RGBA')
    logo = png_resize(logo, new_width=145, new_height=145)
    logo = circle_corner(logo, 10)
    new_img = image_paste(logo, new_img, (1750, 30))
    # 5.绘制头像框 (x1,y1,x2,y2)
    # x2 = x1+width+img_width+width
    # y2 = y1+width+img_height+width
    draw = ImageDraw.Draw(new_img)
    new_img = draw_rect(new_img, (25, 25, 768, 180), 10, fill=(0, 0, 0, 150))
    # 6添加头像
    new_img = image_paste(avatar, new_img, (30, 30))
    # 7.添加用户信息文字

    # # 等级计算
    # xp = data["XP"][0]["total"]
    # unit = 93944
    # level = int((xp \\ unit) + 0.55)
    # color = 'white'
    # if int((xp \\ 93944) + 0.55) > 0:
    #     level = ('S' + str(level - 99))
    #     color = '#FF3333'

    # 载入字体
    en_text_font = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 36)
    ch_text_font = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 36)
    # 获取用化名
    player_name = data["userName"]
    plat = Image.open(filepath + "/img/platform/origin.png").convert("RGBA").resize((40, 40))
    if platform == "pc":
        plat = Image.open(filepath + "/img/platform/origin.png").convert("RGBA").resize((40, 40))
    elif platform == "psn":
        plat = Image.open(filepath + "/img/platform/playstation.png").convert("RGBA").resize((40, 40))
    elif platform == "xbl":
        plat = Image.open(filepath + "/img/platform/xbox.png").convert("RGBA").resize((40, 40))
    draw.text((208, 33), '玩家：', fill='white', font=ch_text_font)
    draw.text((308, 30), f'{player_name}', fill='white', font=en_text_font)
    # 游玩平台
    # draw.rectangle([208, 120, 248, 160], fill="black")
    # r, g, b, alpha = plat.split()
    # new_img.paste(plat, (208, 120), mask=alpha)
    new_img = image_paste(plat, new_img, (208, 120))
    draw.text((260, 120), '游玩时长：', fill='white', font=ch_text_font)
    time_played = data["timePlayed"]
    if ',' in time_played:
        times = time_played.split(',')
        if "days" in times[0]:
            times_1 = int(times[0].replace("days", "").strip()) * 24
        else:
            times_1 = int(times[0].replace("day", "").strip()) * 24
        times_2 = times[1].split(':')
        time_part2 = int(times_2[0]) + Decimal(int(times_2[1]) / 60).quantize(Decimal("0.00"))
        time_played = str(times_1 + time_part2)
    else:
        time_part2 = Decimal(int(time_played.split(':')[1]) / 60).quantize(Decimal("0.00"))
        time_played = int(time_played.split(':')[0]) + time_part2
    draw.text((430, 118), f'{time_played} H', fill='white', font=en_text_font)
    # 8.绘制最佳专家外框
    # 获取兵种图标
    best_class = sorted(data["classes"], key=lambda k: k['kills'], reverse=True)[0]
    # 专家名称
    best_specialist = best_class["characterName"]
    # 专家击杀数
    best_specialist_kills = best_class["kills"]
    # 专家kpm
    best_specialist_kpm = best_class["kpm"]
    # 专家kd
    best_specialist_kill_death = best_class["killDeath"]
    # 游玩时长
    seconds = best_class["secondsPlayed"]
    best_specialist_played = round(seconds / 3600, 2)
    # 专家图标
    class_icon = await get_special_icon(best_class, sv)
    # 图像缩放
    class_icon = class_icon.resize((90, 90))
    # class_icon = png_resize(class_icon, new_width=90, new_height=90)
    # (300, 360)
    # 绘制最佳专家
    ch_text_font_bc = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 38)
    ch_text_font_s = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 30)
    new_img = draw_rect(new_img, (768 + 25, 25, 1318, 180), 10, fill=(0, 0, 0, 150))
    draw.text((815, 55), '最 佳', fill='lightgreen', font=ch_text_font_bc)
    draw.text((815, 105), '专 家', fill='lightgreen', font=ch_text_font_bc)
    new_img = image_paste(class_icon, new_img, (930, 35))
    spec_name = classesList[best_specialist]
    draw.text((918, 130), f'{spec_name}', fill='skyblue', font=ch_text_font_s)
    draw.text((1050, 40), f' K/D：{best_specialist_kill_death}', fill='white', font=ch_text_font_s)
    draw.text((1050, 73), f'KPM：{best_specialist_kpm}', fill='white', font=ch_text_font_s)
    draw.text((1050, 105), f'击杀：{best_specialist_kills}', fill='white', font=ch_text_font_s)
    draw.text((1050, 138), f'时长：{best_specialist_played} H', fill='white', font=ch_text_font_s)

    # 9.MVP/最佳小队
    # 绘制最佳小队/MVP
    new_img = draw_rect(new_img, (1318 + 25, 25, 1920 - 195, 180), 10, fill=(0, 0, 0, 150))
    # 游玩场数
    matches = data["matchesPlayed"]
    # mvp
    mvp = "MVP：" + str(data["mvp"])
    # 神射手距离
    total_long_distance = data['dividedKills']['longDistance']
    p_round_long_distance = data['dividedKills']['inRound']['longDistance']
    playerTakeDowns = data['playerTakeDowns']
    # 最佳小队
    best_squad = "最佳小队：" + str(data["bestSquad"])
    best_show = random.choice((mvp, best_squad))
    ch_text_font2 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 36)
    draw.text((1368, 30), f'游玩场数: {matches}', fill='white', font=ch_text_font2)
    draw.text((1368, 80), f'{best_show}', fill='white', font=ch_text_font2)
    ch_text_font_s = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    draw.text((1368, 130), f'处决: {playerTakeDowns}', fill='white', font=ch_text_font_s)

    # 10.绘制生涯框
    new_img = draw_rect(new_img, (25, 205, 1920 - 25, 455), 10, fill=(0, 0, 0, 150))
    ch_text_font3 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font3 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 36)
    # 分割的击杀数据
    divided_kills = data["dividedKills"]
    # 处理击杀玩家的百分比
    kill_human_per = data["humanPrecentage"]
    kill_human_per = float(kill_human_per.strip('%')) / 100
    # kd
    kd = data["killDeath"]
    # 四舍五入计算真实KD
    real_kd = round(kill_human_per * kd, 2)
    # 击杀数
    kills = data["kills"]
    # kpm
    kpm = data["killsPerMinute"]
    # 真实kpm
    real_kpm = round(kill_human_per * kpm, 2)
    # 步战kd
    infantryKillDeath = data["infantryKillDeath"]
    # 场均击杀
    k_per_match = data["killsPerMatch"]
    # 爆头率
    hs = data["headshots"]
    # 命中率
    acc = data["accuracy"]
    # 胜场
    win = data["winPercent"]
    # 人类百分比
    human_per = data["humanPrecentage"]
    # AI击杀数量
    AI_kill = divided_kills["ai"]
    # 阵亡
    deaths = data["deaths"]
    # 急救
    revives = data["revives"]
    # 标记敌人数
    eme = data["enemiesSpotted"]
    # 摧毁载具数量
    vehiclesDestroyed = data["vehiclesDestroyed"]
    # 载具击杀数
    vehicle_kill = divided_kills["vehicle"]
    # 数据1
    draw.text((150, 220), f'K/D： {kd}', fill='white', font=ch_text_font3)
    draw.text((150, 265), f'真实 K/D： {infantryKillDeath}', fill='white', font=ch_text_font3)
    draw.text((150, 310), f'击杀： {kills}', fill='white', font=ch_text_font3)
    draw.text((150, 355), f'载具击杀： {vehicle_kill}', fill='white', font=ch_text_font3)
    draw.text((150, 400), f'死亡数： {deaths}', fill='white', font=ch_text_font3)

    # 数据2
    draw.text((550, 220), f'KPM： {kpm}', fill='white', font=ch_text_font3)
    draw.text((550, 265), f'真实KPM： {real_kpm}', fill='white', font=ch_text_font3)
    draw.text((550, 310), f'爆头率： {hs}', fill='white', font=ch_text_font3)
    draw.text((550, 355), f'命中率： {acc}', fill='white', font=ch_text_font3)
    draw.text((550, 400), f'胜率： {win}', fill='white', font=ch_text_font3)

    # 数据3
    draw.text((950, 220), f'AI击杀： {AI_kill}', fill='white', font=ch_text_font3)
    draw.text((950, 265), f'场均击杀： {k_per_match}', fill='white', font=ch_text_font3)
    draw.text((950, 310), f'急救数： {revives}', fill='white', font=ch_text_font3)
    draw.text((950, 355), f'标记敌人数： {eme}', fill='white', font=ch_text_font3)
    draw.text((950, 400), f'摧毁载具数： {vehiclesDestroyed}', fill='white', font=ch_text_font3)

    # 数据4 BF TRACKER个人主页
    # en_text_font_ext = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 24)
    # qr_img = qr_code_gen(player_name, platform)
    # qr_img = qr_img.resize((145, 145))
    # draw.text((1300, 228), "BATTLEFIELD\n    TRACKER", fill="lightgreen", font=en_text_font_ext)
    # new_img.paste(qr_img, (1300, 290))

    weapon_list = sorted(data["weapons"], key=lambda k: k['kills'], reverse=True)

    # 数据5 简易检测器
    hacker_check_res = hacker_check(weapon_list)
    final = "未知"
    color = "white"
    check_res = False

    if 3 in hacker_check_res:
        final = "鉴定为红橙黄绿蓝紫\n没有青吗？"
        color = "#FF9999"
        check_res = True
    elif 2 in hacker_check_res:
        final = "挂？\n样本太少了"
        color = "yellow"
        check_res = True
    elif 1 in hacker_check_res:
        final = "数据不对？\n样本太少了"
        color = "yellow"
        check_res = True
    elif 0 in hacker_check_res:
        final = "可疑？\n建议详查"
        color = "yellow"
        check_res = True
    if not check_res:
        # kpm大于1 总kd大于2 真实kd大于1.5
        if kpm > 1.00 and kd > 2 and real_kd > 1.5:
            final = "Pro哥\n你带我走吧T_T"
            color = "gold"
        else:
            final = "薯薯\n别拷打我了哥>_<"
            color = "skyblue"

    ch_text_font_ext = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    ch_text_font_ext2 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 28)
    draw.text((1300, 220), f'机器棱鉴定结果（仅供参考）：', fill="white", font=ch_text_font_ext)
    draw.text((1300, 240), f'\n{final}', fill=f"{color}", font=ch_text_font_ext2)

    # 添加BF ban 检测结果
    bf_ban_res = await get_bf_ban_check(data["userName"], data["userId"], data["id"])
    draw.text((1300, 360), f'联BAN查询：', fill="white", font=ch_text_font_ext)
    draw.text((1300, 380), f'\n{bf_ban_res}', fill="yellow", font=ch_text_font_ext2)

    # 11.绘制第三部分 TOP4武器/载具 947.5-12.5
    new_img = draw_rect(new_img, (25, 480, 1920 - 25, 1080 - 25), 10, fill=(0, 0, 0, 150))
    ch_text_font4 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font4 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 32)

    # 武器部分
    top_weapon_list = sorted(data["weapons"], key=lambda k: k['kills'], reverse=True)
    height = 500
    line_height = 845
    for i in range(0, 5):
        # 1
        # 修饰线条
        if i < 3:
            draw.line([45, height + 5, 45, height + 85], fill="#CCFF00", width=5, joint=None)
        else:
            draw.line([45, line_height, 45, line_height + 80], fill="#66CCFF", width=5, joint=None)
            line_height += 110
        new_img = image_paste(get_top_object_img(top_weapon_list[i], sv).resize((160, 80)), new_img, (50, height + 5))
        draw.text((230, height), f'{top_weapon_list[i]["weaponName"]}', fill="white", font=en_text_font4)
        draw.text((230, height + 45), f'击杀：{top_weapon_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((450, height), f'爆头率：{top_weapon_list[i]["headshots"]}', fill="white", font=ch_text_font4)
        draw.text((450, height + 45), f'命中率：{top_weapon_list[i]["accuracy"]}', fill="white", font=ch_text_font4)

        draw.text((730, height), f'KPM：{top_weapon_list[i]["killsPerMinute"]}', fill="white", font=ch_text_font4)
        draw.text((730, height + 45), f'时长：{int(int(top_weapon_list[i]["timeEquipped"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        height += 110

    # 分割线
    draw.line([950, 505, 950, 1030], fill="white", width=5, joint=None)
    # 载具部分
    top_vehicles_list = sorted(data["vehicles"], key=lambda k: k['kills'], reverse=True)
    height = 500
    line_height = 845
    for n in range(0, 5):
        # 修饰线条
        if n < 3:
            draw.line([975, height + 5, 975, height + 85], fill="#CCFF00", width=5, joint=None)
        else:
            draw.line([975, line_height, 975, line_height + 80], fill="#66CCFF", width=5, joint=None)
            line_height += 110
        if not top_vehicles_list[n].get("vehicleName"):
            if top_vehicles_list[n].get("type"):
                vehicle_name = top_vehicles_list[n].get("type")
            else:
                vehicle_name = top_vehicles_list[n].get("id")
        else:
            vehicle_name = top_vehicles_list[n]["vehicleName"]
        new_img = image_paste(get_top_object_img(top_vehicles_list[n], sv).resize((320, 80)), new_img,
                              (980, height + 5))
        draw.text((1325, height), f'{vehicle_name}', fill="white", font=en_text_font4)
        draw.text((1325, height + 45), f'击杀：{top_vehicles_list[n]["kills"]}', fill="white", font=ch_text_font4)
        draw.text((1630, height), f'KPM：{top_vehicles_list[n]["killsPerMinute"]}', fill="white", font=ch_text_font4)
        draw.text((1630, height + 45), f'摧毁数：{top_vehicles_list[n]["vehiclesDestroyedWith"]}', fill="white",
                  font=ch_text_font4)
        height += 110

    # 添加开发团队logo
    new_img = paste_ic_logo(new_img)
    # 图片处理完成 发送
    sv.logger.info(f"玩家：{player_name}->图片处理完成")
    # 显示图片
    # new_img.show()
    b_io = BytesIO()
    new_img.save(b_io, format="PNG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str


async def bf_2042_simple_pic(data, platform, bot, sv):
    # 基本信息
    bestClass = data['bestClass']
    player = data['userName']
    kills = data['kills']
    killDeath = data['killDeath']
    infantryKillDeath = data['infantryKillDeath']
    killPerMin = data['killsPerMinute']
    headshots = data['headShots']
    accuracy = data['accuracy']
    playtime = data['secondsPlayed']
    matchesPlay = data['matchesPlayed']
    kill_AI = data['dividedKills']['ai']
    # 处理击杀玩家的百分比
    kill_human_per = data["humanPrecentage"]
    kill_human_per = float(kill_human_per.strip('%')) / 100
    # 四舍五入计算真实KD
    real_kd = round(kill_human_per * killDeath, 2)
    # 真实kpm
    real_kpm = round(kill_human_per * killPerMin, 2)

    # 武器信息
    weapons = data['weapons']
    weapons = pd.DataFrame(weapons)
    weapons.sort_values(by='kills', axis=0, inplace=True, ascending=False)
    weapons = weapons.reset_index(drop=True)

    # 载具信息
    vehicles = data['vehicles']
    vehicles = pd.DataFrame(vehicles)
    vehicles.sort_values(by='kills', axis=0, inplace=True, ascending=False)
    vehicles = vehicles.reset_index(drop=True)

    # 专家信息
    classes = data['classes']
    classes = pd.DataFrame(classes)
    classes.sort_values(by='kills', axis=0, inplace=True, ascending=False)
    classes = classes.reset_index(drop=True)

    ch_text_font = ImageFont.truetype(filepath + '/font/msyh.ttc', 18)

    new_img = Image.new('RGBA', (750, 750), (0, 0, 0, 1000))
    # 背景
    img = Image.open(filepath + '/img/bg/common/bf2042s6.jpg')
    new_img.paste(img, (0, 0))
    draw = ImageDraw.Draw(new_img)

    # 添加BF ban 检测结果
    bf_ban_res = await get_bf_ban_check(data["userName"], data["userId"], data["id"])
    ch_text_font_s = ImageFont.truetype(filepath + '/font/msyh.ttc', 16)
    draw.text((400, 18), f'联BAN查询：' + f'{bf_ban_res}', fill="#5093ff", font=ch_text_font_s)

    # 数据5 简易检测器
    weapon_list = sorted(data["weapons"], key=lambda k: k['kills'], reverse=True)
    hacker_check_res = hacker_check(weapon_list)
    final = "未知"
    color = "white"
    check_res = False

    if 3 in hacker_check_res:
        final = "鉴定为红橙黄绿蓝紫，没有青吗？(筹沙币💣)"
        color = "#FF9999"
        check_res = True
    elif 2 in hacker_check_res:
        final = "挂？样本太少了🤨"
        color = "yellow"
        check_res = True
    elif 1 in hacker_check_res:
        final = "数据不对？样本太少了🤨"
        color = "yellow"
        check_res = True
    elif 0 in hacker_check_res:
        final = "可疑？建议详查🤨"
        color = "yellow"
        check_res = True
    if not check_res:
        # kpm大于1 总kd大于2 真实kd大于1.5
        if killPerMin > 1.00 and killDeath > 2 and real_kd > 1.5:
            final = "Pro哥，你带我走吧T_T（薯条好吃🍟）"
            color = "gold"
        else:
            final = "薯薯，别拷打我了哥>_<（KFC-VIVO-50）"
            color = "skyblue"

    draw.text((400, 0), f'{final}', fill=f"{color}", font=ch_text_font_s)

    draw.text((5, 15), '玩家名称：' + player, fill='white', font=ch_text_font)
    draw.text((5, 38), '击杀：' + str(kills) + '，KD：' + str(killDeath) + '，KPM：' + str(killPerMin) + '，步战KD：' + str(
        infantryKillDeath) + '，AI击杀：' + str(kill_AI) + '，真·KD：' + str(real_kd) + '\n爆头率：' + str(
        headshots) + '，精准度：' + str(accuracy) + '，游玩时间：' + str(round(playtime / 3600)) + '小时，游玩场数：' + str(
        matchesPlay) + '，真·KPM：' + str(real_kpm), fill='white', font=ch_text_font)

    draw.text((5, 80), '========================武器信息========================', fill='red', font=ch_text_font)
    for index in range(0, 10):
        height = 100 + 20 * index
        draw.text((5, height), str(index + 1) + ' : ', fill='white', font=ch_text_font)
        weapon_name = bf_object_dice[weapons.loc[index]['weaponName']]
        draw.text((50, height), weapon_name, fill='white', font=ch_text_font)
        draw.text((150, height), '击杀数：' + str(weapons.loc[index]['kills']), fill='white', font=ch_text_font)
        draw.text((300, height), 'KPM：' + str(weapons.loc[index]['killsPerMinute']), fill='white', font=ch_text_font)
        draw.text((420, height), '爆头率：' + str(weapons.loc[index]['headshots']), fill='white', font=ch_text_font)
        draw.text((570, height), '精准度：' + str(weapons.loc[index]['accuracy']), fill='white', font=ch_text_font)

    draw.text((5, 300), '========================载具信息========================', fill='red', font=ch_text_font)
    for index in range(0, 10):
        height = 320 + 20 * index
        draw.text((5, height), str(index + 1) + ' : ', fill='white', font=ch_text_font)
        vehicle_name = bf_object_dice[str(vehicles.loc[index]['vehicleName'])]
        draw.text((50, height), vehicle_name, fill='white', font=ch_text_font)
        draw.text((250, height), '击杀数：' + str(vehicles.loc[index]['kills']), fill='white', font=ch_text_font)
        draw.text((400, height), 'KPM：' + str(vehicles.loc[index]['killsPerMinute']), fill='white', font=ch_text_font)
        draw.text((520, height), '摧毁数：' + str(vehicles.loc[index]['destroyed']), fill='white', font=ch_text_font)

    draw.text((5, 520), '========================专家信息========================', fill='red', font=ch_text_font)

    for index in range(0, 10):
        height = 540 + 20 * index
        draw.text((5, height), str(index + 1) + ' : ', fill='white', font=ch_text_font)
        draw.text((50, height), classesList[classes.loc[index]['characterName']], fill='white', font=ch_text_font)
        draw.text((170, height), '击杀数：' + str(classes.loc[index]['kills']), font=ch_text_font)
        draw.text((320, height), 'KPM：' + str(classes.loc[index]['kpm']), fill='white', font=ch_text_font)
        draw.text((450, height), 'KD：' + str(classes.loc[index]['killDeath']), fill='white', font=ch_text_font)
        draw.text((550, height), '游玩时间：' + str(round(classes.loc[index]['secondsPlayed'] / 3600)) + '小时', fill='white',
                  font=ch_text_font)

    # 图片处理完成 发送
    sv.logger.info(f"玩家：{player}->图片处理完成")
    # 显示图片
    # new_img.show()
    b_io = BytesIO()
    new_img.save(b_io, format="PNG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str


async def bf2042_total(data, platform, ev, sv, match):
    # 1.创建黑色板块 1920*1080
    new_img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 1000))
    # 2.获取头像图片 150*150
    platform_id = 1
    nucleus_id = data['userId']
    persona_id = data['id']
    # 调用接口获取正确的头像(由于某些人的自爆头像，现在获取ea头像仅对绑定用户生效，其他的一律不显示ea头像)
    res = await check_bind(ev.user_id)
    if res[0] and res[1].upper() == data["userName"].upper():
        avatar = await get_avatar(platform_id, persona_id, nucleus_id, sv)
    else:
        avatar = Image.open(filepath + "/img/class_icon/No-Pats.png")
    avatar = png_resize(avatar, new_width=145, new_height=145)
    avatar = circle_corner(avatar, 10)
    # 3.获取背景 并 模糊
    support_res = await check_user_support(ev.user_id)
    if support_res[0]:
        sv.logger.info("用户特权：自定义背景图片")
        img = get_favorite_image(ev.user_id)
    else:
        sv.logger.info("普通用户：常规背景图片")
        bg_name = os.listdir(filepath + "/img/bg/common/")
        index = random.randint(0, len(bg_name) - 1)
        img = Image.open(filepath + f"/img/bg/common/{bg_name[index]}").convert('RGBA').resize((1920, 1080))
    # img_filter = img.filter(ImageFilter.GaussianBlur(radius=3))
    # 4.拼合板块+背景+logo
    new_img.paste(img, (0, 0))
    if support_res[0] and support_res[1].upper() == data["userName"].upper():
        logo = get_user_avatar(ev.user_id)
    else:
        logo = Image.open(filepath + "/img/bf2042_logo/bf2042logo.png").convert('RGBA')
    logo = png_resize(logo, new_width=145, new_height=145)
    logo = circle_corner(logo, 10)
    new_img = image_paste(logo, new_img, (1750, 30))
    # 5.绘制头像框 (x1,y1,x2,y2)
    draw = ImageDraw.Draw(new_img)
    new_img = draw_rect(new_img, (25, 25, 768, 180), 10, fill=(0, 0, 0, 150))
    # 6添加头像
    new_img = image_paste(avatar, new_img, (30, 30))

    # 载入字体
    en_text_font = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 36)
    ch_text_font = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 36)
    # 获取用化名
    player_name = data["userName"]
    plat = Image.open(filepath + "/img/platform/origin.png").convert("RGBA").resize((40, 40))
    if platform == "pc":
        plat = Image.open(filepath + "/img/platform/origin.png").convert("RGBA").resize((40, 40))
    elif platform == "psn":
        plat = Image.open(filepath + "/img/platform/playstation.png").convert("RGBA").resize((40, 40))
    elif platform == "xbl":
        plat = Image.open(filepath + "/img/platform/xbox.png").convert("RGBA").resize((40, 40))
    draw.text((208, 33), '玩家：', fill='white', font=ch_text_font)
    draw.text((308, 30), f'{player_name}', fill='white', font=en_text_font)
    # 游玩平台
    new_img = image_paste(plat, new_img, (208, 120))
    draw.text((260, 120), '游玩时长：', fill='white', font=ch_text_font)
    time_played = data["timePlayed"]
    if ',' in time_played:
        times = time_played.split(',')
        if "days" in times[0]:
            times_1 = int(times[0].replace("days", "").strip()) * 24
        else:
            times_1 = int(times[0].replace("day", "").strip()) * 24
        times_2 = times[1].split(':')
        time_part2 = int(times_2[0]) + Decimal(int(times_2[1]) / 60).quantize(Decimal("0.00"))
        time_played = str(times_1 + time_part2)
    else:
        time_part2 = Decimal(int(time_played.split(':')[1]) / 60).quantize(Decimal("0.00"))
        time_played = int(time_played.split(':')[0]) + time_part2
    draw.text((430, 118), f'{time_played} H', fill='white', font=en_text_font)
    # 8.绘制最佳专家外框
    # 获取兵种图标
    best_class = sorted(data["classes"], key=lambda k: k['kills'], reverse=True)[0]
    # 专家名称
    best_specialist = best_class["characterName"]
    # 专家击杀数
    best_specialist_kills = best_class["kills"]
    # 专家kpm
    best_specialist_kpm = best_class["kpm"]
    # 专家kd
    best_specialist_kill_death = best_class["killDeath"]
    # 游玩时长
    seconds = best_class["secondsPlayed"]
    best_specialist_played = round(seconds / 3600, 2)
    # 专家图标
    class_icon = await get_special_icon(best_class, sv)
    # 图像缩放
    class_icon = class_icon.resize((90, 90))
    # 绘制最佳专家
    ch_text_font_bc = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 38)
    ch_text_font_s = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 30)
    new_img = draw_rect(new_img, (768 + 25, 25, 1318, 180), 10, fill=(0, 0, 0, 150))
    draw.text((815, 55), '最 佳', fill='lightgreen', font=ch_text_font_bc)
    draw.text((815, 105), '专 家', fill='lightgreen', font=ch_text_font_bc)
    new_img = image_paste(class_icon, new_img, (930, 35))
    spec_name = classesList[best_specialist]
    draw.text((918, 130), f'{spec_name}', fill='skyblue', font=ch_text_font_s)
    draw.text((1050, 40), f' K/D：{best_specialist_kill_death}', fill='white', font=ch_text_font_s)
    draw.text((1050, 73), f'KPM：{best_specialist_kpm}', fill='white', font=ch_text_font_s)
    draw.text((1050, 105), f'击杀：{best_specialist_kills}', fill='white', font=ch_text_font_s)
    draw.text((1050, 138), f'时长：{best_specialist_played} H', fill='white', font=ch_text_font_s)

    # 9.MVP/最佳小队
    # 绘制最佳小队/MVP
    new_img = draw_rect(new_img, (1318 + 25, 25, 1920 - 195, 180), 10, fill=(0, 0, 0, 150))
    # 游玩场数
    matches = data["matchesPlayed"]
    # mvp
    mvp = "MVP：" + str(data["mvp"])
    # 神射手距离
    total_long_distance = data['dividedKills']['longDistance']
    p_round_long_distance = data['dividedKills']['inRound']['longDistance']
    playerTakeDowns = data['playerTakeDowns']
    # 最佳小队
    best_squad = "最佳小队：" + str(data["bestSquad"])
    best_show = random.choice((mvp, best_squad))
    ch_text_font2 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 36)
    draw.text((1368, 30), f'游玩场数: {matches}', fill='white', font=ch_text_font2)
    draw.text((1368, 80), f'{best_show}', fill='white', font=ch_text_font2)
    ch_text_font_s = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    draw.text((1368, 130), f'处决: {playerTakeDowns}', fill='white', font=ch_text_font_s)
    if match == 0:
        new_img = await draw_weapons(new_img, data, sv)
    elif match == 1:
        new_img = await draw_vehicles(new_img, data, sv)
    elif match == 2:
        new_img = await draw_classes(new_img, data, sv)
    elif match == 3:
        new_img = await draw_gadgets(new_img, data, sv)
    elif match == 4:
        new_img = await draw_maps(new_img, data, sv)
    elif match == 5:
        new_img = await draw_gamemodes(new_img, data, sv)
    player_name = data["userName"]
    # 添加logo
    new_img = paste_ic_logo(new_img)
    sv.logger.info(f"玩家：{player_name}->图片处理完成")
    # 显示图片
    # new_img.show()
    b_io = BytesIO()
    new_img.save(b_io, format="PNG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str


async def bf_2042_gen_property(data, platform, bot, sv, property):
    # 基本信息
    # 玩家名称
    player_name = data["userName"]
    # 最佳专家
    bestClass = data['bestClass']
    # mvp
    mvp = data['mvp']
    # 击杀
    kills = data['kills']
    # 急救
    revives = data["revives"]
    # KD
    killDeath = data['killDeath']
    # 步战KD
    infantryKillDeath = data['infantryKillDeath']
    # KPM
    killPerMin = data['killsPerMinute']
    # 爆头率
    headshots = data['headShots']
    # 精准度
    accuracy = data['accuracy']
    # 游玩时间
    playtime = data['secondsPlayed']
    playtime = str(round(playtime / 3600))
    # 游戏场数
    matchesPlay = data['matchesPlayed']
    # AI击杀数
    kill_AI = data['dividedKills']['ai']
    # 处理击杀玩家的百分比
    kill_human_per = data["humanPrecentage"]
    kill_human_per = float(kill_human_per.strip('%')) / 100
    # 四舍五入计算真实KD
    real_kd = round(kill_human_per * killDeath, 2)
    # 真实kpm
    real_kpm = round(kill_human_per * killPerMin, 2)

    # 添加BF ban 检测结果
    bf_ban_res = await get_bf_ban_check(data["userName"], data["userId"], data["id"])

    # 数据5 简易检测器
    weapon_list = sorted(data["weapons"], key=lambda k: k['kills'], reverse=True)
    hacker_check_res = hacker_check(weapon_list)
    final = "未知"
    color = "white"
    check_res = False

    if 3 in hacker_check_res:
        final = "傻逼玩意"
        color = "#FF9999"
        check_res = True
    elif 2 in hacker_check_res:
        final = "挂？样本太少"
        color = "yellow"
        check_res = True
    elif 1 in hacker_check_res:
        final = "？样本太少"
        color = "yellow"
        check_res = True
    elif 0 in hacker_check_res:
        final = "疑？详查"
        color = "yellow"
        check_res = True
    if not check_res:
        # kpm大于1 总kd大于2 真实kd大于1.5
        if killPerMin > 1.00 and killDeath > 2 and real_kd > 1.5:
            final = "Pro"
            color = "gold"
        else:
            final = "薯薯"
            color = "skyblue"

    # 计算图像所需大小
    gen_data = data[property]
    item_number = len(gen_data) if len(gen_data) < 16 else 16
    item_number += 1
    # 属性行高
    lineHeight = 40
    img_width = 600
    img_height = 200 + (item_number) * lineHeight + 10
    new_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0))
    backImg = Image.open(filepath + '/img/bg/common/bf2042s6.jpg')
    new_img.paste(backImg, (0, 0))

    ch_text_font = ImageFont.truetype(filepath + '/font/msyh.ttc', 20)
    ch_text_font2 = ImageFont.truetype(filepath + '/font/msyh.ttc', int((lineHeight - 10) / 2))

    # 绘制基本信息背景
    new_img = draw_rect(new_img, (10, 10, 590, 190), 2, fill=(50, 50, 50, 150))
    # 绘制属性背景
    new_img = draw_rect(new_img, (10, 200, 590, 200 + item_number * lineHeight), 2, fill=(50, 50, 50, 150))
    # 字体填充
    draw = ImageDraw.Draw(new_img)
    # 提取属性，并排序
    proData = data[property]
    proData = pd.DataFrame(proData)
    proData.sort_values(by=parse_content[property][1], axis=0, inplace=True, ascending=False)
    proData = proData.reset_index(drop=True)
    # 绘制属性图片
    draw.text((82 + 170, 197), parse_str[property], fill='red', font=ch_text_font)
    for index in range(item_number - 1):
        pName = proData.loc[index][parse_content[property][0]]
        pName = pName.replace('/', '-')
        print(pName)
        filename = filepath + '/img/' + property + '/' + pName + '.png'
        if (os.path.exists(filename)):
            pImg = Image.open(filename).resize(parse_size[property][0])
            new_img.paste(pImg,
                          (10 + parse_size[property][1][0], 230 + index * lineHeight + parse_size[property][1][1]))
        draw.text((12, 230 + index * lineHeight - 15), '-' * 96, fill='#2d85a2', font=ch_text_font2)
        for item_index in range(len(parse_content[property])):
            left = 82
            top = 230
            top += index * lineHeight + 15 * int(item_index / 3)
            left += item_index % 3 * 166
            thisPData = proData.loc[index][parse_content[property][item_index]]
            if (parse_content[property][item_index] == 'secondsPlayed'):
                thisPData = str(round(thisPData / 3600))
            draw.text((left, top), parse_str[parse_content[property][item_index]] + str(str(thisPData)), fill='white',
                      font=ch_text_font2)

            # 最佳专家图像
    bestClassImg = Image.open(filepath + '/img/classes/' + bestClass + '.png').resize((94, 112))
    new_img.paste(bestClassImg, (13, 13))
    # 生成个人数据
    # 玩家名称
    draw.text((113, 10), '玩家:' + str(player_name), fill='white', font=ch_text_font)
    # 游玩时间
    draw.text((354, 10), '游玩时间:' + str(playtime) + 'h', fill='white', font=ch_text_font)
    # kd
    draw.text((113, 40), 'KD:' + str(killDeath), fill='white', font=ch_text_font)
    # kpm
    draw.text((221, 40), 'KPM:' + str(killPerMin), fill='white', font=ch_text_font)
    # real kd
    draw.text((354, 40), '·KD:' + str(real_kd), fill='red', font=ch_text_font)
    # real kpm
    draw.text((462, 40), '·KPM:' + str(real_kpm), fill='red', font=ch_text_font)
    # kills
    draw.text((113, 70), '击杀数:' + str(kills), fill='white', font=ch_text_font)
    # revieve
    draw.text((354, 70), '急救数:' + str(revives), fill='white', font=ch_text_font)
    # headshot
    draw.text((113, 100), '爆头率:' + str(headshots), fill='white', font=ch_text_font)
    # accuracy
    draw.text((354, 100), '精准度:' + str(accuracy), fill='white', font=ch_text_font)
    # ai kill
    draw.text((15, 130), 'AI击杀:' + str(kill_AI), fill='white', font=ch_text_font)
    # infantry kd
    draw.text((160, 130), '步战KD:' + str(infantryKillDeath), fill='white', font=ch_text_font)
    # match
    draw.text((305, 130), '总场数:' + str(matchesPlay), fill='white', font=ch_text_font)
    # mvp
    draw.text((450, 130), 'MVP:' + str(mvp), fill='white', font=ch_text_font)
    # hacker?
    draw.text((15, 160), '猜测:' + str(final), fill=color, font=ch_text_font)
    # bf ban
    draw.text((305, 160), 'BFBAN:' + str(bf_ban_res), fill='blue', font=ch_text_font)

    # 生成图像
    new_img.save('./' + property + '.png', format='PNG')
    # 图片处理完成 发送
    sv.logger.info(f"玩家：{player_name}->图片处理完成")
    # 显示图片
    # new_img.show()
    b_io = BytesIO()
    new_img.save(b_io, format="PNG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str


async def draw_vehicles(new_img, data, sv):
    draw = ImageDraw.Draw(new_img)
    # 10.绘制武器框
    new_img = draw_rect(new_img, (25, 205, 1920 - 25, 1080 - 25), 10, fill=(0, 0, 0, 150))

    # 武器击杀数排序
    top_list = sorted(data["vehicles"], key=lambda k: k['kills'], reverse=True)
    # 载入字体
    ch_text_font4 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font4 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 32)
    ch_text_font4_5 = ImageFont.truetype(filepath + '/font/msyh.ttc', 32)

    # 遍历 左
    height = 220
    index = 0
    for i in range(0, 8):
        new_img = image_paste(get_top_object_img(top_list[i], sv).resize((160, 40)), new_img, (50, height + 25))
        if not top_list[i].get("vehicleName"):
            if top_list[i].get("type"):
                vehicle_name = bf_object_dice[top_list[i].get("type")]
            else:
                vehicle_name = top_list[i].get("id")
        else:
            vehicle_name = bf_object_dice.get(top_list[i]["vehicleName"], top_list[i]["vehicleName"])
        draw.text((230, height), f'{vehicle_name}', fill="white", font=ch_text_font4_5)
        draw.text((230, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((450, height), f'摧毁数：{top_list[i]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
        draw.text((450, height + 45), f'碾压击杀：{top_list[i]["roadKills"]}', fill="white", font=ch_text_font4)

        draw.text((730, height), f'KPM：{top_list[i]["killsPerMinute"]}', fill="white", font=ch_text_font4)
        draw.text((730, height + 45), f'时长：{int(int(top_list[i]["timeIn"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        if i != 7:
            # 绘制虚线
            new_img = await draw_point_line(new_img, start_point=(50, height + 90), end_point=(1870, height + 90),
                                            line_color='lightgreen')
        height += 105
        index = i

    # 分割线
    draw.line([950, 225, 950, 1030], fill="white", width=5, joint=None)
    # 遍历 右
    height = 220
    for i in range(index + 1, index + 9):
        new_img = image_paste(get_top_object_img(top_list[i], sv).resize((160, 40)), new_img, (975, height + 25))
        if not top_list[i].get("vehicleName"):
            if top_list[i].get("type"):
                vehicle_name = bf_object_dice[top_list[i].get("type")]
            else:
                vehicle_name = top_list[i].get("id")
        else:
            vehicle_name = bf_object_dice.get(top_list[i]["vehicleName"], top_list[i]["vehicleName"])
        draw.text((1160, height), f'{vehicle_name}', fill="white", font=ch_text_font4_5)
        draw.text((1160, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((1380, height), f'摧毁数：{top_list[i]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
        draw.text((1380, height + 45), f'碾压击杀：{top_list[i]["roadKills"]}', fill="white", font=ch_text_font4)

        draw.text((1660, height), f'KPM：{top_list[i]["killsPerMinute"]}', fill="white", font=ch_text_font4)
        draw.text((1660, height + 45), f'时长：{int(int(top_list[i]["timeIn"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        height += 105
        # 图片处理完成 发送
    return new_img


async def draw_weapons(new_img, data, sv):
    draw = ImageDraw.Draw(new_img)
    # 10.绘制武器框
    new_img = draw_rect(new_img, (25, 205, 1920 - 25, 1080 - 25), 10, fill=(0, 0, 0, 150))

    # 武器击杀数排序
    top_list = sorted(data["weapons"], key=lambda k: k['kills'], reverse=True)
    # 载入字体
    ch_text_font4 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font4 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 32)

    # 遍历 左
    height = 220
    index = 0
    for i in range(0, 8):
        new_img = image_paste(get_top_object_img(top_list[i], sv).resize((160, 80)), new_img, (50, height + 5))
        draw.text((230, height), f'{top_list[i]["weaponName"]}', fill="white", font=en_text_font4)
        draw.text((230, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((450, height), f'爆头率：{top_list[i]["headshots"]}', fill="white", font=ch_text_font4)
        draw.text((450, height + 45), f'命中率：{top_list[i]["accuracy"]}', fill="white", font=ch_text_font4)

        draw.text((730, height), f'KPM：{top_list[i]["killsPerMinute"]}', fill="white", font=ch_text_font4)
        draw.text((730, height + 45), f'时长：{int(int(top_list[i]["timeEquipped"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        if i != 7:
            # 绘制虚线
            new_img = await draw_point_line(new_img, start_point=(50, height + 90), end_point=(1870, height + 90),
                                            line_color='lightgreen')
        height += 105
        index = i

    # 分割线
    draw.line([950, 225, 950, 1030], fill="white", width=5, joint=None)
    # 遍历 右
    height = 220
    for i in range(index + 1, index + 9):
        new_img = image_paste(get_top_object_img(top_list[i], sv).resize((160, 80)), new_img, (975, height + 5))
        draw.text((1160, height), f'{top_list[i]["weaponName"]}', fill="white", font=en_text_font4)
        draw.text((1160, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((1380, height), f'爆头率：{top_list[i]["headshots"]}', fill="white", font=ch_text_font4)
        draw.text((1380, height + 45), f'命中率：{top_list[i]["accuracy"]}', fill="white", font=ch_text_font4)

        draw.text((1660, height), f'KPM：{top_list[i]["killsPerMinute"]}', fill="white", font=ch_text_font4)
        draw.text((1660, height + 45), f'时长：{int(int(top_list[i]["timeEquipped"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        height += 105
        # 图片处理完成 发送
    return new_img


async def draw_classes(new_img, data, sv):
    draw = ImageDraw.Draw(new_img)
    # 10.绘制框
    new_img = draw_rect(new_img, (25, 205, 1920 - 25, 1080 - 25), 10, fill=(0, 0, 0, 150))

    # 击杀数排序
    top_list = sorted(data["classes"], key=lambda k: k['kills'], reverse=True)
    # 载入字体
    ch_text_font4 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font4 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 32)
    ch_text_font4_5 = ImageFont.truetype(filepath + '/font/msyh.ttc', 32)

    # 遍历 左
    height = 220
    index = 0
    for i in range(0, 8):
        special_icon = await get_special_icon(top_list[i], sv)
        new_img = image_paste(special_icon.resize((70, 70)), new_img, (100, height + 5))
        character_name = classesList[top_list[i]["characterName"]]
        draw.text((230, height), f'{character_name}', fill="white", font=ch_text_font4_5)
        draw.text((230, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((450, height), f'KPM：{top_list[i]["kpm"]}', fill="white", font=ch_text_font4)
        draw.text((450, height + 45), f'K/D：{top_list[i]["killDeath"]}', fill="white", font=ch_text_font4)

        draw.text((730, height), f'死亡数：{top_list[i]["deaths"]}', fill="white", font=ch_text_font4)
        draw.text((730, height + 45), f'时长：{int(int(top_list[i]["secondsPlayed"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        if i != 7:
            # 绘制虚线
            new_img = await draw_point_line(new_img, start_point=(50, height + 90), end_point=(1870, height + 90),
                                            line_color='lightgreen')
        height += 105
        index = i

    # 分割线
    draw.line([950, 225, 950, 1030], fill="white", width=5, joint=None)
    # 遍历 右
    height = 220
    for i in range(index + 1, index + 9):
        special_icon = await get_special_icon(top_list[i], sv)
        new_img = image_paste(special_icon.resize((70, 70)), new_img, (975 + 50, height + 5))
        character_name = classesList[top_list[i]["characterName"]]
        draw.text((1160, height), f'{character_name}', fill="white", font=ch_text_font4_5)
        draw.text((1160, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((1380, height), f'KPM：{top_list[i]["kpm"]}', fill="white", font=ch_text_font4)
        draw.text((1380, height + 45), f'K/D：{top_list[i]["killDeath"]}', fill="white", font=ch_text_font4)

        draw.text((1660, height), f'死亡数：{top_list[i]["deaths"]}', fill="white", font=ch_text_font4)
        draw.text((1660, height + 45), f'时长：{int(int(top_list[i]["secondsPlayed"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        height += 105
        # 图片处理完成 发送
    return new_img


async def draw_gamemodes(new_img, data, sv):
    draw = ImageDraw.Draw(new_img)
    # 10.绘制框
    new_img = draw_rect(new_img, (25, 205, 1920 - 25, 1080 - 25), 10, fill=(0, 0, 0, 150))

    # 击杀数排序
    top_list = sorted(data["gamemodes"], key=lambda k: k['kills'], reverse=True)
    # 载入字体
    ch_text_font4 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font4 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 32)
    ch_text_font4_5 = ImageFont.truetype(filepath + '/font/msyh.ttc', 32)
    np_logo = Image.open(filepath + "/img/specialist_icon/No-Pats.png").convert('RGBA')
    # 遍历 左
    height = 265
    index = 0
    for i in range(0, 4):
        new_img = image_paste(np_logo.resize((70, 70)), new_img, (100, height + 5))
        gamemode_name = game_mode[top_list[i]["gamemodeName"]]
        draw.text((230, height), f'{gamemode_name}', fill="white", font=ch_text_font4_5)
        draw.text((230, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((450, height), f'KPM：{top_list[i]["kpm"]}', fill="white", font=ch_text_font4)
        draw.text((450, height + 45), f'场次：{top_list[i]["matches"]}', fill="white", font=ch_text_font4)

        draw.text((730, height), f'胜率：{top_list[i]["winPercent"]}', fill="white", font=ch_text_font4)
        draw.text((730, height + 45), f'时长：{int(int(top_list[i]["secondsPlayed"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        if i != 3:
            # 绘制虚线
            new_img = await draw_point_line(new_img, start_point=(50, height + 145), end_point=(1870, height + 90),
                                            line_color='lightgreen')
        height += 200
        index = i

    # 分割线
    draw.line([950, 225, 950, 1030], fill="white", width=5, joint=None)
    # 遍历 右
    height = 265
    for i in range(index + 1, index + 5):
        new_img = image_paste(np_logo.resize((70, 70)), new_img, (975 + 50, height + 5))
        gamemode_name = game_mode[top_list[i]["gamemodeName"]]
        draw.text((1160, height), f'{gamemode_name}', fill="white", font=ch_text_font4_5)
        draw.text((1160, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((1380, height), f'KPM：{top_list[i]["kpm"]}', fill="white", font=ch_text_font4)
        draw.text((1380, height + 45), f'场次：{top_list[i]["matches"]}', fill="white", font=ch_text_font4)

        draw.text((1660, height), f'胜率：{top_list[i]["winPercent"]}', fill="white", font=ch_text_font4)
        draw.text((1660, height + 45), f'时长：{int(int(top_list[i]["secondsPlayed"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        height += 200
        # 图片处理完成 发送
    return new_img


async def draw_maps(new_img, data, sv):
    draw = ImageDraw.Draw(new_img)
    # 10.绘制武器框
    new_img = draw_rect(new_img, (25, 205, 1920 - 25, 1080 - 25), 10, fill=(0, 0, 0, 150))

    # 武器击杀数排序
    top_list = sorted(data["maps"], key=lambda k: k['wins'], reverse=True)
    # 载入字体
    ch_text_font4 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font4 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 32)
    ch_text_font4_5 = ImageFont.truetype(filepath + '/font/msyh.ttc', 32)

    # 遍历 左
    height = 220
    index = 0
    for i in range(0, 8):
        new_img = image_paste(get_top_object_img(top_list[i], sv).resize((150, 60)), new_img, (50, height + 15))
        map_name = map_list[top_list[i]["mapName"]]
        draw.text((230, height), f'{map_name}', fill="white", font=ch_text_font4_5)
        draw.text((230, height + 45), f'获胜：{top_list[i]["wins"]}', fill="white", font=ch_text_font4)

        draw.text((450, height), f'场次：{top_list[i]["matches"]}', fill="white", font=ch_text_font4)
        draw.text((450, height + 45), f'胜率：{top_list[i]["winPercent"]}', fill="white", font=ch_text_font4)

        draw.text((730, height), f'失败：{top_list[i]["losses"]}', fill="white", font=ch_text_font4)
        draw.text((730, height + 45), f'时长：{int(int(top_list[i]["secondsPlayed"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        if i != 7:
            # 绘制虚线
            new_img = await draw_point_line(new_img, start_point=(50, height + 90), end_point=(1870, height + 90),
                                            line_color='lightgreen')
        height += 105
        index = i

    # 分割线
    draw.line([950, 225, 950, 1030], fill="white", width=5, joint=None)
    # 遍历 右
    height = 220
    for i in range(index + 1, index + 9):
        new_img = image_paste(get_top_object_img(top_list[i], sv).resize((150, 60)), new_img, (975, height + 15))
        map_name = map_list[top_list[i]["mapName"]]
        draw.text((1160, height), f'{map_name}', fill="white", font=ch_text_font4_5)
        draw.text((1160, height + 45), f'获胜：{top_list[i]["wins"]}', fill="white", font=ch_text_font4)

        draw.text((1380, height), f'场次：{top_list[i]["matches"]}', fill="white", font=ch_text_font4)
        draw.text((1380, height + 45), f'胜率：{top_list[i]["winPercent"]}', fill="white", font=ch_text_font4)

        draw.text((1660, height), f'失败：{top_list[i]["losses"]}', fill="white", font=ch_text_font4)
        draw.text((1660, height + 45), f'时长：{int(int(top_list[i]["secondsPlayed"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        height += 105
        # 图片处理完成 发送
    return new_img


async def draw_gadgets(new_img, data, sv):
    draw = ImageDraw.Draw(new_img)
    # 10.绘制框
    new_img = draw_rect(new_img, (25, 205, 1920 - 25, 1080 - 25), 10, fill=(0, 0, 0, 150))

    # 击杀数排序
    top_list = sorted(data["gadgets"], key=lambda k: k['kills'], reverse=True)
    # 载入字体
    ch_text_font4 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font4 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 32)
    ch_text_font4_5 = ImageFont.truetype(filepath + '/font/msyh.ttc', 32)

    # 遍历 左
    height = 220
    index = 0
    for i in range(0, 8):
        icon = get_top_object_img(top_list[i], sv)
        new_img = image_paste(icon.resize((70, 70)), new_img, (100, height + 5))
        gadget_name = bf_object_dice[top_list[i]["gadgetName"]]
        draw.text((220, height), f'{gadget_name}', fill="white", font=ch_text_font4_5)
        draw.text((220, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((450, height), f'KPM：{top_list[i]["kpm"]}', fill="white", font=ch_text_font4)
        draw.text((450, height + 45), f'摧毁载具：{top_list[i]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)

        draw.text((730, height), f'多重击杀：{top_list[i]["multiKills"]}', fill="white", font=ch_text_font4)
        draw.text((730, height + 45), f'时长：{int(int(top_list[i]["secondsPlayed"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        if i != 7:
            # 绘制虚线
            new_img = await draw_point_line(new_img, start_point=(50, height + 90), end_point=(1870, height + 90),
                                            line_color='lightgreen')
        height += 105
        index = i

    # 分割线
    draw.line([950, 225, 950, 1030], fill="white", width=5, joint=None)
    # 遍历 右
    height = 220
    for i in range(index + 1, index + 9):
        icon = get_top_object_img(top_list[i], sv)
        new_img = image_paste(icon.resize((70, 70)), new_img, (975 + 50, height + 5))
        character_name = bf_object_dice[top_list[i]["gadgetName"]]
        draw.text((1150, height), f'{character_name}', fill="white", font=ch_text_font4_5)
        draw.text((1150, height + 45), f'击杀：{top_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((1380, height), f'KPM：{top_list[i]["kpm"]}', fill="white", font=ch_text_font4)
        draw.text((1380, height + 45), f'摧毁载具：{top_list[i]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)

        draw.text((1660, height), f'多重击杀：{top_list[i]["multiKills"]}', fill="white", font=ch_text_font4)
        draw.text((1660, height + 45), f'时长：{int(int(top_list[i]["secondsPlayed"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        height += 105
        # 图片处理完成 发送
    return new_img
