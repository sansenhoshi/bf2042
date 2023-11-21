from .mysql_connector import *


#  绑定用户
async def bind_user(name, platform, uid, nucleusId, personaId):
    res = await create_new_user_bind(name, platform, uid, nucleusId, personaId, 0)
    return res


#   查询用户绑定状态
async def check_bind(uid):
    res = await check_user_bind_exist(uid)
    return res


#    修改用户绑定状态
async def change_user_bind(uid, player, nucleusId, personaId):
    res = await update_user_player_by_qq_id(uid, player, nucleusId, personaId)
    return res


#  绑定用户支持
async def change_user_support(uid, support):
    res = await update_user_support_by_qq_id(uid, support)
    return res


async def check_user_support(uid):
    res = await check_user_support_by_qq_id(uid)
    return res


# 修改群审批
async def change_group_approve_status(group_id, approve):
    res = await change_group_approve(group_id, approve)
    return res


# 检查群审批
async def check_group_approve_status(group_id):
    res = await check_group_approve(group_id)
    return res


async def add_query_record(player, qq_id):
    await create_query_record(player, qq_id)

