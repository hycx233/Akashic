# Akashic

Akashic是一个由Python编写的数据查询机器人（后端）。基于[Mirai](https://github.com/mamoe/mirai)它可以运行在QQ中，为用户提供游戏数据查询服务

Akashic，音译为阿卡什（或阿卡夏），意译为以太



### 开发进度

- Akashic Bot平台 —— 多平台适配
  - Tencent QQ
    - [x] ~~mirai-api-http & Graia Application~~
    - [x] mirai-api-http & Ariadne
      - [x] 群聊查询
      - [x] 私聊查询
    - [ ] ???(未定) —— 频道查询
  - Discord
    - [ ] discord.py
      - [ ] ...
  - Telegram
    - [ ] AIOGram
      - [ ] ...
- Akashic Bot功能
  - Minecraft
    - Hypixel
      - [x] 基本信息,Bedwars,Skywars,公会...查询
      - [ ] 游戏不同模式数据查询
      - [ ] Skyblock信息查询
      - [ ] 更多游戏查询服务...
    - Syuu
      - [x] Rank数据查询
    - Other
      - [x] 服务器查询 
        - [ ] Todo: Bug fixing
      - [x] 玩家资料查询
      - [ ] 更多服务...
  - Arcaea
      - Arcaea Limited Api
          - [x] B30查询
          - [ ] Recent查询
          - [ ] 指定歌曲查询
          - [ ] 玩家信息查询
      - BotArcApi
          - [ ] B30查询
              - [ ] Overflow查询
          - [ ] Recent查询
          - [ ] 指定歌曲查询
      - Other
          - [ ] 单曲信息查询
              - [ ] 预览音频
          - [ ] 单曲ptt计算
          - [ ] 指定定数/等级查询
          - [ ] ...
  - Phigros
      - [ ] 单曲信息查询
      - [ ] 单曲rks计算
      - [ ] 指定定数/等级查询
      - [ ] ...
  - Other
      - [ ] 数据存储迁移至MongoDB
      - [x] 随机数生成等小工具
      - [ ] 签到系统
      - [ ] Bilibili监听推送功能
      - [ ] 更多小功能



### ~~Akashic的构建~~

鉴于项目的不稳定性与合法性，本项目将不再提供搭建方法，仅在此开源源代码供大家参考学习，或为本项目提出好的点子和建议。

注：从v11.0开始，本项目使用的Python - MAH中间件由[GraiaProject/Application](https://github.com/GraiaProject/Application) (V4)全面迁移至[Ariadne](https://github.com/GraiaProject/Ariadne) (V4+)，未来会进一步迁移至[Avilla](https://github.com/GraiaProject/Avilla) (V5)



### 开源协议与使用项目说明

本项目使用**AGPLv3**协议开源，建议使用/间接使用到本项目源码的项目使用AGPLv3开源，同时不支持/鼓励一切商业使用。

#### **本项目使用到的开源项目**

- [mamoe/mirai: 高效率 QQ 机器人支持库](https://github.com/mamoe/mirai) - 底层支持
- [project-mirai/mirai-api-http: Mirai HTTP API (console) plugin](https://github.com/project-mirai/mirai-api-http) -- 通信 协议支持
- [GraiaProject/Application: 一个设计精巧, 协议实现完备的, 基于 mirai-api-http 的即时聊天软件自动化框架. ](https://github.com/GraiaProject/Application) -- Python - mirai-api-http通信中间件 框架
- [GraiaProject/Ariadne: 一个优雅且完备的 Python QQ 自动化框架。基于 Mirai API HTTP v2。 Powered by Graia Project。](https://github.com/GraiaProject/Ariadne) -- Python - mirai-api-http通信中间件 框架

- [Spelako Project](https://github.com/Spelako) -- Hypixel查询部分翻译支持，排版参考



在GNU Affero通用公共许可证第三版 (GNU Affero General Public License version 3, AGPLv3) 的约束下, 您可以自由地使用和修改该软件, 以及传播该软件或其修改过的版本. 此许可证的约束包括但不限于：

1. 您不得抹去或修改该软件的作者信息及许可证声明。
2. 如传播该软件或其修改过的版本, 您必须同时使用 AGPLv3 开放其源代码。

详见[GNU Affero通用公共许可证 - GNU工程 - 自由软件基金会](https://www.gnu.org/licenses/agpl-3.0)

#### **许可证**

```
Copyright (C) 2021-2022 Akashic Project by hycx233.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```

