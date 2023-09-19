import hashlib
import json
import os
import random
import time
from io import BytesIO
import requests.exceptions
import aiohttp
import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont

filepath = os.path.dirname(__file__).replace("\\", "/")
# 记录URL
bf_ban_url = "https://api.gametools.network/bfban/checkban"


# 圆角遮罩处理
def draw_rect(img, pos, radius, **kwargs):
    transp = Image.new('RGBA', img.size, (0, 0, 0, 0))
    alpha_draw = ImageDraw.Draw(transp, "RGBA")
    alpha_draw.rounded_rectangle(pos, radius, **kwargs)
    img.paste(Image.alpha_composite(img, transp))
    return img


# 圆角处理
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


# 获取专家类型图片
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


# PNG重绘大小
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


# 获取物品图片
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


# 二维码生成
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


# 图片粘贴
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


# 下载QQ头像
def download_avatar(user_id: str) -> bytes:
    url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    data = download_url(url)
    if not data or hashlib.md5(data).hexdigest() == "acef72340ac0e914090bd35799f5594e":
        url = f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100"
        data = download_url(url)
    return data


# 根据URL下载文件
def download_url(url: str) -> bytes:
    for i in range(3):
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                continue
            return resp.content
        except Exception as e:
            print(f"Error downloading {url}, retry {i}/3: {str(e)}")


# 保存用户的图片
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


# 加logo
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


# 获取EA头像
async def get_avatar(platform_id, persona_id, nucleus_id):
    default_avatar_path = filepath + "/img/No-Pats.png"
    try:
        url = f"https://api.gametools.network/bf2042/feslid/?platformid={platform_id}&personaid={persona_id}&nucleusid={nucleus_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'accept': 'application/json'}) as response:
                response.raise_for_status()
                data = json.loads(await response.text())
                avatar_url = data.get('avatar')
                print("头像URL处理"+avatar_url)
                if avatar_url:
                    try:
                        # 添加10s超时判断，如果超时直接使用默认头像
                        res = BytesIO(requests.get(avatar_url, timeout=10).content)
                        avatar = Image.open(res).convert('RGBA')
                        return avatar
                    except requests.exceptions.RequestException as e:
                        print(f"请求异常：{e}")

    except requests.exceptions.RequestException as e:
        print(f"请求异常：{e}")

    # 使用默认头像
    avatar = Image.open(default_avatar_path).convert('RGBA')
    return avatar
