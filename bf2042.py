import base64
import os
import random
from decimal import Decimal
from io import BytesIO

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from hoshino.modules.bf2042.data_tools import hacker_check, get_bf_ban_check
from hoshino.modules.bf2042.picture_tools import draw_rect, circle_corner, png_resize, \
    get_top_object_img, \
    image_paste, get_favorite_image, get_user_avatar, paste_ic_logo, get_avatar, get_special_icon, draw_point_line
from hoshino.modules.bf2042.user_manager import check_user_support, check_user_support2, check_user_bind

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


async def bf_2042_gen_pic(data, platform, bot, ev, sv):
    # 1.创建黑色板块 1920*1080
    new_img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 1000))
    # 2.获取头像图片 150*150
    platform_id = 1
    nucleus_id = data['userId']
    persona_id = data['id']
    # 调用接口获取正确的头像(由于某些人的自爆头像，现在获取ea头像仅对绑定用户生效，其他的一律不显示ea头像)
    res = await check_user_bind(ev.user_id)
    if res[1] and res[0].upper() == data["userName"].upper():
        avatar = await get_avatar(platform_id, persona_id, nucleus_id, sv)
    else:
        avatar = Image.open(filepath + "/img/class_icon/No-Pats.png")
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

    top_weapon_list = sorted(data["weapons"], key=lambda k: k['kills'], reverse=True)

    # 1
    # 修饰线条
    draw.line([45, 505, 45, 585], fill="#CCFF00", width=5, joint=None)
    # draw.rectangle([50, 505, 210, 585], fill="black")
    new_img = image_paste(get_top_object_img(top_weapon_list[0], sv).resize((160, 80)), new_img, (50, 505))
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
    new_img = image_paste(get_top_object_img(top_weapon_list[1], sv).resize((160, 80)), new_img, (50, 615))
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
    new_img = image_paste(get_top_object_img(top_weapon_list[2], sv).resize((160, 80)), new_img, (50, 725))
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
    new_img = image_paste(get_top_object_img(top_weapon_list[3], sv).resize((160, 80)), new_img, (50, 845))
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
    new_img = image_paste(get_top_object_img(top_weapon_list[4], sv).resize((160, 80)), new_img, (50, 955))
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
    new_img = image_paste(get_top_object_img(top_vehicles_list[0], sv).resize((320, 80)), new_img, (980, 505))
    draw.text((1325, 500), f'{top_vehicles_list[0]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 545), f'击杀：{top_vehicles_list[0]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 500), f'KPM：{top_vehicles_list[0]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 545), f'摧毁数：{top_vehicles_list[0]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
    # draw.text((1630, 545), f'时长：{top1weapon_vehicles_time_in}h', fill="white", font=ch_text_font4)
    # 2
    # 绘制修饰线条
    draw.line([975, 615, 975, 695], fill="#CCFF00", width=5, joint=None)
    # draw.rectangle([980, 615, 1295, 695], fill="black")
    new_img = image_paste(get_top_object_img(top_vehicles_list[1], sv).resize((320, 80)), new_img, (980, 615))
    draw.text((1325, 610), f'{top_vehicles_list[1]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 655), f'击杀：{top_vehicles_list[1]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 610), f'KPM：{top_vehicles_list[1]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 655), f'摧毁数：{top_vehicles_list[1]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
    # 3
    # 绘制修饰线条
    draw.line([975, 725, 975, 805], fill="#CCFF00", width=5, joint=None)
    # draw.rectangle([980, 725, 1295, 805], fill="black")
    new_img = image_paste(get_top_object_img(top_vehicles_list[2], sv).resize((320, 80)), new_img, (980, 725))
    draw.text((1325, 720), f'{top_vehicles_list[2]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 765), f'击杀：{top_vehicles_list[2]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 720), f'KPM：{top_vehicles_list[2]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 765), f'摧毁数：{top_vehicles_list[2]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
    # 4
    # 绘制修饰线条
    draw.line([975, 845, 975, 925], fill="#66CCFF", width=5, joint=None)
    # draw.rectangle([980, 845, 1295, 925], fill="black")
    new_img = image_paste(get_top_object_img(top_vehicles_list[3], sv).resize((320, 80)), new_img, (980, 845))
    draw.text((1325, 840), f'{top_vehicles_list[3]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 885), f'击杀：{top_vehicles_list[3]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 840), f'KPM：{top_vehicles_list[3]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 885), f'摧毁数：{top_vehicles_list[3]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)
    # 5
    # 绘制修饰线条
    draw.line([975, 955, 975, 1035], fill="#66CCFF", width=5, joint=None)
    # draw.rectangle([980, 955, 1295, 1035], fill="black")
    new_img = image_paste(get_top_object_img(top_vehicles_list[4], sv).resize((320, 80)), new_img, (980, 955))
    draw.text((1325, 950), f'{top_vehicles_list[4]["vehicleName"]}', fill="white", font=en_text_font4)
    draw.text((1325, 995), f'击杀：{top_vehicles_list[4]["kills"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 950), f'KPM：{top_vehicles_list[4]["killsPerMinute"]}', fill="white", font=ch_text_font4)
    draw.text((1630, 995), f'摧毁数：{top_vehicles_list[4]["vehiclesDestroyedWith"]}', fill="white", font=ch_text_font4)

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
    draw.text((400, 16), f'联BAN查询：' + f'{bf_ban_res}', fill="#5093ff", font=ch_text_font)

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

    draw.text((400, 0), f'{final}', fill=f"{color}", font=ch_text_font)

    draw.text((5, 15), '玩家名称：' + player, fill='white', font=ch_text_font)
    draw.text((5, 38), '击杀：' + str(kills) + '，KD：' + str(killDeath) + '，KPM：' + str(killPerMin) + '，步战KD：' + str(
        infantryKillDeath) + '，AI击杀：' + str(kill_AI) + '，真·KD：' + str(real_kd) + '\n爆头率：' + str(
        headshots) + '，精准度：' + str(accuracy) + '，游玩时间：' + str(round(playtime / 3600)) + '小时，游玩场数：' + str(
        matchesPlay) + '，真·KPM：' + str(real_kpm), fill='white', font=ch_text_font)

    draw.text((5, 80), '========================武器信息========================', fill='red', font=ch_text_font)
    for index in range(0, 10):
        height = 100 + 20 * index
        draw.text((5, height), str(index + 1) + ' : ', fill='white', font=ch_text_font)
        draw.text((50, height), weapons.loc[index]['weaponName'], fill='white', font=ch_text_font)
        draw.text((150, height), '击杀数：' + str(weapons.loc[index]['kills']), fill='white', font=ch_text_font)
        draw.text((300, height), 'KPM：' + str(weapons.loc[index]['killsPerMinute']), fill='white', font=ch_text_font)
        draw.text((420, height), '爆头率：' + str(weapons.loc[index]['headshots']), fill='white', font=ch_text_font)
        draw.text((570, height), '精准度：' + str(weapons.loc[index]['accuracy']), fill='white', font=ch_text_font)

    draw.text((5, 300), '========================载具信息========================', fill='red', font=ch_text_font)
    for index in range(0, 10):
        height = 320 + 20 * index
        draw.text((5, height), str(index + 1) + ' : ', fill='white', font=ch_text_font)
        draw.text((50, height), vehicles.loc[index]['vehicleName'], fill='white', font=ch_text_font)
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


async def bf2042_weapon(data, platform, bot, ev, sv):
    # 1.创建黑色板块 1920*1080
    new_img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 1000))
    # 2.获取头像图片 150*150
    platform_id = 1
    nucleus_id = data['userId']
    persona_id = data['id']
    # 调用接口获取正确的头像(由于某些人的自爆头像，现在获取ea头像仅对绑定用户生效，其他的一律不显示ea头像)
    res = await check_user_bind(ev.user_id)
    if res[1] and res[0].upper() == data["userName"].upper():
        avatar = await get_avatar(platform_id, persona_id, nucleus_id, sv)
    else:
        avatar = Image.open(filepath + "/img/class_icon/No-Pats.png")
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
    # 最佳小队
    best_squad = "最佳小队：" + str(data["bestSquad"])
    best_show = random.choice((mvp, best_squad))
    ch_text_font2 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 36)
    draw.text((1368, 50), f'游玩场数: {matches}', fill='white', font=ch_text_font2)
    draw.text((1368, 111), f'{best_show}', fill='white', font=ch_text_font2)

    # 10.绘制武器框
    new_img = draw_rect(new_img, (25, 205, 1920 - 25, 1080 - 25), 10, fill=(0, 0, 0, 150))

    # 武器击杀数排序
    top_weapon_list = sorted(data["weapons"], key=lambda k: k['kills'], reverse=True)

    # 载入字体
    ch_text_font4 = ImageFont.truetype(filepath + '/font/NotoSansSCMedium-4.ttf', 32)
    en_text_font4 = ImageFont.truetype(filepath + '/font/BF_Modernista-Bold.ttf', 32)

    # 遍历 左
    height = 220
    index = 0
    for i in range(0, 8):
        new_img = image_paste(get_top_object_img(top_weapon_list[i], sv).resize((160, 80)), new_img, (50, height + 5))
        draw.text((230, height), f'{top_weapon_list[i]["weaponName"]}', fill="white", font=en_text_font4)
        draw.text((230, height + 45), f'击杀：{top_weapon_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((450, height), f'爆头率：{top_weapon_list[i]["headshots"]}', fill="white", font=ch_text_font4)
        draw.text((450, height + 45), f'命中率：{top_weapon_list[i]["accuracy"]}', fill="white", font=ch_text_font4)

        draw.text((730, height), f'KPM：{top_weapon_list[i]["killsPerMinute"]}', fill="white", font=ch_text_font4)
        draw.text((730, height + 45), f'时长：{int(int(top_weapon_list[i]["timeEquipped"]) / 3600 + 0.55)} H',
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
    for i in range(index, index + 8):
        new_img = image_paste(get_top_object_img(top_weapon_list[i], sv).resize((160, 80)), new_img, (975, height + 5))
        draw.text((1160, height), f'{top_weapon_list[i]["weaponName"]}', fill="white", font=en_text_font4)
        draw.text((1160, height + 45), f'击杀：{top_weapon_list[i]["kills"]}', fill="white", font=ch_text_font4)

        draw.text((1380, height), f'爆头率：{top_weapon_list[i]["headshots"]}', fill="white", font=ch_text_font4)
        draw.text((1380, height + 45), f'命中率：{top_weapon_list[i]["accuracy"]}', fill="white", font=ch_text_font4)

        draw.text((1660, height), f'KPM：{top_weapon_list[i]["killsPerMinute"]}', fill="white", font=ch_text_font4)
        draw.text((1660, height + 45), f'时长：{int(int(top_weapon_list[i]["timeEquipped"]) / 3600 + 0.55)} H',
                  fill="white",
                  font=ch_text_font4)
        height += 105
        # 图片处理完成 发送
    player_name = data["userName"]
    sv.logger.info(f"玩家：{player_name}->武器图片处理完成")
    # 显示图片
    # new_img.show()
    b_io = BytesIO()
    new_img.save(b_io, format="PNG")
    base64_str = 'base64://' + base64.b64encode(b_io.getvalue()).decode()
    return base64_str
