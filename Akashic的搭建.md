# Akashic的搭建

**Akashic**是一个基于Python运行的hypixel玩家数据查询的QQ机器人



**注意**：

该项目仍处于测试状态，可能有诸多bug，稳定性不能保证。请您再三考虑是否需要搭建该项目



想要尝试实例化运行该项目，您首先需要：

- 足够的**耐心**，熟练运用**搜索引擎**解决问题的能力
- 一台运行设备，如linux服务器，您的window计算机等等
- Python3.7及以上环境支持，推荐3.9（请自行安装并确保python可以正常运行）
- Java8及以上环境支持，推荐jre11（您可以不必手动安装java，使用mcl-installer安装Mirai时会引导您进行自动安装）
- 一个QQ账号



## Akashic的运行主要依赖以下项目：

1. #### Mirai [[mamoe/mirai: 高效率QQ机器人支持库 ]](https://github.com/mamoe/mirai)

   您可以使用[iTXTech/mcl-installer: MCL一键安装工具](https://github.com/iTXTech/mcl-installer)来快速安装Mirai及其相关依赖组件

   请您根据官方文档的教程创建并登录一个bot实例并确保其可以正常运行

2. #### Mirai-Api-Http [[project-mirai/mirai-api-http: Mirai HTTP API (console) plugin]](https://github.com/project-mirai/mirai-api-http)

   如果您已经按照上一步成功安装了MCL，可以在终端（系统终端，**并非**mcl终端）中执行`./mcl --update-package net.mamoe:mirai-api-http --type plugin --channel stable`来快速安装M-A-H（如需指定版本可在结尾加上`--version x.x.x`）

3. #### Graia-Application-Mirai [[GraiaProject/Application: 一个设计精巧, 协议实现完备的, 基于 mirai-api-http 的即时聊天软件自动化框架]](https://github.com/GraiaProject/Application)

   您可以在终端中执行`pip install graia-application-mirai`来快速安装Graia

   接下来，请您根据Graia官方文档中的教程进行M-A-H的配置，并尝试创建测试实例检测是否Graia是否能够成功连接上Mirai。如果连接成功，运行正常，那么恭喜您，您已经成功了*70%*

### **注意：**

Mirai-Api-Http 2.0以上版本与graia-application-mirai和graia-broadcast（安装graia-application-mirai时会自动安装）的某些版本可能并不兼容，如果您在正确安装Mirai，M-A-H及Graia后，如果您在正常启动mirai并成功创建及运行bot实例后，尝试运行Graia官方提供的测试实例时遇到报错，您可以尝试更换不同版本的M-A-H和Graia，该问题可以在[Discussions · GraiaProject/Application](https://github.com/GraiaProject/Application/discussions)找到解决方法



## Akashic的运行同样依赖以下python运行库：

1. #### Asyncio [[python/asyncio: asyncio historical repository)]](https://github.com/python/asyncio)

   您可以在终端中执行`pip install asyncio`来安装

2. #### Aiohttp [[aio-libs/aiohttp: Asynchronous HTTP client/server framework for asyncio and Python]](https://github.com/aio-libs/aiohttp)

   您可以在终端中执行`pip install aiohttp`来安装

3. #### Requests [[psf/requests: A simple, yet elegant HTTP library]](https://github.com/psf/requests)

   您可以在终端中执行`pip install requests`来安装



如果您确定以上依赖均已安装并**正常运行**，恭喜您，您已经成功了*90%*

### 接下来，您需要使用使用编辑器打开*Akashic.py*文件，您需要填写/修改以下内容：

1. 在源码开头处找到`key = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"`，将引号内的内容换为您的hypixel api key

   使用正版账号登入mc.hypixel.net服务器，输入/api以获取您的api key

   hypixel api key相关内容可以[Hypixel Public API](https://api.hypixel.net/)网站找到

2. 在源码结尾处找到

   `app = GraiaMiraiApplication(`
       `broadcast=bcc,`
       `connect_info=Session(`
           `host="http://localhost:xxxx",`  填入M-A-H服务运行的地址
           `authKey="xxxxxxxxxxxxxxx",`  填入M-A-H中的authKey
           `account=114514,`  填入机器人的 qq 号
           `websocket=True` 您的M-A-H中是否开启了websocket,如未开启请改为False
       `)`
   `)`

3. 保存并退出

#### 如果能够正常运行，那么恭喜您，您已经成功构建了**Akashic Bot** **: D**



