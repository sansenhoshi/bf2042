import aiohttp

map_list = {
    "Renewal": "涅槃（复兴）",
    "Orbital": "航天发射中心",
    "Manifest": "货物仓单",
    "Discarded": "废弃之地",
    "Kaleidoscope": "万花筒",
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
    "Reclaimed": "重生"
}

game_mode = {
    "Breakthrough": "突破模式",
    "Breakthrough Small": "突破模式（小型）",
    "Breakthrough Large": "突破模式（大型）",
    "Conquest": "征服模式",
    "Conquest Small": "征服模式（小型）",
    "Conquest large": "征服模式（大型）",
    "Rush": "突袭模式",
    "Modbuilder Custom": "门户自定义",
    "Hazard Zone": "危险地带",
    "Hazard Zone Small": "危险地带（小型）",
    "Custom": "自定义模式"
}
region = {
    "Europe": "欧洲",
    "Asia": "亚洲",
    "North America": "北美",
    "South America": "南美",
    "Africa": "非洲",
    "Oceania": "大洋洲"
}



async def get_server_list(server_name):
    url = f"https://api.gametools.network/bf2042/detailedserver/?name={server_name}&experiencename={server_name}&return_ownername=true&lang=zh-cn"
    async with aiohttp.ClientSession() as session:
        async with session.request("GET", url) as response:
            server_info = await response.json()
            owner_info = server_info["owner"]
            owner_name = owner_info["name"]
            owners = [owner_info]
            # 使用服务器owner信息获取服务器其他信息
            owners = json.dumps(owners)
            url = f"https://api.gametools.network/bf2042/servers/?owners={owners}"
            server_message = "服务器信息\n"
            async with aiohttp.ClientSession() as session2:
                async with session2.get(url) as response:
                    data = await response.json()
                    # 依照在线人数排序
                    data = sorted(data["servers"], key=lambda k: k['playerAmount'], reverse=True)
                    for server in data:
                        server_prefix = server["prefix"]
                        server_max_player = server["maxPlayers"]
                        server_current_number = server["playerAmount"]
                        server_mode = server["mode"]
                        server_max_que = server["maxQue"]
                        server_in_que = server["inQue"]
                        server_current_map = server["currentMap"]
                        server_region = server["region"]
                        server_message += f"\n----------" \
                                          f"\n服务器名称：{server_prefix}" \
                                          f"\n游戏模式：{game_mode[server_mode]}" \
                                          f"\n当前地图：{map_list[server_current_map]}" \
                                          f"\n最大游玩人数：{server_max_player}" \
                                          f"\n在线人数：{server_current_number}" \
                                          f"\n最大队列人数：{server_max_que}" \
                                          f"\n当前队列人数：{server_in_que}" \
                                          f"\n地区：{region[server_region]}" \
                                          f"\n创建者：{owner_name}" \
                                          f"\n----------"
            print(server_message)
        return server_message
