import base64
import os
import random
from decimal import Decimal
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont
from hoshino.modules.bf2042.data_tools import hacker_check, get_bf_ban_check
from hoshino.modules.bf2042.picture_tools import draw_rect, circle_corner, get_class_type, png_resize, \
    get_top_object_img, \
    qr_code_gen, image_paste, get_favorite_image, get_user_avatar, paste_ic_logo, get_avatar
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
    # 1.创建黑色板块 1920*1080
    new_img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 1000))
    # 2.获取头像图片 150*150
    platform_id = 1
    nucleus_id = data['userId']
    persona_id = data['id']
    # 调用接口获取正确的头像
    avatar = await get_avatar(platform_id, persona_id, nucleus_id)
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
            final = "Pro哥\n爱吃薯条，容易“**”"
            color = "gold"
        else:
            final = "薯薯\n别拷打我了哥😭"
            color = "skyblue"

    ch_text_font_ext = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    ch_text_font_ext2 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 28)
    draw.text((1485, 228), f'鉴定结果（仅供参考）：', fill="white", font=ch_text_font_ext)
    draw.text((1485, 238), f'\n{final}', fill=f"{color}", font=ch_text_font_ext2)

    # 添加BF ban 检测结果
    bf_ban_res = await get_bf_ban_check(data["userName"], data["userId"], data["id"])
    draw.text((1485, 350), f'联BAN查询：', fill="white", font=ch_text_font_ext)
    draw.text((1485, 360), f'\n{bf_ban_res}', fill="yellow", font=ch_text_font_ext2)

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
