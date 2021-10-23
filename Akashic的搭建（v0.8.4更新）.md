# Akashic的搭建（v0.8.4更新）

**Akashic**是一个基于**Python**运行的hypixel玩家数据查询的**QQ机器人**（后端部分）



### **注意**：

该项目仍处于测试状态，可能有诸多bug，稳定性及功能性不能保证。请您再三考虑是否需要搭建该项目

不保证按照该文档能100%成功搭建bot实例



### 想要尝试实例化运行该项目，您首先需要：

- 足够的**耐心**，熟练运用**搜索引擎**解决问题的能力
- 一台运行设备，如Linux服务器，您的Window计算机等等
- Python3.7及以上环境支持，推荐3.9（请自行安装并确保python可以正常运行）
- Java8及以上环境支持，推荐jre11（您可以不必手动安装java，使用mcl-installer安装Mirai时会引导您进行自动安装）
- 一个QQ账号



## 安装Mirai及MAH插件

1. #### Mirai [[mamoe/mirai: 高效率QQ机器人支持库 ]](https://github.com/mamoe/mirai)

   您可以使用[iTXTech/mcl-installer: MCL一键安装工具](https://github.com/iTXTech/mcl-installer)来快速安装Mirai及其相关依赖组件

   请您根据官方文档的指引创建并登录一个bot实例，并确保其可以正常运行

2. #### Mirai-Api-Http [[project-mirai/mirai-api-http: Mirai HTTP API (console) plugin]](https://github.com/project-mirai/mirai-api-http)

   请您根据官方文档指引，安装插件M-A-H，**版本<2.0**，建议版本1.12.0



## 安装Akashic运行所必需的依赖库

1. #### 下载*requirements.txt*

2. #### 使用pip一并安装全部依赖库

   执行`pip install -r requirements.txt`即可

#### **注意：**

Mirai-Api-Http 2.0以上版本与必需依赖**graia-application-mirai**和**graia-broadcast**（安装graia-application-mirai时会自动安装）的某些版本可能并不兼容，如果您在正确安装Mirai，M-A-H及Graia后，如果您在正常启动mirai并成功创建及运行bot实例后，尝试运行Graia官方提供的测试实例时遇到报错，您可以尝试更换不同版本的M-A-H和Graia，该问题可以在[Discussions · GraiaProject/Application](https://github.com/GraiaProject/Application/discussions)找到

Graia自身与MAH存在些许版本兼容问题，开发者实测可用版本搭配为Mirai console2.7.1（或2.8.0） + MAH1.12.0 + Graia Application Mirai0.19.2（Graia Broadcast0.8.11），自带的requirements.txt默认将会安装该版本（Graia Application Mirai v0.19.2）。

## 填写配置文件

### 使用编辑器打开*config.txt*文件，您需要填写/修改以下内容：

1. ```
   Mirai-Api-Http_host = "http://localhost:8080"
   Mirai-Api-Http_authKey = "xxxxxxxxxxxxx"
   Mirai-Api-Http_account =  1919810
   Mirai-Api-Http_websocket = True
   
   Hypixel_apiKey = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
   
   Admin_account = 1145141919
   
   Command_prefix = "/"
   
   Bot_name = "TEST-BOT"
   
   ```

   以上为配置文件格式示例

2. #### 内容介绍：

   1. Mirai-Api-Http_host —— 此处填写您MAH中配置的地址，若您未对MAH做改动可不必修改
   2. Mirai-Api-Http_authKey——此处填写您MAH中配置的密钥，通常在启动Mirai console时可以找到，默认为*INITKEY*开头的一串字符
   3. Mirai-Api-Http_account——此处填写您用于建立Bot实例的qq帐号（Mirai console中登录的qq帐号）
   4. Mirai-Api-Http_websocket——此处填写您是否在MAH中开启了websocket，若开启则填True，若关闭则填False（该项可在MAH的配置文件中找到，详见MAH相关文档）
   5. Hypixel_apiKey——此处填写您的hypixel api密钥，您可以登入hypixel服务器，在聊天栏输入指令/api来获取您的api密钥，请注意将其谨慎存储，不要泄露，相关内容详见[Hypixel Public API](https://api.hypixel.net/)
   6. Admin_account——此处填入Bot管理员qq账号（您的qq账号），如果运行出现了未知的错误可能会将报错信息发送给您，您可以将报错信息反馈给开发者。开发者将根据报错内容尽快修复。
   7. Command_prefix——Bot指令触发前缀，默认为/
   8. Bot_name——您可以将Bot进行重命名，在部分场景会显示该名字

3. #### 保存并退出

#### 尝试使用终端运行*akashic.py*,如果能够正常运行，那么恭喜您，您已经成功构建了**Akashic Bot** **: D**


