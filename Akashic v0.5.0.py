import aiohttp
import requests
import asyncio
import threading
import time
import datetime
import queue
from threading import Thread
from time import gmtime,strftime
from requests.adapters import HTTPAdapter
from graia.application import GraiaMiraiApplication
from graia.application.group import Group, Member
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain
from graia.application.message.parser.signature import FullMatch, RequireParam
from graia.application.session import Session
from graia.broadcast import Broadcast




def hyp(text):
    """/hyp查询"""

    key = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    start = datetime.datetime.now()

    # requests.session().mount('http://', HTTPAdapter(max_retries=3))
    # requests.session().mount('https://', HTTPAdapter(max_retries=3))
    timeout_hyp = aiohttp.ClientTimeout(total=5)

    def timeStamp(unixtime):
        time1 = time.localtime(float(unixtime / 1000))
        result = time.strftime("%Y-%m-%d %H:%M:%S", time1)
        return result

    def timeconvert(unixtime):
        time1 = datetime.datetime.strptime(timeStamp(int(unixtime) * 1000), '%Y-%m-%d %H:%M:%S')
        time2 = datetime.datetime.strptime(timeStamp(0), '%Y-%m-%d %H:%M:%S')
        delta = time1 - time2
        time3 = delta.days * 24
        time4 = delta.seconds
        hours = str((int((strftime("%H:%M:%S", gmtime(time4)))[0:2]) + time3))
        minutes = (strftime("%H:%M:%S", gmtime(time4)))[3:5]
        seconds = (strftime("%H:%M:%S", gmtime(time4)))[6:8]
        result = '%s:%s:%s' % (hours, minutes, seconds)
        return result

    def delcolor(string):
        for color in (
        '§0', '§1', '§2', '§3', '§4', '§5', '§6', '§7', '§8', '§9', '§a', '§b', '§c', '§d', '§e', '§f', '§k', '§l',
        '§m', '§n', '§o', '§r'):
            string = string.replace(color, '')
        return string

    input = str(text)
    error = '0/NaN'
    str1 = ' '
    num = (len(input) - len(input.replace(str1, ''))) // len(str1)
    if not str(num) == '1':
        output = "请检查您输入的指令是否正确!"
        return output

    else:
        command = str.split(input)[0]
        player = str.split(input)[1]
        url = 'https://api.mojang.com/users/profiles/minecraft/%s' % (player)
        start_mojang = datetime.datetime.now()

        try:
            uuiddata = requests.get(url).json()
            uuid = uuiddata['id']
            end_mojang = datetime.datetime.now()
            used_mojang = end_mojang - start_mojang
        except:
            output = '该玩家无数据!'
            return output
        start_hyp = datetime.datetime.now()

        def thread_loop_task(loop, uuid):
            asyncio.set_event_loop(loop)

            async def game_stats_get(uuid, key):
                while True:
                    url = 'https://api.hypixel.net/player?key=%s&uuid=%s' % (key, uuid)
                    async with aiohttp.ClientSession(timeout=timeout_hyp) as session:
                        try:
                            async with session.get(url, timeout=timeout_hyp) as resp:
                                data = await resp.json()
                                print('success1')
                                return data
                        except:
                            async with session.get(url, timeout=timeout_hyp) as resp:
                                data = await resp.json()
                                print('success1_retry')
                                return data

            async def online_stats_get(uuid, key):
                while True:
                    url = 'https://api.hypixel.net/status?key=%s&uuid=%s' % (key, uuid)
                    async with aiohttp.ClientSession(timeout=timeout_hyp) as session:
                        try:
                            async with session.get(url, timeout=timeout_hyp) as resp:
                                data = await resp.json()
                                print('success2')
                                return data
                        except:
                            async with session.get(url, timeout=timeout_hyp) as resp:
                                data = await resp.json()
                                print('success2_retry')
                                return data

            async def rsw_stats_get(uuid, key):
                while True:
                    url = 'https://api.hypixel.net/player/ranked/skywars?key=%s&uuid=%s' % (key, uuid)
                    async with aiohttp.ClientSession(timeout=timeout_hyp) as session:
                        try:
                            async with session.get(url, timeout=timeout_hyp) as resp:
                                data = await resp.json()
                                print('success3')
                                return data
                        except:
                            async with session.get(url, timeout=timeout_hyp) as resp:
                                data = await resp.json()
                                print('success3_retry')
                                return data

            future = [asyncio.ensure_future(game_stats_get(uuid, key)),
                      asyncio.ensure_future(online_stats_get(uuid, key)),
                      asyncio.ensure_future(rsw_stats_get(uuid, key))]
            loop.run_until_complete(asyncio.wait(future))
            result = [future[0].result(), future[1].result(), future[2].result()]
            return result

        class MyThread(threading.Thread):
            def __init__(self, func, args=()):
                super(MyThread, self).__init__()
                self.func = func
                self.args = args

            def run(self):
                self.result = self.func(*self.args)

            def get_result(self):
                try:
                    return self.result
                except Exception as e:
                    return None

        thread_loop = asyncio.new_event_loop()
        threads = []
        t = MyThread(thread_loop_task, args=(thread_loop, uuid,))
        t.start()
        threads.append(t.get_result())
        t.join()
        result = t.get_result()
        end_hyp = datetime.datetime.now()
        used_hyp = end_hyp - start_hyp
        data1 = result[0]
        data2 = result[1]
        data3 = result[2]

        '''---------------------------------------------STATS---------------------------------------------'''
        # url1 = 'https://api.hypixel.net/player?key=%s&uuid=%s' % (key, uuid)
        # data1 = requests.get(url1).json()  # get player's information
        ifsuccess = data1['success']

        if ifsuccess is True:
            result = data1['player']
            if result is None:
                output = '玩家不存在！'
                return output
            else:
                try:
                    try:
                        name = data1['player']['displayname']
                    except:
                        name = player
                    try:
                        prefix = delcolor(data1['player']['prefix'])
                        if prefix == 'NONE':
                            prefix = ''
                        elif prefix is None:
                            prefix = ''
                    except:
                        prefix = ''
                    try:
                        rank_pro = '[%s]' % data1['player']['rank']
                        if rank_pro == 'NORMAL':
                            rank_pro = ''
                        elif rank_pro == '[NORMAL]':
                            rank_pro = ''
                    except:
                        rank_pro = ''
                    try:
                        rank = data1['player']['newPackageRank']
                    except:
                        rank = ''
                    if rank == 'VIP':
                        rank = '[VIP]'
                    elif rank == 'VIP_PLUS':
                        rank = '[VIP+]'
                    elif rank == 'MVP':
                        rank = '[MVP]'
                    elif rank == 'MVP_PLUS':
                        try:
                            rank_plusplus = data1['player']['monthlyPackageRank']
                            if rank_plusplus == 'SUPERSTAR':
                                rank = '[MVP++]'
                            else:
                                rank = '[MVP+]'
                        except:
                            rank = '[MVP+]'
                    elif rank == 'NONE':
                        rank = ''
                    elif rank is None:
                        rank = ''


                except Exception as Error:
                    output = '运行出错，请联系开发者!报错位置:%s' % Error
        else:
            try:
                output = data1['cause']
                if output == 'Invalid API key':
                    output = 'API key为空,请检查是否正确配置API key!'
                    return output
                elif output == 'Key throttle':
                    output = 'API key达到查询上限,请稍后再试!'
                    return output
                else:
                    output = '从api.hypixel.net获取数据失败，原因:%s' % output
                    return output
            except:
                output = '从api.hypixel.net获取数据失败，原因未知'
                return output

        '''---------------------------------------------ONLINE---------------------------------------------'''
        if command in ('/hypixel', '/hyp', '/HYP', '/查', '/查询', '/info', '/信息'):
            # url2 = 'https://api.hypixel.net/status?key=%s&uuid=%s' % (key, uuid)
            # data2 = requests.get(url2).json()
            ifsuccess2 = data2['success']
            if ifsuccess2 is True:
                status = data2['session']['online']
                if status is True:
                    try:
                        mode = '|%s' % data2['session']['mode']
                    except:
                        mode = ''
                    try:
                        map = '|%s' % data2['session']['map']
                    except:
                        map = ''
                    gametype = data2['session']['gameType']
                    playing = '%s%s%s' % (gametype, mode, map)
                    online = '[在线]'
                else:
                    online = '[离线]'
                    try:
                        recentgame = data1['player']['mostRecentGameType']
                    except:
                        recentgame = 'NaN'
                    playing = ' 最近游戏:%s' % recentgame
            else:
                playing = error
                online = '[ERROR]'
        else:
            pass

        '''---------------------------------------------RSW---------------------------------------------'''
        if command in ('/sw', '/skywars', '/SW', '/SkyWars', '/空岛', '/空岛战争'):
            # url3 = 'https://api.hypixel.net/player/ranked/skywars?key=%s&uuid=%s' % (key, uuid)
            # data3 = requests.get(url3).json()
            ifsuccess3 = data3['success']
            if ifsuccess3 is True:
                try:
                    position_rsw = data3['result']['position']
                except:
                    position_rsw = 'NaN'
                try:
                    score_rsw = data3['result']['score']
                except:
                    score_rsw = '0'
                rsw = 'Rank分数:%s Rank排名:%s' % (score_rsw, position_rsw)
            else:
                rsw = 'Rank数据未找到!'
        else:
            pass

    '''--------------------------------------------------MATCH RESULT--------------------------------------------------'''
    output = "暂不支持的指令,请检查是否有拼写错误!"
    try:
        if command in ('/hypixel', '/hyp', '/HYP', '/查', '/查询', '/info', '/信息'):
            try:
                exp = float(data1['player']['networkExp'])
                level = ('%.2f' % ((exp / 1250 + 12.25) ** 0.5 - 2.5))
            except:
                level = '1'
            try:
                karma = data1['player']['karma']
            except:
                karma = '0'
            try:
                achievement = data1['player']['achievementPoints']
            except:
                achievement = '0'
            try:
                firstlogin = timeStamp(data1['player']['firstLogin'])
            except:
                firstlogin = 'NaN'
            try:
                lastlogin = timeStamp(data1['player']['lastLogin'])
            except:
                lastlogin = 'NaN'
            try:
                lastlogout = timeStamp(data1['player']['lastLogout'])
            except:
                lastlogout = 'NaN'

            output = "%s%s%s%s[Lv.%s]\n%s%s\n成就点数:%s 人品值:%s\n首次登入时间:%s\n上次登入时间:%s\n上次下线时间:%s" % (
            rank_pro, prefix, rank, name, level, online, playing, achievement, karma, firstlogin, lastlogin,
            lastlogout)
        elif command in ('/sw', '/skywars', '/SW', '/SkyWars', '/空岛', '/空岛战争'):
            '''---------------------------------------------SKYWARS---------------------------------------------'''
            try:
                level_sw = data1['player']['stats']['SkyWars']['levelFormatted']
                level_sw = delcolor(level_sw)
            except:
                level_sw = '0'
            try:
                coins_sw = data1['player']['stats']['SkyWars']['coins']
            except:
                coins_sw = '0'
            try:
                heads_sw = (data1['player']['stats']['SkyWars']['heads'])
            except:
                heads_sw = '0'
            try:
                assists_sw = data1['player']['stats']['SkyWars']['assists']
            except:
                assists_sw = '0'
            try:
                deaths_sw = data1['player']['stats']['SkyWars']['deaths']
            except:
                deaths_sw = '0'
            try:
                kills_sw = data1['player']['stats']['SkyWars']['kills']
            except:
                kills_sw = '0'
            try:
                wins_sw = data1['player']['stats']['SkyWars']['wins']
            except:
                wins_sw = '0'
            try:
                losses_sw = data1['player']['stats']['SkyWars']['losses']
            except:
                losses_sw = '0'
            try:
                kd_sw = '%.2f' % (kills_sw / deaths_sw)
            except:
                kd_sw = '0'
            try:
                wl_sw = '%.2f' % (wins_sw / losses_sw)
            except:
                wl_sw = '0'
            try:
                arrows_sw_shot = data1['player']['stats']['SkyWars']['arrows_shot']
                arrows_sw_hit = data1['player']['stats']['SkyWars']['arrows_hit']
                arrows_sw_acc = '%.2f%%' % (arrows_sw_hit / arrows_sw_shot * 100)
            except:
                arrows_sw_shot = '0'
                arrows_sw_hit = '0'
                arrows_sw_acc = '0'
            try:
                thrown_sw = data1['player']['stats']['SkyWars']['egg_thrown']
            except:
                thrown_sw = '0'
            try:
                chestsopened_sw = data1['player']['stats']['SkyWars']['chests_opened']
            except:
                chestsopened_sw = '0'
            try:
                enderpearls_thrown_sw = data1['player']['stats']['SkyWars']['enderpearls_thrown']
            except:
                enderpearls_thrown_sw = '0'
            try:
                blocksplaced_sw = data1['player']['stats']['SkyWars']['blocks_placed']
            except:
                blocksplaced_sw = '0'
            try:
                blocksbroken_sw = data1['player']['stats']['SkyWars']['blocks_broken']
            except:
                blocksbroken_sw = '0'
            try:
                playedtime_sw_1 = timeconvert(data1['player']['stats']['SkyWars']['time_played_solo'])
            except:
                playedtime_sw_1 = 'NaN'
            try:
                playedtime_sw_2 = timeconvert(data1['player']['stats']['SkyWars']['time_played_team'])
            except:
                playedtime_sw_2 = 'NaN'
            try:
                playedtime_sw = timeconvert(data1['player']['stats']['SkyWars']['time_played'])
            except:
                playedtime_sw = 'NaN'

            output = "%s%s%s%s[%s]\n硬币:%s 头颅:%s 总助攻:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总胜场:%s 总败场:%s 总W/L:%s\n%s" % (
            rank_pro, prefix, rank, name, level_sw, coins_sw, heads_sw, assists_sw, kills_sw, deaths_sw, kd_sw,
            wins_sw, losses_sw, wl_sw, rsw)
        elif command in ('/bw', '/bedwars', '/BW', '/BedWars', '/起床', '/起床战争'):
            '''---------------------------------------------BEDWARS---------------------------------------------'''
            try:
                level_bw = data1['player']['achievements']['bedwars_level']
            except:
                level_bw = '0'
            try:
                kills_bw = data1['player']['stats']['Bedwars']['kills_bedwars']
            except:
                kills_bw = '0'
            try:
                deaths_bw = data1['player']['stats']['Bedwars']['deaths_bedwars']
            except:
                deaths_bw = '0'
            try:
                kills_bw_final = data1['player']['stats']['Bedwars']['final_kills_bedwars']
            except:
                kills_bw_final = '0'
            try:
                deaths_bw_final = data1['player']['stats']['Bedwars']['final_deaths_bedwars']
            except:
                deaths_bw_final = '0'
            try:
                wins_bw = data1['player']['stats']['Bedwars']['wins_bedwars']
            except:
                wins_bw = '0'
            try:
                losses_bw = data1['player']['stats']['Bedwars']['losses_bedwars']
            except:
                losses_bw = '0'
            try:
                beds_bw = data1['player']['stats']['Bedwars']['beds_broken_bedwars']
            except:
                beds_bw = '0'
            try:
                coins_bw = data1['player']['stats']['Bedwars']['coins']
            except:
                coins_bw = '0'
            try:
                winstreak_bw = data1['player']['stats']['Bedwars']['winstreak']
            except:
                winstreak_bw = '0'
            try:
                kd_bw = '%.2f' % (kills_bw / deaths_bw)
            except:
                kd_bw = '0'
            try:
                kd_bw_final = '%.2f' % (kills_bw_final / deaths_bw_final)
            except:
                kd_bw_final = '0'
            try:
                wl_bw = '%.2f' % (wins_bw / losses_bw)
            except:
                wl_bw = '0'

            output = "%s%s%s%s[Lv.%s]\n硬币:%s 破坏床数:%s 当前连胜:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总最终击杀:%s 总最终死亡:%s 总最终K/D:%s\n总胜场:%s 总败场:%s 总W/L:%s" % (
            rank_pro, prefix, rank, name, level_bw, coins_bw, beds_bw, winstreak_bw, kills_bw, deaths_bw, kd_bw,
            kills_bw_final, deaths_bw_final, kd_bw_final, wins_bw, losses_bw, wl_bw)
        elif command in ('/mw', '/megawalls', '/MegaWalls', '/MW', '/超战', '/超级战墙'):
            '''---------------------------------------------MEGAWALLS---------------------------------------------'''
            try:
                coins_walls3 = data1['player']['stats']['Walls3']['coins']
            except:
                coins_walls3 = '0'
            try:
                witherdamage_walls3 = data1['player']['stats']['Walls3']['wither_damage']
            except:
                witherdamage_walls3 = '0'
            try:
                kills_walls3_defender = data1['player']['stats']['Walls3']['defender_kills']
            except:
                kills_walls3_defender = '0'
            try:
                kills_walls3 = data1['player']['stats']['Walls3']['kills']
            except:
                kills_walls3 = '0'
            try:
                deaths_walls3 = data1['player']['stats']['Walls3']['deaths']
            except:
                deaths_walls3 = '0'
            try:
                assists_walls3 = data1['player']['stats']['Walls3']['assists']
            except:
                assists_walls3 = '0'
            try:
                kills_walls3_final = data1['player']['stats']['Walls3']['final_kills']
            except:
                kills_walls3_final = '0'
            try:
                deaths_walls3_final = data1['player']['stats']['Walls3']['final_deaths']
            except:
                deaths_walls3_final = '0'
            try:
                assists_walls3_final = data1['player']['stats']['Walls3']['final_assists']
            except:
                assists_walls3_final = '0'
            try:
                wins_walls3 = data1['player']['stats']['Walls3']['wins']
            except:
                wins_walls3 = '0'
            try:
                losses_walls3 = data1['player']['stats']['Walls3']['losses']
            except:
                losses_walls3 = '0'
            try:
                kd_walls3 = '%.2f' % (kills_walls3 / deaths_walls3)
            except:
                kd_walls3 = '0'
            try:
                kd_walls3_final = '%.2f' % (kills_walls3_final / deaths_walls3_final)
            except:
                kd_walls3_final = '0'
            try:
                wl_walls3 = '%.2f' % (wins_walls3 / losses_walls3)
            except:
                wl_walls3 = '0'

            output = "%s%s%s%s\n硬币:%s 总伤害凋灵:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总最终击杀:%s 总最终死亡:%s 总最终K/D:%s\n总胜场:%s 总败场:%s 总W/L:%s\n总助攻:%s 总最终助攻:%s" % (
            rank_pro, prefix, rank, name, coins_walls3, witherdamage_walls3, kills_walls3, deaths_walls3, kd_walls3,
            kills_walls3_final, deaths_walls3_final, kd_walls3_final, wins_walls3, losses_walls3, wl_walls3,
            assists_walls3, assists_walls3_final)
        elif command in ('/uhc', '/UHC', '/极限生存', '/极限生存冠军'):
            '''---------------------------------------------UHC---------------------------------------------'''
            try:
                coins_uhc = data1['player']['stats']['UHC']['coins']
            except:
                coins_uhc = '0'
            try:
                kills_uhc_2 = data1['player']['stats']['UHC']['kills']
            except:
                kills_uhc_2 = 0
            try:
                kills_uhc_1 = data1['player']['stats']['UHC']['kills_solo']
            except:
                kills_uhc_1 = 0
            try:
                deaths_uhc_2 = data1['player']['stats']['UHC']['deaths']
            except:
                deaths_uhc_2 = 0
            try:
                deaths_uhc_1 = data1['player']['stats']['UHC']['deaths_solo']
            except:
                deaths_uhc_1 = 0
            try:
                score_uhc = data1['player']['stats']['UHC']['score']
            except:
                score_uhc = 0
            try:
                headseaten_uhc_2 = data1['player']['stats']['UHC']['heads_eaten']
            except:
                headseaten_uhc_2 = 0
            try:
                headseaten_uhc_1 = data1['player']['stats']['UHC']['heads_eaten_solo']
            except:
                headseaten_uhc_1 = 0
            try:
                wins_uhc_2 = data1['player']['stats']['UHC']['wins']
            except:
                wins_uhc_2 = 0
            try:
                wins_uhc_1 = data1['player']['stats']['UHC']['wins_solo']
            except:
                wins_uhc_1 = 0
            try:
                wins_uhc = int(wins_uhc_1 + wins_uhc_2)
            except:
                wins_uhc - 0
            try:
                kills_uhc = int(kills_uhc_1 + kills_uhc_2)
            except:
                kills_uhc = 0
            try:
                deaths_uhc = int(deaths_uhc_1 + deaths_uhc_2)
            except:
                deaths_uhc = 0
            try:
                headseaten_uhc = int(headseaten_uhc_1 + headseaten_uhc_2)
            except:
                headseaten_uhc = 0
            try:
                kd_uhc = '%.2f' % (kills_uhc / deaths_uhc)
            except:
                kd_uhc = 0

            output = "%s%s%s%s\n硬币:%s 分数:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总胜场:%s 总金头使用:%s" % (
            rank_pro, prefix, rank, name, coins_uhc, score_uhc, kills_uhc, deaths_uhc, kd_uhc, wins_uhc,
            headseaten_uhc)
        elif command in ('/duel', '/duels', '/Duels', '/Duel', '/决斗', '/决斗游戏'):
            '''---------------------------------------------DUELS---------------------------------------------'''
            try:
                kills_duels = data1['player']['stats']['Duels']['kills']
            except:
                kills_duels = 0
            try:
                deaths_duels = data1['player']['stats']['Duels']['deaths']
            except:
                deaths_duels = 0
            try:
                wins_duels = data1['player']['stats']['Duels']['wins']
            except:
                wins_duels = 0
            try:
                losses_duels = data1['player']['stats']['Duels']['losses']
            except:
                losses_duels = 0
            try:
                wl_duels = str('%.2f' % (wins_duels / losses_duels))
            except:
                wl_duels = 0
            try:
                kd_duels = str('%.2f' % (kills_duels / deaths_duels))
            except:
                kd_duels = 0
            try:
                arrows_shots_duels = data1['player']['stats']['Duels']['bow_shots']
            except:
                arrows_shots_duels = 0
            try:
                arrows_hits_duels = data1['player']['stats']['Duels']['bow_hits']
            except:
                arrows_hits_duels = 0
            try:
                arrows_acc_duels = str('%.2f%%' % (arrows_hits_duels / arrows_shots_duels * 100))
            except:
                arrows_acc_duels = '0%'
            try:
                melee_swings_duels = data1['player']['stats']['Duels']['melee_swings']
            except:
                melee_swings_duels = 0
            try:
                melee_hits_duels = data1['player']['stats']['Duels']['melee_hits']
            except:
                melee_hits_duels = 0
            try:
                melee_acc_duels = str('%.2f%%' % (melee_hits_duels / melee_swings_duels * 100))
            except:
                melee_acc_duels = '0%'
            try:
                coins_duels = data1['player']['stats']['Duels']['coins']
            except:
                coins_duels = 0

            output = "%s%s%s%s\n硬币:%s\n近战命中率:%s 射击命中率:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总胜场:%s 总败场:%s 总W/L:%s" % (
            rank_pro, prefix, rank, name, coins_duels, melee_acc_duels, arrows_acc_duels, kills_duels, deaths_duels,
            kd_duels, wins_duels, losses_duels, wl_duels)
        elif command in ('/bsg', '/BSG', '/hg', '/HG', '/饥饿游戏', '/闪电饥饿游戏', '/饥饿'):
            '''---------------------------------------------BSG---------------------------------------------'''
            try:
                kills_bsg = data1['player']['stats']['HungerGames']['kills']
            except:
                kills_bsg = 0
            try:
                deaths_bsg = data1['player']['stats']['HungerGames']['deaths']
            except:
                deaths_bsg = 0
            try:
                kd_bsg = str('%.2f' % (kills_bsg / deaths_bsg))
            except:
                kd_bsg = 0
            try:
                coins_bsg = data1['player']['stats']['HungerGames']['coins']
            except:
                coins_bsg = 0
            try:
                wins_bsg = data1['player']['stats']['HungerGames']['wins']
            except:
                wins_bsg = 0
            try:
                gamesplayed_bsg = deaths_bsg + wins_bsg
            except:
                gamesplayed_bsg = 0
            try:
                timeplayed_bsg = timeconvert(data1['player']['stats']['HungerGames']['time_played'])
            except:
                timeplayed_bsg = timeconvert(0)
            try:
                kg_bsg = str('%.2f' % (kills_bsg / gamesplayed_bsg))
            except:
                kg_bsg = 0

            output = "%s%s%s%s\n硬币:%s 总胜场:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总游戏时长:%s 总游戏场数:%s 总K/G:%s\n*由于hypixel早期数据问题,部分值可能并不正确" % (
            rank_pro, prefix, rank, name, coins_bsg, wins_bsg, kills_bsg, deaths_bsg, kd_bsg, timeplayed_bsg,
            gamesplayed_bsg, kg_bsg)
        elif command in ('/mm', '/MM', '/murder', 'Murder', '/密室', '/密室杀手'):
            '''---------------------------------------------MURDER MYSTERY---------------------------------------------'''
            try:
                coins_murder = data1['player']['stats']['MurderMystery']['coins']
            except:
                coins_murder = 0
            try:
                kills_murder = data1['player']['stats']['MurderMystery']['kills']
            except:
                kills_murder = 0
            try:
                deaths_murder = data1['player']['stats']['MurderMystery']['deaths']
            except:
                deaths_murder = 0
            try:
                wins_murder = data1['player']['stats']['MurderMystery']['wins']
            except:
                wins_murder = 0
            try:
                gamesplayed_murder = data1['player']['stats']['MurderMystery']['games']
            except:
                gamesplayed_murder = 0
            try:
                kills_murder_knife = data1['player']['stats']['MurderMystery']['knife_kills']
            except:
                kills_murder_knife = 0
            try:
                kills_murder_bow = data1['player']['stats']['MurderMystery']['bow_kills']
            except:
                kills_murder_bow = 0
            try:
                kills_murder_knife_thrown = data1['player']['stats']['MurderMystery']['thrown_knife_kills']
            except:
                kills_murder_knife_thrown = 0
            try:
                kills_murder_infected = data1['player']['stats']['MurderMystery']['kills_as_infected']
            except:
                kills_murder_infected = 0
            try:
                kills_murder_survivor = data1['player']['stats']['MurderMystery']['kills_as_survivor']
            except:
                kills_murder_survivor = 0
            try:
                wins_murder_infected = data1['player']['stats']['MurderMystery']['survivor_wins']
            except:
                wins_murder_infected = 0

            output = "%s%s%s%s\n硬币:%s 总胜场:%s\n总击杀:%s 总死亡:%s\n弓箭击杀:%s 飞刀击杀:%s 总游戏场数:%s\n感染者击杀:%s 生存者击杀:%s 感染模式胜场:%s" % (
            rank_pro, prefix, rank, name, coins_murder, wins_murder, kills_murder, deaths_murder, kills_murder_bow,
            kills_murder_knife_thrown, gamesplayed_murder, kills_murder_infected, kills_murder_survivor,
            wins_murder_infected)
        elif command in ('/tnt', '/TNT'):
            '''---------------------------------------------TNT GAMES---------------------------------------------'''
            try:
                coins_tnt = data1['player']['stats']['TNTGames']['coins']
            except:
                coins_tnt = 0
            try:
                wins_tnt_tntrun = data1['player']['stats']['TNTGames']['wins_tntrun']
            except:
                wins_tnt_tntrun = 0
            try:
                wins_tnt_pvprun = data1['player']['stats']['TNTGames']['wins_pvprun']
            except:
                wins_tnt_pvprun = 0
            try:
                wins_tnt_tntag = data1['player']['stats']['TNTGames']['wins_tntag']
            except:
                wins_tnt_tntag = 0
            try:
                wins_tnt_bow = data1['player']['stats']['TNTGames']['wins_bowspleef']
            except:
                wins_tnt_bow = 0
            try:
                wins_tnt_wizard = data1['player']['stats']['TNTGames']['wins_capture']
            except:
                wins_tnt_wizard = 0
            try:
                kills_tnt_pvp = data1['player']['stats']['TNTGames']['kills_pvprun']
            except:
                kills_tnt_pvp = 0
            try:
                kills_tnt_tag = data1['player']['stats']['TNTGames']['kills_tntag']
            except:
                kills_tnt_tag = 0
            try:
                kills_tnt_wizard = data1['player']['stats']['TNTGames']['kills_capture']
            except:
                kills_tnt_wizard = 0
            try:
                deaths_tnt_wizard = data1['player']['stats']['TNTGames']['deaths_capture']
            except:
                deaths_tnt_wizard = 0
            try:
                assists_tnt_wizard = data1['player']['stats']['TNTGames']['assists_capture']
            except:
                assists_tnt_wizard = 0
            try:
                record_tnt_tntrun = timeconvert(data1['player']['stats']['TNTGames']['record_tntrun'])
            except:
                record_tnt_tntrun = timeconvert(0)
            try:
                record_tnt_pvprun = timeconvert(data1['player']['stats']['TNTGames']['record_pvprun'])
            except:
                record_tnt_pvprun = timeconvert(0)
            try:
                kd_tnt_wizard = str('%.2f' % (kills_tnt_wizard / deaths_tnt_wizard))
            except:
                kd_tnt_wizard = 0

            output = "%s%s%s%s\n硬币:%s\nTNTRun: 胜场:%s 记录:%s\nPVPRun: 胜场:%s 击杀数:%s 记录:%s\nTNTag: 胜场数:%s 击杀数:%s\nBowspleef: 胜场数:%s\nWizards: 胜场数:%s 助攻数:%s\n击杀数:%s 死亡数:%s K/D:%s" % (
            rank_pro, prefix, rank, name, coins_tnt, wins_tnt_tntrun, record_tnt_tntrun, wins_tnt_pvprun,
            kills_tnt_pvp, record_tnt_pvprun, wins_tnt_tntag, kills_tnt_tag, wins_tnt_bow, wins_tnt_wizard,
            assists_tnt_wizard, kills_tnt_wizard, deaths_tnt_wizard, kd_tnt_wizard)
    except:
        output = '输出缺少变量，请联系开发者!'

    end = datetime.datetime.now()
    used = end - start
    print(used_mojang, used_hyp, used)
    used = '%s秒' % str(used)[5:10]
    output = '%s\n查询用时:%s  by Akashic' % (output, used)

    return output


loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:xxxx", # 填入 httpapi 服务运行的地址
        authKey="INITKEYxxxxxxxx", # 填入 authKey
        account=114514, # 你的机器人的 qq 号
        websocket=True # mirai-api-http中是否开启了websocket,如未开启请改为False
    )
)

@bcc.receiver("GroupMessage")
async def group_message_handler(
    message: MessageChain,
    app: GraiaMiraiApplication,
    group: Group, member: Member
):
    if message.asDisplay().startswith('/'):
        await app.sendGroupMessage(group, MessageChain.create([Plain(hyp(message.asDisplay()))]))



app.launch_blocking()