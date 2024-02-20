import base64
import os
import random
from decimal import Decimal
from io import BytesIO

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


async def pic_generator(player_data, query_type, query_user_info, bf_ban_info, hacker_info):
    """
    PNG缩放透明度处理
    :param player_data: 玩家数据
    :param query_type: 查询类型
    :param query_user_info: 查询者信息
    :param bf_ban_info: 联ban信息
    :param hacker_info: 外挂检测信息
    :return:
    """
