**适用于hoshino的战地风云2042战绩查询（图片）**
<br><br>
**战地风云2042**
<br>
**常规----------**<br>
[.盒  ID]  PC战绩查询<br>
[.武器+ID] 查询武器数据<br>
[.枪械+ID] 另一种查询武器数据的方法<br>
[.载具+ID] 查询载具数据<br>
[.专家+ID] 查询专家数据<br>
[.模式+ID] 查询游戏模式数据<br>
[.地图+ID] 查询地图游玩情况<br>
[.配备+ID] 查询配备数据<br>
**另一种查询方式----------**<br>
[.数据+ID] 查询文字图片版本玩家数据<br>
[/枪械+ID] 另一种查询武器数据的方法<br>
[/载具+ID] 查询载具数据<br>
[/专家+ID] 查询专家数据<br>
[/模式+ID] 查询游戏模式数据<br>
[/地图+ID] 查询地图游玩情况<br>
[.装置+ID] 查询配备数据<br>
**其他操作----------**<br>
[.2042战绩+ID] PC战绩查询<br>
[.绑定+ID] 绑定游戏ID到QQ（仅仅支持PC）<br>
[.修改绑定+ID] 修改绑定的游戏id<br>
[.2042门户+门户关键字] 查询门户服务器列表<br>
**主机----------**<br>
[.2042xbox端战绩+ID] xbox战绩查询<br>
[.2042ps端战绩+ID] ps战绩查询<br>
[.PS绑定+ID] 绑定游戏ID到QQ（仅仅支持PS）<br>
[.XBOX绑定+ID] 绑定游戏ID到QQ（仅仅支持XBOX）<br>
**特色----------**<br>
[.上传图片] 上传自定义背景（需要请求bot管理员获得）<br>
[.清空背景] 清空所有背景图片<br>
入群检测-----<br>
检测新加群的EA ID<br>
****门户****<br>
~~[`.2042门户 + 门户关键字 `] 查询关键字在线人数最多的服务器~~ 暂时出了点问题，查不到服务器或者直接报错，等修复

**需要安装依赖**

```bash
pip install -r requirements.txt
```

**在`hoshino`的`config`文件夹中`__bot__.py`中的`MODULES_ON`部分添加`bf2042`即可**
<br><br>
1.代码写的很烂，轻喷，主业是Java，Python是我东拼西凑整了一点出来用的，毫无编码规范（屎山警告）
<br>2.自己随便整了一个外挂的检测方法，可以简单的判断该玩家是否为暴力外挂<br>
<br>
`bg`文件夹中存放的是背景<br>
`common`是普通背景<br>有什么好看的就往里面塞吧<br>
`user`是用户的背景存放位置，根据qq号会创建对应的文件夹，可以放入多张图片，随机选取其中一张作为背景
<br>
<br>**PS**：分辨率最好是是16:9的，不然系统裁剪后会有黑边，虽然不影响，但是你不想看你好看的色图做你的背景吗？<br>
<br>第一次运行如果没有对应的图片会自己下载，有些东西名字太长可能会遮挡到别的内容，我也没时间详细弄了，打工人何必为难打工人呢<br>
<br>
<br><br>
![个人数据示例图](https://sansenhoshi.site/upload/67FE863E3934CCB998F735DF1966FAD6.jpg)
![武器数据示例图](https://sansenhoshi.site/upload/weapon-info.png)
