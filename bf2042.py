import base64
import hashlib
import os
import random
import time
from decimal import Decimal
from io import BytesIO
import json
import aiohttp
import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont
from hoshino.modules.bf2042.user_manager import check_user_support, check_user_support2

classesList = {
    "Mackay": "麦凯",
    "Angel": "天使",
    "Falck": "法尔克",
    "Paik": "白智秀",
    "Sundance": "日舞",
    "Dozer": "推土机",
    "Rao": "拉奥",
    "Lis": "莉丝",
    "Irish": "爱尔兰佬",
    "Crawford": "克劳福德",
    "Boris": "鲍里斯",
    "Zain": "扎因",
    "Casper": "卡斯帕",
    "Blasco": "布拉斯科",
}
classes_type_list = {
    "Assault": "突击兵",
    "Support": "支援兵",
    "Recon": "侦察兵",
    "Engineer": "工程兵"
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

'''2042图片战绩生成'''
filepath = os.path.dirname(__file__).replace("\\", "/")
bf_ban_url = "https://api.gametools.network/bfban/checkban"


async def bf_2042_gen_pic(data, platform, bot, ev):
    # 检查玩家是否存在
    if "userName" not in data:
        mes = "未找到该玩家"
        return mes
    # 1.创建黑色板块 1920*1080
    new_img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 1000))
    # 2.获取头像图片 150*150
    platform_id = 1
    nucleus_id = data['userId']
    persona_id = data['id']
    # 调用接口获取正确的头像
    avatar_url = await get_avatar(platform_id, persona_id, nucleus_id)
    print("头像URL处理：" + avatar_url)
    avatar = Image.open(filepath + "/img/class_icon/No-Pats.png").convert('RGBA')
    try:
        if not avatar_url == "":
            res = BytesIO(requests.get(avatar_url).content)
            avatar = Image.open(res)
    except Exception as e:
        print(e)
    avatar = png_resize(avatar, new_width=145, new_height=145)
    avatar = circle_corner(avatar, 10)
    # 3.获取背景 并 模糊
    # 判断是否为support
    if await check_user_support(ev.user_id):
        img = get_favorite_image(ev.user_id)
    else:
        bg_name = os.listdir(filepath + "/img/bg/common/")
        index = random.randint(0, len(bg_name) - 1)
        img = Image.open(filepath + f"/img/bg/common/{bg_name[index]}").convert('RGBA').resize((1920, 1080))
    # img_filter = img.filter(ImageFilter.GaussianBlur(radius=3))
    # 4.拼合板块+背景+logo
    new_img.paste(img, (0, 0))
    if await check_user_support2(ev.user_id, data["userName"]):
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
    class_type = best_class["className"]
    # 专家图标
    class_icon_path = get_class_type(class_type)
    class_icon = Image.open(class_icon_path).convert('RGBA')
    # 图像缩放
    class_icon = class_icon.resize((90, 90))
    # class_icon = png_resize(class_icon, new_width=90, new_height=90)
    # (300, 360)
    # 绘制最佳专家
    new_img = draw_rect(new_img, (768 + 25, 25, 1318, 180), 10, fill=(0, 0, 0, 150))
    draw.text((815, 55), '最 佳\n专 家', fill='lightgreen', font=ch_text_font)
    # draw.rectangle([930, 35, 1020, 125], fill="black")
    # new_img.paste(class_icon, (930, 35))
    new_img = image_paste(class_icon, new_img, (930, 35))
    draw.text((920, 130), f'{classes_type_list[class_type]}', fill='skyblue', font=ch_text_font)
    draw.text((1050, 40), f'{classesList[best_specialist]}', fill='white', font=ch_text_font)
    draw.text((1050, 115), f'击杀数：{best_specialist_kills}', fill='white', font=ch_text_font)

    # 9.MVP/最佳小队
    # 绘制最佳小队/MVP
    new_img = draw_rect(new_img, (1318 + 25, 25, 1920 - 195, 180), 10, fill=(0, 0, 0, 150))
    # 游玩场数
    matches = data["matchesPlayed"]
    # mvp
    mvp = "MVP：" + str(data["mvp"])
    # 最佳小队
    best_squad = "最佳小队：" + str(data["bestSquad"])
    best_show = random.choice((mvp, best_squad))
    ch_text_font2 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 36)
    draw.text((1368, 50), f'游玩场数: {matches}', fill='white', font=ch_text_font2)
    draw.text((1368, 111), f'{best_show}', fill='white', font=ch_text_font2)
    # 10.绘制生涯框
    new_img = draw_rect(new_img, (25, 205, 1920 - 25, 455), 10, fill=(0, 0, 0, 150))
    ch_text_font3 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font3 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 36)
    kd = data["killDeath"]
    real_kd = data["infantryKillDeath"]
    kills = data["kills"]
    kpm = data["killsPerMinute"]
    k_per_match = data["killsPerMatch"]
    hs = data["headshots"]
    acc = data["accuracy"]
    win = data["winPercent"]
    human_per = data["humanPrecentage"]
    AI_kill = kills - int(kills * float(human_per.replace("%", "")) / 100 + 0.55)
    deaths = data["deaths"]
    revives = data["revives"]
    eme = data["enemiesSpotted"]
    # 数据1
    draw.text((150, 235), f'K/D： {kd}', fill='white', font=ch_text_font3)
    draw.text((150, 280), f'真实 K/D： {real_kd}', fill='white', font=ch_text_font3)
    draw.text((150, 325), f'击杀： {kills}', fill='white', font=ch_text_font3)
    draw.text((150, 370), f'死亡数： {deaths}', fill='white', font=ch_text_font3)

    # 数据2
    draw.text((550, 235), f'KPM： {kpm}', fill='white', font=ch_text_font3)
    draw.text((550, 280), f'爆头率： {hs}', fill='white', font=ch_text_font3)
    draw.text((550, 325), f'命中率： {acc}', fill='white', font=ch_text_font3)
    draw.text((550, 370), f'胜率： {win}', fill='white', font=ch_text_font3)

    # 数据3
    draw.text((950, 235), f'AI击杀： {AI_kill}', fill='white', font=ch_text_font3)
    draw.text((950, 280), f'场均击杀： {k_per_match}', fill='white', font=ch_text_font3)
    draw.text((950, 325), f'急救数： {revives}', fill='white', font=ch_text_font3)
    draw.text((950, 370), f'发现敌人数： {eme}', fill='white', font=ch_text_font3)

    # 数据4 BF TRACKER个人主页
    en_text_font_ext = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 24)
    qr_img = qr_code_gen(player_name, platform)
    qr_img = qr_img.resize((145, 145))
    draw.text((1300, 228), "BATTLEFIELD\n    TRACKER", fill="lightgreen", font=en_text_font_ext)
    new_img.paste(qr_img, (1300, 290))

    weapon_list = sorted(data["weapons"], key=lambda k: k['kills'], reverse=True)

    # 数据5 简易检测器
    hacker_check_res = hacker_check(weapon_list)
    final = "未知"
    color = "white"
    check_res = False

    if 3 in hacker_check_res:
        final = "挂钩"
        color = "red"
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
            final = "Pro哥"
            color = "gold"
        else:
            final = "薯薯\n别拷打我了哥"
            color = "skyblue"

    ch_text_font_ext = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    ch_text_font_ext2 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 28)
    draw.text((1485, 228), f'鉴定结果（仅供参考）：', fill="white", font=ch_text_font_ext)
    draw.text((1485, 238), f'\n{final}', fill=f"{color}", font=ch_text_font_ext2)

    # 添加BF ban 检测结果
    bf_ban_res = await bf_ban_check(data["userName"], data["userId"], data["id"])
    draw.text((1485, 350), f'联BAN查询：', fill="white", font=ch_text_font_ext)
    draw.text((1485, 360), f'\n{bf_ban_res}', fill="white", font=ch_text_font_ext2)

    # 11.绘制第三部分 TOP4武器/载具 947.5-12.5
    new_img = draw_rect(new_img, (25, 480, 1920 - 25, 1080 - 25), 10, fill=(0, 0, 0, 150))
    ch_text_font4 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font4 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 32)

    top_weapon_list = sorted(data["weapons"], key=lambda k: k['kills'], reverse=True)

    # 1
    # 修饰线条
    draw.line([45, 505, 45, 585], fill="#CCFF00", width=5, joint=None)
    # draw.rectangle([50, 505, 210, 585], fill="black")
    new_img = image_paste(get_top_object_img(top_weapon_list[0]).resize((160, 80)), new_img, (50, 505))
    draw.text((230, 500), f'{top_weapon_list[0]["weaponName"]}', fill="white", font=en_text_font4)
    draw.text((230, 545), f'击杀：{top_weapon_list[0]["kills"]}', fill="white", font=ch_text_font4)

    draw.text((450, 500), f'爆头率：{top_weapon_list[0]["headshots"]}', fill="white", font=ch_text_font4)
    draw.text((450, 545), f'命中率：{top_weapon_list[0]["accuracy"]}', fill="white", font=ch_text_font4)

    draw.text((730, 500), f'KPM：{top_weapon_list[0]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((730, 545), f'时长：{int(int(top_weapon_list[0]["timeEquipped"]) / 3600 + 0.55)} H', fill="white",
              font=ch_text_font4)
    # 2
    # 修饰线条
    draw.line([45, 615, 45, 695], fill="#CCFF00", width=5, joint=None)
    # draw.rectangle([50, 615, 210, 695], fill="black")
    new_img = image_paste(get_top_object_img(top_weapon_list[1]).resize((160, 80)), new_img, (50, 615))
    draw.text((230, 610), f'{top_weapon_list[1]["weaponName"]}', fill="white", font=en_text_font4)
    draw.text((230, 655), f'击杀：{top_weapon_list[1]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((450, 610), f'爆头率：{top_weapon_list[1]["headshots"]}', fill="white", font=ch_text_font4)
    draw.text((450, 655), f'命中率：{top_weapon_list[1]["accuracy"]}', fill="white", font=ch_text_font4)
    draw.text((730, 610), f'KPM：{top_weapon_list[1]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((730, 655), f'时长：{int(int(top_weapon_list[1]["timeEquipped"]) / 3600 + 0.55)} H', fill="white",
              font=ch_text_font4)
    # 3
    # 修饰线条
    draw.line([45, 725, 45, 805], fill="#CCFF00", width=5, joint=None)
    # draw.rectangle([50, 725, 210, 805], fill="black")
    new_img = image_paste(get_top_object_img(top_weapon_list[2]).resize((160, 80)), new_img, (50, 725))
    draw.text((230, 720), f'{top_weapon_list[2]["weaponName"]}', fill="white", font=en_text_font4)
    draw.text((230, 765), f'击杀：{top_weapon_list[2]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((450, 720), f'爆头率：{top_weapon_list[2]["headshots"]}', fill="white", font=ch_text_font4)
    draw.text((450, 765), f'命中率：{top_weapon_list[2]["accuracy"]}', fill="white", font=ch_text_font4)
    draw.text((730, 720), f'KPM：{top_weapon_list[2]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((730, 765), f'时长：{int(int(top_weapon_list[2]["timeEquipped"]) / 3600 + 0.55)} H', fill="white",
              font=ch_text_font4)
    # 4
    # 修饰线条
    draw.line([45, 845, 45, 925], fill="#66CCFF", width=5, joint=None)
    # draw.rectangle([50, 845, 210, 925], fill="black")
    new_img = image_paste(get_top_object_img(top_weapon_list[3]).resize((160, 80)), new_img, (50, 845))
    draw.text((230, 840), f'{top_weapon_list[3]["weaponName"]}', fill="white", font=en_text_font4)
    draw.text((230, 885), f'击杀：{top_weapon_list[3]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((450, 840), f'爆头率：{top_weapon_list[3]["headshots"]}', fill="white", font=ch_text_font4)
    draw.text((450, 885), f'命中率：{top_weapon_list[3]["accuracy"]}', fill="white", font=ch_text_font4)
    draw.text((730, 840), f'KPM：{top_weapon_list[3]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((730, 885), f'时长：{int(int(top_weapon_list[3]["timeEquipped"]) / 3600 + 0.55)} H', fill="white",
              font=ch_text_font4)
    # 5
    # 修饰线条
    draw.line([45, 955, 45, 1035], fill="#66CCFF", width=5, joint=None)
    # draw.rectangle([50, 955, 210, 1035], fill="black")
    new_img = image_paste(get_top_object_img(top_weapon_list[4]).resize((160, 80)), new_img, (50, 955))
    draw.text((230, 950), f'{top_weapon_list[4]["weaponName"]}', fill="white", font=en_text_font4)
    draw.text((230, 995), f'击杀：{top_weapon_list[4]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((450, 950), f'爆头率：{top_weapon_list[4]["headshots"]}', fill="white", font=ch_text_font4)
    draw.text((450, 995), f'命中率：{top_weapon_list[4]["accuracy"]}', fill="white", font=ch_text_font4)
    draw.text((730, 950), f'KPM：{top_weapon_list[4]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((730, 995), f'时长：{int(int(top_weapon_list[4]["timeEquipped"]) / 3600 + 0.55)} H', fill="white",
              font=ch_text_font4)

    # 分割线
    draw.line([950, 505, 950, 1030], fill="white", width=5, joint=None)
    # 载具部分
    top_vehicles_list = sorted(data["vehicles"], key=lambda k: k['kills'], reverse=True)
    # 1
    # 绘制修饰线条
    draw.line([975, 505, 975, 585], fill="#CCFF00", width=5, joint=None)
    # draw.rectangle([980, 505, 1295, 585], fill="black")
    new_img = image_paste(get_top_object_img(top_vehicles_list[0]).resize((320, 80)), new_img, (980, 505))
    draw.text((1325, 500), f'{top_vehicles_list[0]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 545), f'击杀：{top_vehicles_list[0]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 500), f'KPM：{top_vehicles_list[0]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 545), f'摧毁数：{top_vehicles_list[0]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
    # draw.text((1630, 545), f'时长：{top1weapon_vehicles_time_in}h', fill="white", font=ch_text_font4)
    # 2
    # 绘制修饰线条
    draw.line([975, 615, 975, 695], fill="#CCFF00", width=5, joint=None)
    # draw.rectangle([980, 615, 1295, 695], fill="black")
    new_img = image_paste(get_top_object_img(top_vehicles_list[1]).resize((320, 80)), new_img, (980, 615))
    draw.text((1325, 610), f'{top_vehicles_list[1]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 655), f'击杀：{top_vehicles_list[1]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 610), f'KPM：{top_vehicles_list[1]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 655), f'摧毁数：{top_vehicles_list[1]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
    # 3
    # 绘制修饰线条
    draw.line([975, 725, 975, 805], fill="#CCFF00", width=5, joint=None)
    # draw.rectangle([980, 725, 1295, 805], fill="black")
    new_img = image_paste(get_top_object_img(top_vehicles_list[2]).resize((320, 80)), new_img, (980, 725))
    draw.text((1325, 720), f'{top_vehicles_list[2]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 765), f'击杀：{top_vehicles_list[2]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 720), f'KPM：{top_vehicles_list[2]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 765), f'摧毁数：{top_vehicles_list[2]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
    # 4
    # 绘制修饰线条
    draw.line([975, 845, 975, 925], fill="#66CCFF", width=5, joint=None)
    # draw.rectangle([980, 845, 1295, 925], fill="black")
    new_img = image_paste(get_top_object_img(top_vehicles_list[3]).resize((320, 80)), new_img, (980, 845))
    draw.text((1325, 840), f'{top_vehicles_list[3]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 885), f'击杀：{top_vehicles_list[3]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 840), f'KPM：{top_vehicles_list[3]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 885), f'摧毁数：{top_vehicles_list[3]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
    # 5
    # 绘制修饰线条
    draw.line([975, 955, 975, 1035], fill="#66CCFF", width=5, joint=None)
    # draw.rectangle([980, 955, 1295, 1035], fill="black")
    new_img = image_paste(get_top_object_img(top_vehicles_list[4]).resize((320, 80)), new_img, (980, 955))
    draw.text((1325, 950), f'{top_vehicles_list[4]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 995), f'击杀：{top_vehicles_list[4]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 950), f'KPM：{top_vehicles_list[4]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 995), f'摧毁数：{top_vehicles_list[4]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)

    # 添加开发团队logo
    new_img = paste_ic_logo(new_img)

    # 显示图片
    # new_img.show()
    b_io = BytesIO()
    new_img.save(b_io, format="PNG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str


# 圆角遮罩处理
def draw_rect(img, pos, radius, **kwargs):
    transp = Image.new('RGBA', img.size, (0, 0, 0, 0))
    alpha_draw = ImageDraw.Draw(transp, "RGBA")
    alpha_draw.rounded_rectangle(pos, radius, **kwargs)
    img.paste(Image.alpha_composite(img, transp))
    return img


def circle_corner(img, radii):
    """
    半透明圆角处理
    :param img: 要修改的文件
    :param radii: 圆角弧度
    :return: 返回修改过的文件
    """
    circle = Image.new('L', (radii * 2, radii * 2), 0)  # 创建黑色方形
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)  # 黑色方形内切白色圆形

    img = img.convert("RGBA")
    w, h = img.size

    # 创建一个alpha层，存放四个圆角，使用透明度切除圆角外的图片
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)),
                (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)),
                (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)),
                (0, h - radii))  # 左下角
    img.putalpha(alpha)  # 白色区域透明可见，黑色区域不可见

    # 添加圆角边框
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle(img.getbbox(), outline="white", width=3, radius=radii)
    return img


def get_class_type(class_type):
    """
    获取专家类型
    :param class_type: 专家类型
    :return: 返回对应的图标路径
    """
    icon_path = filepath + "/img/class_icon/No-Pats.png"
    if class_type == 'Assault':
        icon_path = filepath + "/img/class_icon/ui/Assault_Icon_small.png"
    elif class_type == 'Support':
        icon_path = filepath + "/img/class_icon/ui/Support_Icon_small.png"
    elif class_type == 'Recon':
        icon_path = filepath + "/img/class_icon/ui/Recon_Icon_small.png"
    elif class_type == 'Engineer':
        icon_path = filepath + "/img/class_icon/ui/Engineer_Icon_small.png"
    return icon_path


def png_resize(source_file, new_width=0, new_height=0, resample="ANTIALIAS", ref_file=''):
    """
    PNG缩放透明度处理
    :param source_file: 源文件（Image.open()）
    :param new_width: 设置的宽度
    :param new_height: 设置的高度
    :param resample:抗锯齿
    :param ref_file:参考文件
    :return:
    """
    img = source_file
    img = img.convert("RGBA")
    width, height = img.size

    if ref_file != '':
        imgRef = Image.open(ref_file)
        new_width, new_height = imgRef.size
    else:
        if new_height == 0:
            new_height = new_width * width / height

    # img.load()
    bands = img.split()
    if resample == "NEAREST":
        resample = Image.NEAREST
    else:
        if resample == "BILINEAR":
            resample = Image.BILINEAR
        else:
            if resample == "BICUBIC":
                resample = Image.BICUBIC
            else:
                if resample == "ANTIALIAS":
                    resample = Image.ANTIALIAS
    bands = [b.resize((new_width, new_height), resample) for b in bands]
    ResizedFile = Image.merge('RGBA', bands)
    # return
    return ResizedFile


# 获取图片
def get_top_object_img(object_data):
    """
    获取对应物品图标
    :param object_data: 物品数据
    :return: 图标
    """
    img_url = object_data["image"]
    print("物品URL处理：" + img_url)
    img = Image.open(filepath + "/img/object_icon/default.png").convert('RGBA')
    # object_name = "default"
    path = filepath + "/img/object_icon/"
    try:
        obj_name = os.listdir(path)
        if "weaponName" in object_data:
            object_name = object_data["weaponName"]
            if object_name in str(obj_name):
                img = Image.open(f"{path}{object_name}.png").convert('RGBA')
            else:
                img = Image.open(BytesIO(requests.get(img_url).content)).convert('RGBA')
                img.save(filepath + f"/img/object_icon/{object_name}.png")
        elif "vehicleName" in object_data:
            object_name = object_data["vehicleName"]
            if object_name in str(obj_name):
                img = Image.open(f"{path}{object_name}.png").convert('RGBA')
            else:
                img = Image.open(BytesIO(requests.get(img_url).content)).convert('RGBA')
                img.save(filepath + f"/img/object_icon/{object_name}.png")
    except Exception as err:
        print(err)
    return img


def qr_code_gen(player, platform):
    """
    version ：QR code 的版次，可以设置 1 ～ 40 的版次。
    error_correction ：容错率，可选 7%、15%、25%、30%，参数如下 ：
    qrcode.constants.ERROR_CORRECT_L ：7%
    qrcode.constants.ERROR_CORRECT_M ：15%（预设）
    qrcode.constants.ERROR_CORRECT_Q ：25%
    qrcode.constants.ERROR_CORRECT_H ：30%
    box_size ：每个模块的像素个数。
    border ：边框区的厚度，预设是 4。
    image_factory ：图片格式，默认是 PIL。
    mask_pattern ：mask_pattern 参数是 0 ～ 7，如果省略会自行使用最适当的方法。
    """
    if "pc" == platform:
        platform = "origin"
    bf_tracker_link = f"https://battlefieldtracker.com/bf2042/profile/{platform}/{player}/overview"
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=5,
                       border=2)
    qr.add_data(bf_tracker_link)
    img = qr.make_image(fill_color='white', back_color="black")
    return img


def image_paste(paste_image, under_image, pos):
    """

    :param paste_image: 需要粘贴的图片
    :param under_image: 底图
    :param pos: 位置（x,y）坐标
    :return: 返回图片
    """
    # 获取需要贴入图片的透明通道
    r, g, b, alpha = paste_image.split()
    # 粘贴时将alpha值传递至mask属性
    under_image.paste(paste_image, pos, alpha)
    return under_image


# 获取专属图库
def get_favorite_image(uid):
    bg_path = filepath + f"/img/bg/user/{uid}/"
    if os.listdir(bg_path):
        bg_name = os.listdir(bg_path)
        index = random.randint(0, len(bg_name) - 1)
        img = Image.open(bg_path + f"{bg_name[index]}").convert('RGBA').resize((1920, 1080))
    else:
        common_bg_name = os.listdir(filepath + "/img/bg/common/")
        index = random.randint(0, len(common_bg_name) - 1)
        img = Image.open(filepath + f"/img/bg/common/{common_bg_name[index]}").convert('RGBA').resize((1920, 1080))
    return img


# 获取bot管理员专属图库
def get_user_avatar(user):
    avatar = download_avatar(user)
    avatar = Image.open(BytesIO(avatar)).convert('RGBA').resize((1920, 1080))
    return avatar


def download_avatar(user_id: str) -> bytes:
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = download_url(url)
    if not data or hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
        data = download_url(url)
    return data


def download_url(url: str) -> bytes:
    for i in range(3):
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                continue
            return resp.content
        except Exception as e:
            print(f"Error downloading {url}, retry {i}/3: {str(e)}")


async def user_img_save(pic_data: bytes, uid: int):
    bg_path = filepath + f"/img/bg/user/{uid}/"
    try:
        # 裁剪图片
        pic_data = cut_image(pic_data, 16 / 9)
        # 保存图片
        time_now = int(time.time())
        pic_data = pic_data.convert('RGB')
        pic_data = pic_data.resize((1920, 1080))
        pic_data.save(bg_path + str(time_now) + ".jpeg", quality=95)
    except Exception as e:
        raise Exception("图片保存失败")


# 图片裁剪
def cut_image(pic_data: bytes, target_ratio: float):
    try:
        pic_data = Image.open(BytesIO(pic_data))
        w, h = pic_data.size
        pic_ratio = w / h
        if pic_ratio > target_ratio:
            # 宽高比大于目标比例，按高度缩放。保持宽度不变
            new_h = w / target_ratio
            h_delta = (h - new_h) / 2
            w_delta = 0
        else:
            # 宽高比小于目标比例，按宽度缩放。保持高度不变
            new_w = h * target_ratio
            w_delta = (w - new_w) / 2
            h_delta = 0
        cropped = pic_data.crop((w_delta, h_delta, w - w_delta, h - h_delta))
        return cropped
    except Exception as e:
        raise Exception("图片剪裁失败")


def hacker_check(weapon_data):
    """
    简易外挂数据检测
    :param weapon_data: 武器数据
    :return: 返回检测的数据标记，
    击杀数大于300切爆头率大于30小于40标记1，
    击杀数大于100切爆头率大于40标记2（基本实锤）
    """
    ignore_type = ["DMR", "Bolt Action", "Railguns", "Lever-Action Carbines", "Sidearm"]
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


async def bf_ban_check(user_name, userids, personaids):
    url = f"https://api.gametools.network/bfban/checkban/?names={user_name}&userids={userids}&personaids={personaids}"
    headers = {'accept': 'application/json'}
    trans = "未查询到相关封禁信息"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
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


def paste_ic_logo(img):
    # 载入logo
    ic_logo = filepath + "/img/dev_logo/IC.png"
    # 载入字体
    en_text_font = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 18)
    logo_file = Image.open(ic_logo).convert("RGBA").resize((20, 20))
    draw = ImageDraw.Draw(img)
    img = draw_rect(img, (645, 1058, 1220, 1078), 1, fill=(0, 0, 0, 150))
    draw.text((700, 1055), "BF2042 Player‘s Status Plugin Designed By", fill="white", font=en_text_font)
    img = image_paste(logo_file, img, (1040, 1058))
    draw.text((1065, 1055), "SANSENHOSHI", fill="white", font=en_text_font)
    return img


# 获取ea头像（由于数据接口返回头像问题，改为详细获取头像和用户名）
async def get_avatar(platform_id, persona_id, nucleus_id):
    url = f"https://api.gametools.network/bf2042/feslid/?platformid={platform_id}&personaid={persona_id}&nucleusid={nucleus_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'accept': 'application/json'}) as response:
            data = json.loads(await response.text())
            avatar = data['avatar']
            return avatar
