from graia.ariadne.adapter import DefaultAdapter
from graia.ariadne.app import Ariadne,RelationshipMixin, FileMixin, MultimediaMixin
from graia.ariadne.message.chain import MessageChain
import graia.ariadne.message.element
from graia.ariadne.event.mirai import NudgeEvent,BotInvitedJoinGroupRequestEvent,BotEvent,BotOnlineEvent,BotOfflineEventDropped,BotOfflineEventForce,BotOfflineEventActive
from graia.ariadne.message.element import Plain, At, Quote, Source, Poke, PokeMethods, Voice
from graia.ariadne.message.element import Image as IMAGE
from graia.ariadne.model import Friend, MiraiSession, Group, Member
from graia.broadcast import Broadcast
from graia.ariadne.entry import *
import asyncio
import base64
import datetime
import json
import logging
import math
import os
import platform
import random
import re
import socket
import string
import struct
import sys
import threading
import time
from logging import handlers
from time import gmtime, strftime
import aiohttp
import dns.resolver
import psutil
import requests
from PIL import Image, ImageDraw, ImageFont


logger = logging.getLogger('akashic')
logger.setLevel(level=logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

file_handler = logging.FileHandler('akashic.log')
file_handler.setLevel(level=logging.DEBUG)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

time_rotating_file_handler = handlers.TimedRotatingFileHandler(filename='akashic.log', when='D')
time_rotating_file_handler.setLevel(logging.DEBUG)
time_rotating_file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(time_rotating_file_handler)


# logger.addHandler(stream_handler)


def writelog(level=20, user='Invalid', group='Invalid', input='Invalid', output='Invalid'):


    input = input.replace('\n', '\\n')
    output = output.replace('\n', '\\n')

    message = f'{group} <- {user} -- {input} -> {output}'
    logger.log(level, message)


def getConfig(filename):
    config_dict = {}

    with open(filename, 'r') as config:

        for line in config:
            if line == '\n':
                pass
            else:
                conf = line.replace('\n', '').replace(' ', '').replace('"', '')
                conf_list = conf.split('=')
                # print(conf_list)
                config_dict[conf_list[0]] = conf_list[1]

        for key in config_dict:
            if config_dict[key] in ('True', 'true'):
                config_dict[key] = True
            elif config_dict[key] in ('False', 'false'):
                config_dict[key] = False
            else:
                pass
        for key in config_dict:
            if key == 'Admin_account':
                config_dict[key] = config_dict[key].split(',')
            else:
                pass

        print('Read config file:\n', config_dict)
        return config_dict


TIMESTART = datetime.datetime.now()
config = getConfig(r'config.txt')
VERSION = 'Akashic v0.10.2'
VERSION += '-β'

BOTNAME = config['Bot_name']
OWNER = config['Owner_account']
ADMIN = config['Admin_account']
if OWNER not in ADMIN:
    ADMIN.append(OWNER)
COMMAND = config['Command_prefix']
HYPAPIKEY = config['Hypixel_apiKey']
FONT = config['Font_file']
global LUCK
LUCK = {'update_time': int(time.time())}


def string_to_image(string, font_file=FONT, font_size=20, font_color=(240, 255, 255), background_color=(80, 80, 80),
                    file_name="test.png"):
    """
    将字符串转换为图片
    :param string: 字符串
    :param font_size: 字体大小
    :param font_color: 字体颜色
    :param background_color: 背景颜色
    :return: 图片
    """

    max_length = max([len(i) for i in string.split('\n')])
    width = int(math.ceil(max_length * font_size * 0.8))
    n = string.count('\n')
    image = Image.new("RGB", (width, math.floor(n * font_size * 1.3)), background_color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_file, font_size)
    draw.text((0, 0), string, font=font, fill=font_color)

    image.save(file_name)
    return image


async def hyp(text, user, group=['None','None']):
    time_now = datetime.datetime.now()
    user_id = user[0]
    user = f'{user[1]}[{user[0]}]'
    group = f'{group[1]}[{group[0]}]'
    text_input = text

    EXPAND = 1024 * 1024
    key = HYPAPIKEY
    start = datetime.datetime.now()
    timeout_hyp = aiohttp.ClientTimeout(total=5)

    '''---------------------------------------------COMMAND_LIST---------------------------------------------'''
    command_help = (f'{COMMAND}HELP', f'{COMMAND}帮助')
    command_hyp = (f'{COMMAND}HYPIXEL', f'{COMMAND}HYP', f'{COMMAND}查', f'{COMMAND}查询', f'{COMMAND}信息')
    command_sw = (f'{COMMAND}SW', f'{COMMAND}SKYWARS', f'{COMMAND}空岛', f'{COMMAND}空岛战争')
    command_bw = (f'{COMMAND}BW', f'{COMMAND}BEDWARS' f'{COMMAND}起床', f'{COMMAND}起床战争')
    command_mw = (f'{COMMAND}MW', f'{COMMAND}MEGAWALLS', f'{COMMAND}超战', f'{COMMAND}超级战墙')
    command_uhc = (f'{COMMAND}UHC', f'{COMMAND}极限生存', f'{COMMAND}极限生存冠军')
    command_duel = (f'{COMMAND}DUEL', f'{COMMAND}DUELS', f'{COMMAND}决斗', f'{COMMAND}决斗游戏')
    command_bsg = (
    f'{COMMAND}BSG', f'{COMMAND}HG', f'{COMMAND}HUNGERGAMES', f'{COMMAND}饥饿游戏', f'{COMMAND}闪电饥饿游戏', f'{COMMAND}饥饿')
    command_hg = (f'{COMMAND}MM', f'{COMMAND}MURDER', f'{COMMAND}密室', f'{COMMAND}密室杀手')
    command_tnt = (f'{COMMAND}TNT', 'TNTGAMES')
    command_ban = (f'{COMMAND}BAN', f'{COMMAND}BANNED', f'{COMMAND}封禁')
    command_guild = (f'{COMMAND}GUILD', f'{COMMAND}公会')
    command_parkour = (f'{COMMAND}PARKOUR', f'{COMMAND}跑酷')

    command_list_hypixel = command_parkour + command_help + command_hyp + command_sw + command_bw + command_mw + command_uhc + command_duel + command_bsg + command_hg + command_tnt + command_ban + command_guild

    command_list_namehistory = (f'{COMMAND}NAME', f'{COMMAND}HISTORY', f'{COMMAND}HISTORYNAME', f'{COMMAND}NAMEHISTORY', f'{COMMAND}MC', f'{COMMAND}MINECRAFT')
    command_list_ping = (f'{COMMAND}PING', f'{COMMAND}SfERVER', f'{COMMAND}MCPING', f'{COMMAND}查服')
    command_list_api = (f'{COMMAND}API', f'{COMMAND}APISTATS')
    command_list_status = (f'{COMMAND}.STATUS', f'{COMMAND}SERVERSTATUS')
    command_list_luck = (f'{COMMAND}LUCK', f'{COMMAND}FORTUNE', f'{COMMAND}运气')
    command_list_random = (f'{COMMAND}RANDOM', f'{COMMAND}随机', f'{COMMAND}随机数')
    command_list_randomstr = (f'{COMMAND}RANDOMSTR', f'{COMMAND}STR', f'{COMMAND}随机字符串', f'{COMMAND}随机字符')
    command_list_syuulb = (f'{COMMAND}SYUULB', f'{COMMAND}SYUU', f'{COMMAND}SYUULEADERBOARD')
    command_list_syuu = (f'{COMMAND}SYUU', f'{COMMAND}SYUUPLAYER')
    command_list_send = (f'{COMMAND}ECHO', f'{COMMAND}SEND')
    command_list_friend = (f'{COMMAND}FRIEND', f'{COMMAND}FL')
    command_list_group = (f'{COMMAND}GROUP', f'{COMMAND}GL')
    command_list_test = (f'{COMMAND}TEST')

    def intformat(list):
        output_list = []

        for i in list:
            if r'^*&$#' in str(i):
                i = str.replace(i, r'^*&$#', '')
                output_list.append(i)
            else:
                if type(i) == float:
                    i = str(i)
                    output_list.append(i)
                else:
                    try:
                        i = int(i)
                        i = format(i, ',d')
                        output_list.append(i)
                    except:
                        output_list.append(i)
        return tuple(output_list)

    def system_rate():
        ''' 内存与CPU使用率 '''
        mem = psutil.virtual_memory()
        # 本机内存的占用率
        memory = '内存占用率: ' + str(psutil.virtual_memory().percent) + '%'
        mem_str = "内存使用量: " + str(round(mem.used / EXPAND, 2)) + "MB/"
        mem_str += str(round(mem.total / EXPAND, 2)) + "MB"

        # 本机cpu的总占用率
        cpu = 'CPU占用率: ' + str(psutil.cpu_percent(0)) + '%'
        output = '当前资源占用情况:\n' + cpu + '\n' + memory + '\n' + mem_str
        return output

    def serverGet(text):

        def formhandle(string):
            for color in (
                    '§0', '§1', '§2', '§3', '§4', '§5', '§6', '§7', '§8', '§9', '§a', '§b', '§c', '§d', '§e', '§f',
                    '§k',
                    '§l', '§m',
                    '§n', '§o', '§r'):
                string = string.replace(color, '')
            sentense = string.split('\n')
            string_2 = ''
            for i in sentense:
                string_1 = i.strip(' ')
                string_2 = '%s%s\n' % (string_2, string_1)
            string_2 = string_2.rstrip()
            return string_2

        def ping(ip, port=25565):

            def read_var_int():
                i = 0
                j = 0
                while True:
                    k = sock.recv(1)
                    if not k:
                        return 0
                    k = k[0]
                    i |= (k & 0x7f) << (j * 7)
                    j += 1
                    if j > 5:
                        raise ValueError('var_int too big')
                    if not (k & 0x80):
                        return i

            socket.setdefaulttimeout(2)
            sock = socket.socket()
            time = datetime.datetime.now()
            sock.connect((ip, port))
            time2 = datetime.datetime.now()
            used = '%sms' % int(float(str(time2 - time)[6:11]) * 1000)
            try:
                host = ip.encode('utf-8')
                data = b''  # wiki.vg/Server_List_Ping
                data += b'\x00'  # packet ID
                data += b'\x04'  # protocol variant
                data += struct.pack('>b', len(host)) + host
                data += struct.pack('>H', port)
                data += b'\x01'  # next state
                data = struct.pack('>b', len(data)) + data
                sock.sendall(data + b'\x01\x00')  # handshake + status ping
                length = read_var_int()  # full packet length
                if length < 10:
                    if length < 0:
                        raise ValueError('negative length read')
                    else:
                        raise ValueError('invalid response %s' % sock.read(length))

                sock.recv(1)  # packet type, 0 for pings
                length = read_var_int()  # string length
                data = b''
                while len(data) != length:
                    chunk = sock.recv(length - len(data))
                    if not chunk:
                        raise ValueError('connection abborted')

                    data += chunk
                data_json = json.loads(data)
                version = data_json['version']['name']
                protocol = data_json['version']['protocol']
                player_max = data_json['players']['max']
                player_online = data_json['players']['online']
                try:
                    description = formhandle(data_json['description'])
                except:
                    url = 'https://mcapi.us/server/status?ip=%s' % ip
                    description = requests.get(url).json()['motd']
                    description = formhandle(description)
                try:
                    type = data_json['modinfo']['type']
                except:
                    type = 'NaN'
                try:
                    modList = data_json['modinfo']['modlist']
                except:
                    modList = 'NaN'
                icon = data_json['favicon'][22:]
                icon = base64.b64decode(icon)
                file = open('1.png', 'wb')
                file.write(icon)

                output = '[源ip]%s:%s\n[描述]%s\n[版本]%s(%s)\n[人数]%s/%s\n[延迟]%s\n[类型]%s\n[mod]%s' % (
                    ip, port, description, version, protocol, player_online, player_max, used, type, modList)

                return output
            finally:
                sock.close()

        def srv(domain):

            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['223.5.5.5']
            resolver.lifetime = 6
            srvInfo = {}
            try:
                time_1 = datetime.datetime.now()
                srv_records = resolver.query('_minecraft._tcp.' + domain, 'SRV')
                time_2 = datetime.datetime.now()
                print(time_2 - time_1)
                for srv1 in srv_records:
                    srvInfo['host'] = str(srv1.target).rstrip('.')
                    srvInfo['port'] = srv1.port
                    # srvInfo['weight'] = srv1.weight
                    # srvInfo['priority'] = srv1.priority
                print(srvInfo)
                return srvInfo
            except:
                return None

        try:
            input = str.split(text)[0]
            print(input)
        except:
            output = ''
            return output
        time_1 = datetime.datetime.now()
        try:
            try:
                output = ping(input)
            except:

                address = srv(input)
                ip = address['host']
                port = address['port']
                print(ip, port)
                output = ping(ip, port)
        except:
            output = '获取失败或服务器不存在!'

        time_2 = datetime.datetime.now()
        used = time_2 - time_1
        used = '%s秒' % str(used)[5:10]
        output = '%s\n查询用时:%s  by Akashic' % (output, used)
        return output

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
        string = str(string)
        for color in (
        '§0', '§1', '§2', '§3', '§4', '§5', '§6', '§7', '§8', '§9', '§a', '§b', '§c', '§d', '§e', '§f', '§k', '§l',
        '§m', '§n', '§o', '§r'):
            string = string.replace(color, '')
        return string

    def formhandlerSW(string):
        string = str(string)
        string_output = ''
        for color in (
        '§0', '§1', '§2', '§3', '§4', '§5', '§6', '§7', '§8', '§9', '§a', '§b', '§c', '§d', '§e', '§f', '§k', '§l',
        '§m', '§n', '§o', '§r'):
            string = string.replace(color, '')
        print(string)
        # for string_1 in string:
        #     print(string_1)
        #     if string_1 not in ('1','2','3','4','5','6','7','8','9','0'):
        #         string_1 = ''
        #     else:
        #         pass
        #     string_output = '%s%s' % (string_output,string_1)
        return string

    def quotient(dividend, divisor):
        try:
            quotient = dividend / divisor
            quotient = '%.2f' % quotient
            quotient = float(quotient)
        except:
            quotient = 0
        return quotient

    def quotient_json(json, key_list, root_1='NaN', root_2='NaN', root_3='NaN', root_4='NaN'):
        root_1, root_2, root_3, root_4 = str(root_1), str(root_2), str(root_3), str(root_4)
        try:
            if root_4 != 'NaN' and root_3 != 'NaN' and root_2 != 'NaN' and root_1 != 'NaN':
                data = json['%s' % root_1]['%s' % root_2]['%s' % root_3]['%s' % root_4]
            elif root_3 != 'NaN' and root_2 != 'NaN' and root_1 != 'NaN':
                data = json['%s' % root_1]['%s' % root_2]['%s' % root_3]
            elif root_2 != 'NaN' and root_1 != 'NaN':
                data = json['%s' % root_1]['%s' % root_2]
            elif root_1 != 'NaN':
                data = json['%s' % root_1]
            else:
                pass
        except:
            pass
        output_list = []
        for key in key_list:
            try:
                result = data['%s' % key]
            except:
                result = 0
            output_list.append(result)

        dividend = output_list[0]
        divisor = output_list[1]

        try:
            quotient = dividend / divisor
            quotient = '%.2f' % quotient
            quotient = float(quotient)
        except:
            quotient = 0
        return quotient

    def getintdata(json, game, object):
        try:
            data = json['player']['stats']['%s' % game]['%s' % object]
        except:
            data = 0
        return data

    def translate_game(text):
        translate_dic = {'QUAKECRAFT': '未来射击', 'WALLS3': '超级战墙', 'WALLS': '战墙', 'PAINTBALL': '彩弹射击',
                         'SURVIVAL_GAMES': '闪电饥饿游戏', 'TNTGAMES': '掘战游戏', 'VAMPIREZ': '吸血鬼', 'WALLS3': '超级战墙',
                         'ARCADE': '街机游戏', 'ARENA': '竞技场', 'UHC': '极限生存冠军', 'MCGO': '警匪大战', 'BATTLEGROUND': '战争领主',
                         'SUPER_SMASH': '星碎英雄', 'GINGERBREAD': '方块赛车', 'HOUSING': '家园世界', 'SKYWARS': '空岛战争',
                         'TRUE_COMBAT': '疯狂战墙', 'SPEED_UHC': '速战极限生存', 'SKYCLASH': '空岛竞技场', 'LEGACY': '经典游戏',
                         'PROTOTYPE': '游戏实验室', 'BEDWARS': '起床战争', 'MURDER_MYSTERY': '密室杀手', 'BUILD_BATTLE': '建筑大师',
                         'DUELS': '决斗游戏', 'SKYBLOCK': '空岛生存', 'PIT': '天坑乱斗', 'REPLAY': '回放系统', 'SMP': 'Hypixel SMP',
                         'MAIN': '主城'}
        for word in translate_dic.keys():
            text = text.replace(word, translate_dic[word])
        return text

    def translate_mode(text):
        translate_dic = {'LOBBY': '大厅', 'ctf_mini': '夺旗模式', 'domination': '抢点战模式', 'team_deathmatch': '团队死亡竞赛模式',
                         'standard': '标准模式', 'face_off': '对决模式', 'solo_normal': '单挑模式', 'teams_normal': '团队模式',
                         '2v2_normal': ' 2v2 模式', 'teams_normal': ' 2v2v2 模式', '1v1_normal': ' 1v1 模式',
                         'friends_normal': ' Friends 1v1v1v1 模式', 'dynamic': '私人岛屿', 'hub': '主岛屿', 'farming_1': '农场岛屿',
                         'combat_1': '蜘蛛巢穴', 'combat_2': '烈焰堡垒', 'combat_3': '末地', 'mining_1': '黄金矿区',
                         'mining_2': '深层矿洞', 'mining_3': ' Dwarven Mine ', 'mining_4': ' Crystal Hollows ',
                         'foraging_1': '公园', 'dungeon_hub': '地牢大厅', 'dungeon': '地牢', 'ranked_normal': '排位模式',
                         'solo_normal': '单挑普通模式', 'solo_insane': '单挑疯狂模式', 'teams_normal': '双人普通模式',
                         'teams_insane': '双人疯狂模式', 'mega_normal': ' 超级普通模式', 'mega_doubles': '超级 Doubles 模式',
                         'solo_insane_tnt_madness': '单挑疯狂 TNT 模式', 'teams_insane_tnt_madness': '双人疯狂 TNT 模式',
                         'solo rush': '单挑疾速模式', 'teams_insane_rush': '双人疾速模式', 'solo_insane_slime': '单挑史莱姆模式',
                         'teams_insane_slime': '双人史莱姆模式', 'solo_insane_lucky': '单挑幸运方块模式',
                         'teams_insane_lucky': '双人幸运方块模式', 'solo_insane_hunters_vs_beasts': '狩猎对决模式', 'TNTRUN': '方块掘战',
                         'PVPRUN': 'PVP 方块掘战', 'BOWSPLEEF': '掘一死箭', 'TNTAG': '烫手 TNT ', 'CAPTURE': '法师掘战',
                         'BEDWARS_EIGHT_ONE': '单挑模式', 'BEDWARS_EIGHT_TWO': '双人模式', 'BEDWARS_FOUR_THREE': ' 3v3v3v3 模式',
                         'BEDWARS_FOUR_FOUR': ' 4v4v4v4 模式', 'BEDWARS_CAPTURE': '据点模式',
                         'BEDWARS_EIGHT_TWO_RUSH': '双人疾速模式', 'BEDWARS_FOUR_FOUR_RUSH': ' 4v4v4v4 疾速模式',
                         'BEDWARS_EIGHT_TWO_ULTIMATE': '双人超能力模式', 'BEDWARS_FOUR_FOUR_ULTIMATE': ' 4v4v4v4 超能力模式',
                         'BEDWARS_CASTLE': '40v40城池攻防战模式', 'BEDWARS_TWO_FOUR': '4V4 模式',
                         'BEDWARS_EIGHT_TWO_VOIDLESS': '双人无虚空模式', 'BEDWARS_FOUR_FOUR_VOIDLESS': ' 4v4v4v4 无虚空模式',
                         'BEDWARS_EIGHT_TWO_ARMED': '双人枪械模式', 'BEDWARS_FOUR_FOUR_ARMED': ' 4v4v4v4 枪械模式',
                         'BEDWARS_EIGHT TWO_LUCKY': '双人幸运方块模式', 'BEDWARS_FOUR_FOUR_LUCKY': ' 4v4v4v4 幸运方块模式',
                         'BEDWARS_PRACTICE': '练习模式', 'HOLE_IN_THE_WALL': '人体打印机', 'SOCCER': '足球',
                         'BOUNTY_HUNTERS': '赏金猎人', 'PIXEL_PAINTERS': '像素画师', 'DRAGON_WARS': '龙之战',
                         'ENDER_SPLEEF': '末影掘战', 'STARWARS': '星际战争', 'THROW_OUT': '乱棍之战', 'DEFENDER': '进击的苦力怕',
                         'PARTY_GAMES_1': '派对游戏', 'FARM_HUNT': '农场躲猫猫', 'ZOMBIES_DEAD_END': '僵尸末日',
                         'ZOMBIES_BAD_BLOOD': '僵尸末日', 'ZOMBIES_ALIEN_ARCADIUM': '僵尸末日',
                         'HIDE_AND_SEEK_PROP_HUNT': '道具躲猫猫', 'HIDE_AND_SEEK_PARTY_POOPER': '派对躲猫猫',
                         'SIMON_SAYS': '我说你做', 'SANTA_SAYS': '圣诞老人说你做', 'MINI_WALLS': '迷你战墙', 'DAYONE': '行尸走肉',
                         'PVP_CTW': '捕捉羊毛大作战', 'normal': '爆破模式', 'deathmatch': '团队死亡竞赛模式',
                         'NORMAL_PARTY': '挑战模式 - 爆破模式', 'DEATHMATCH_PARTY': '挑战模式 - 团队死亡竞赛模式',
                         'BUILD_BATTLE_SOLO_NORMAL': '单人模式', 'BUILD_BATTLE_TEAMS_NORMAL': '团队模式',
                         'BUILD_BATTLE_SOLO_PRO': '高手模式', 'BUILD_BATTLE_GUESS_THE_BUILD': '建筑猜猜乐',
                         'DUELS_CLASSIC_DUEL': '经典决斗', 'DUELS_SW_DUEL': '空岛战争决斗', 'DUELS_SW_DOUBLES': '空岛战争决斗双人决斗',
                         'DUELS_BOW_DUEL': '弓箭决斗', 'DUELS_UHC_DUEL': '极限生存决斗', 'DUELS_UHC_DOUBLES': '极限生存冠军双人决斗',
                         'DUELS_UHC_FOUR': '极限生存冠军四人决斗', 'DUELS_UHC_MEETUP': '极限生存冠军死亡竞赛决斗',
                         'DUELS_POTION_DUEL': '药水决斗', 'DUELS_COMBO_DUEL': '连击决斗', 'DUELS_OP_DUEL': '高手决斗',
                         'DUELS_OP_DOUBLES': '高手双人决斗', 'DUELS_MW_DUEL': '超级战墙决斗', 'DUELS_MW_DOUBLES': '超级战墙双人决斗',
                         'DUELS_SUMO_DUEL': '相扑决斗', 'DUELS_BLITZ_DUEL': '商店街游戏决斗', 'DUELS_BOWSPLEEF_DUEL': '掘一死箭决斗',
                         'DUELS_BRIDGE_DUEL': '战桥决斗', 'DUELS_BRIDGE_DOUBLES': '战桥双人决斗', 'DUELS_BRIDGE_FOUR': '战桥四人决斗',
                         'DUELS_BRIDGE_2V2V2V2': '战桥 2v2v2v2 决斗', 'DUELS_BRIDGE_3V3V3V3': '战桥 4v4v4v4 决斗',
                         'MURDER_CLASSIC': '经典模式', 'MURDER_DOUBLE_UP': '双倍模式', 'MURDER_ASSASSINS': '刺客模式',
                         'MURDER_INFECTION': '感染模式', 'TOWERWARS_SOLO': '单挑模式', 'TOWERWARS_TEAM_OF_TWO': '双人模式',
                         'SOLO': '单挑模式', 'TEAMS': '组队模式', 'EVENTS': '活动模式'}
        for word in translate_dic.keys():
            text = text.replace(word, translate_dic[word])
        return text

    def translate_map(text):
        translate_dic = {'DeadEnd': '穷途末路', 'BadBlood': '坏血之宫', 'AlienArcadium': '外星游乐园', 'Amazon': '亚马逊雨林',
                         'Waterfall': '瀑布', 'Airshow': '热气球展览会', 'Aquarium': '水族馆', 'Archway': '拱形廊道', 'Ashore': '海滩',
                         'Boletum': '蘑菇岛', 'Chained': '铁索连环', 'Crypt': '地窖', 'Eastwood': '东方客栈', 'Glacier': '冰天雪地',
                         'Hollow': '中空岛屿', 'Invasion': '全盘入侵', 'Lectus': '罗马竞技场', 'Lighthouse': '灯塔', 'Lotus': '莲花岛',
                         'Pernicious': '不毛之地', 'Playground': '游乐场', 'Rooftop': '屋顶', 'Speedway': '赛道',
                         'Stonekeep': '石砖要塞', 'Swashbuckle': '海盗船', 'Treenan': '参天松树', 'IvoryCastle': '象牙城池',
                         'Cauldron': '炼药锅', 'Nomad': '流浪之地', 'Memorial': '纪念碑岛', 'Palette': '调色世界', 'Winterhelm': '冰盔岛',
                         'Villa': '别墅之岛', 'Chronos': '车轮之环', 'Mothership': '航空母舰', 'Oasis': '绿洲之岛', 'Onionring': '洋葱圈岛',
                         'Aegis': '盾之神殿', 'AgniTemple': '阿格尼神庙', 'Anchored': '水底之境', 'Aquarius': '水瓶座圣殿',
                         'Aqueduct': '运河大桥', 'ArxCitadel': '阿克斯城堡', 'Clearing': '荒野木屋', 'Coherence': '林间',
                         'Crumble': '崩溃之地', 'DessertedIslands': '甜点之岛', 'DwarfFortress': '矮人堡垒', 'Dwarven': '十字交叉',
                         'Dynasty': '落樱亭台', 'Eden': '伊甸园', 'Eirene': '穹顶', 'Elven': '巨城', 'ElvenTowers': '精灵巨城',
                         'Entangled': '金矿遗迹', 'Equinox': '四季秘境', 'FirelinkShrine': '遗迹之城', 'Frostbite': '冰封之岛',
                         'Fortress': '要塞', 'Fossil': '树海秘境', 'Foundation': '建筑工地', 'Fungi': '蘑菇岛', 'Hontori': '樱扬桥亭',
                         'Humidity': '荒漠', 'Jinzhou': '樱花岛屿', 'LongIsland': '狭长岛屿', 'Maereen': '金字塔',
                         'Magnolite': '熔岩巨山', 'Marooned': '放逐之地', 'Martian': '火星基地', 'MegaShire': '希雷', 'Meteor': '流星',
                         'Onionring2': '洋葱环v2', 'Onset': '角斗场', 'Overfall': '高地之湖', 'Pitfall': '中空岛屿', 'Plateau': '高原',
                         'Railroad': '铁路', 'Reef': '暗礁之地', 'Rocky': '乱石崚峋', 'Sanctuary': '圣所', 'Sanctum': '圣地',
                         'Sandbox': '沙盒', 'Sawmill': '锯木厂', 'Siege': '浮空城', 'Sentinel': '前哨基地', 'Shire': '营地',
                         'Shrooms': '蘑菇之境', 'Skychurch': '天空教堂', 'Strata': '升空之岛', 'Submerged': '深海秘境', 'Templar': '圣堂',
                         'Towers': '塔楼基地', 'Tribal': '林间树屋', 'Tribute': '决战之岩', 'Tundra': '苔原', 'FrostBound': '冰霜巨城',
                         'TwistedGrove': '环合密林', 'AncientTomb': '古墓', 'Towerfall': '高坠塔', 'Transport': '运输塔',
                         'Archives': '档案馆', 'HypixelWorld': 'Hypixel游乐园', 'Headquarters': '总部', 'Library': '图书馆',
                         'GoldRush': '淘金热', 'CruiseShip': '游轮', 'Hollywood': '好莱坞', 'ArchivesTopFloor': '档案馆顶层',
                         'Widow\'sDen': '寡妇的书房', 'Aquarium': '水族馆', 'Snowglobe': '雪景球', 'TheBridge': '战桥',
                         'Arena': '竞技场', 'Sumo': '相扑', 'Aquatica': '水生', 'Thornhill': '生灵之山', 'TheRift': '征召峡谷',
                         'Stormwind': '风暴之境', 'Scorched': '暗黑圣地', 'Ruins': '遗弃古堡', 'Neolithic': '大漠之丘', 'Gorge': '雪原城池',
                         'FalstadGate': '石城之门', 'DorivenBasin': '荒郊盆地', 'DeathValley': '死亡山谷', 'Crossfire': '交火王城',
                         'BlackTemple': '黑岩神寺', 'AtherroughValley': '神魔之城', 'Arches': '失落山谷', 'Arathi': '远郊乡村'}
        for word in translate_dic.keys():
            text = text.replace(word, translate_dic[word])
        return text

    def fillin(text, list):
        for i in list:
            text = text.replace('%a', str(i), 1)
        return text

    def jsonhandler(json, key_list, output_str='NaN', root_1='NaN', root_2='NaN', root_3='NaN', root_4='NaN'):

        try:
            if root_4 != 'NaN' and root_3 != 'NaN' and root_2 != 'NaN' and root_1 != 'NaN':
                data = json['%s' % root_1]['%s' % root_2]['%s' % root_3]['%s' % root_4]
            elif root_3 != 'NaN' and root_2 != 'NaN' and root_1 != 'NaN':
                data = json['%s' % root_1]['%s' % root_2]['%s' % root_3]
            elif root_2 != 'NaN' and root_1 != 'NaN':
                data = json['%s' % root_1]['%s' % root_2]
            elif root_1 != 'NaN':
                data = json['%s' % root_1]
            else:
                pass
        except:
            pass

        output_list = []
        for key in key_list:
            try:
                result = data['%s' % key]
            except:
                result = 0
            output_list.append(result)

        if output_str == 'NaN':
            return output_list
        else:
            try:
                for value in output_list:
                    output_str = output_str.replace('%s', str(value), 1)
                return output_str
            except:
                return None


    input = str(text)
    error = 'Invalid'

    mode_input = str(len(str.split(input)))
    command = str.upper(str.split(input)[0])
    if mode_input == '1':
        if command in command_help:
            name = 'help'
            output = f'指令列表\nmc查服-{COMMAND}ping <ip/addr>\nhyp基本信息-{COMMAND}hyp <player>\n空岛战争-{COMMAND}sw <player>\n起床战争-{COMMAND}bw <player>\n超级战墙-{COMMAND}mw <player>\n决斗游戏-{COMMAND}duels <player>\n闪电饥饿游戏-{COMMAND}bsg <player>\nUHC-{COMMAND}uhc <player>\n密室杀手-{COMMAND}mm <player>\nTNT游戏-{COMMAND}tnt <player>\n公会查询-{COMMAND}guild <player>\nsyuu查询-{COMMAND}syuu <player>\nsyuu排行榜-{COMMAND}syuulb'

        elif command in command_list_test:
            # v = await app.uploadVoice(base64.b64decode(open(r"C:\Users\18622\Downloads\arcaea_3.11.0c\assets\songs\aegleseeker\aegleseeker.ogg",'rb').read()))
            await app.sendFriendMessage(3442535256,MessageChain.create([Voice()]))

        elif command in command_list_api:
            if str(user_id) not in ADMIN:
                output = '您没有使用该命令的权限!'
                writelog(30, user, group, input, output)
                return output
            data = requests.get('https://api.hypixel.net/key?key=%s' % key).json()
            if data['success'] is True:
                owner = data['record']['owner']
                limit = data['record']['limit']
                queries = data['record']['queriesInPastMin']
                total = data['record']['totalQueries']
                output = '当前api状态:\napi持有者UUID:%s\n请求数上限:%s\n当前1min内请求数:%s\n总请求数:%s' % intformat(
                    [owner, str(limit), str(queries), str(total)])
            else:
                output = 'api状态获取失败'

        elif command in command_list_luck:
            global LUCK
            update_time = LUCK['update_time']
            now_time = int(time.mktime(time.strptime(datetime.datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")))
            time_difference = now_time - update_time

            if time_difference > 86400:
                LUCK = {'update_time': int(time.time())}

            random_a = random.randint(0, 9)
            random_b = random.choice([0, 10, 20, 20, 30, 30, 40, 40, 40, 50, 50, 50, 50, 60, 60, 60, 70, 70, 80, 90])
            random_c = random_a + random_b
            if random_c == 0:
                random_d = random.randint(1, 10)
                if random_d == 1:
                    random_c = 0
                else:
                    random_c == 100

            if str(user_id) in LUCK:
                random_c = LUCK[str(user_id)]
            else:
                LUCK[str(user_id)] = random_c
                pass
            output = f'您今天打破坚冰的概率为{random_c}%\n*仅供娱乐 by Akashic'
            # print(LUCK)
            return output

        elif command in command_ban:
            url = 'https://api.hypixel.net/punishmentstats?key=%s' % key
            data_ban = requests.get(url).json()
            try:
                watchdog_minute = data_ban['watchdog_lastMinute']
                watchdog_daily = data_ban['watchdog_rollingDaily']
                watchdog_total = data_ban['watchdog_total']
                staff_daily = data_ban['staff_rollingDaily']
                staff_total = data_ban['staff_total']

                output = 'hypixel服务器封禁数据:\nWatchdog近一分钟内封禁:%s\nWatchdog本日封禁:%s\nWatchdog总封禁:%s\nStaff今日封禁:%s\nStaff总封禁:%s' % intformat(
                    [watchdog_minute, watchdog_daily, watchdog_total, staff_daily, staff_total])
                writelog(20, user, group, input, output)

                return output
            except:
                output = 'hypixel服务器封禁数据获取失败!'
                writelog(30, user, group, input, output)

                return output

        elif command in command_list_status:
            if str(user_id) not in ADMIN:
                output = '您没有使用该命令的权限!'
                writelog(30, user, group, input, output)

                return output
            try:
                print(123)
                info_sys = system_rate()
                info_env = platform.platform()
                info_py = platform.python_version()
                time_now = datetime.datetime.now()
                info_time = time_now - TIMESTART
                print(sys.argv[0].split("/")[-1])
                info_update = os.stat(sys.argv[0]).st_mtime
                ModifiedTime = time.localtime(info_update)

                y = time.strftime('%Y', ModifiedTime)
                m = time.strftime('%m', ModifiedTime)
                d = time.strftime('%d', ModifiedTime)
                H = time.strftime('%H', ModifiedTime)
                M = time.strftime('%M', ModifiedTime)
                S = time.strftime('%S', ModifiedTime)

                info_update = '%s-%s-%s %s:%s:%s' % (y, m, d, H, M, S)
                output = 'Bot后端基于:%s\n开发者:hycx233\n最后编译时间:%s\n当前运行时间:%s\n当前运行平台:%s\n当前运行环境:Python%s\n%s' % (
                VERSION, info_update, info_time, info_env, info_py, info_sys)
                writelog(20, user, group, input, output)

                return output
            except Exception as e:
                output = f'获取资源占用情况失败!{e}'
                writelog(30, user, group, input, output)

                print(e)
                return output

        elif command in command_list_friend:
            if str(user_id) not in ADMIN:
                output = '您没有使用该命令的权限!'
                writelog(30, user, group, input, output)
                return output

            friendList = await app.getFriendList()
            friend_str = '好友列表:\n'
            for f in friendList:
                f_id = f.id
                f_name = f.nickname
                friend_str += f'{f_id} - {f_name}\n'
            friend_str += f'好友总数: {str(len(friendList))}'
            print(friend_str)
            output = friend_str

        elif command in command_list_group:
            if str(user_id) not in ADMIN:
                output = '您没有使用该命令的权限!'
                writelog(30, user, group, input, output)
                return output

            groupList = await app.getGroupList()
            group_str = '群聊列表:\n'
            for group1 in groupList:
                g_id = group1.id
                g_name = group1.name
                g_perm = group1.accountPerm
                group_str += f'{g_id} - {g_name}\n'
            group_str += f'已加入群聊总数: {str(len(groupList))}'
            print(group_str)
            output = group_str

        elif command in command_list_syuulb:

            url = 'https://api.syuu.net/public/leader-boards/practice'
            data_syuulb = requests.get(url).json()
            resp = data_syuulb['response']

            gameType_list = ['Sharp2Prot2', 'MCSG', 'OCTC', 'Gapple', 'Archer', 'NoDelay', 'Soup', 'BuildUHC', 'Debuff',
                             'Sharp4Prot3', 'Sumo', 'Axe', 'Spleef', 'FinalUHC', 'Bridge', 'MLGRush', 'Boxing',
                             'Parkour']
            leaderBoard_dict = {}
            leaderBoard_list = []

            for gameType in gameType_list:
                leader_board = resp[gameType]
                leaderBoard_str = '%s的排行榜' % gameType
                place = 0
                for player in leader_board:
                    place += 1
                    name = player['lastknownname']
                    score = player['rankedelo']
                    leaderBoard_str += '\n[%s]%s - %s' % (place, name, score)
                print(leaderBoard_str)
                leaderBoard_dict[gameType] = leaderBoard_str
                leaderBoard_list.append(leaderBoard_str)
            # print(leaderBoard_dict)
            time_cached = '更新时间:'
            time_cached += data_syuulb['cached-at']

            leaderBoard_list.append(time_cached)
            range_list = [(10, 15), (400, 15), (790, 15), (10, 400), (400, 400), (790, 400), (10, 785), (400, 785),
                          (790, 785), (10, 1170), (400, 1170), (790, 1170), (10, 1555), (400, 1555), (790, 1555),
                          (10, 1940), (400, 1940), (790, 1940), (790, 2290)]

            font = ImageFont.truetype(FONT, 25)
            im = Image.new("RGB", (1190, 2340), (80, 80, 80))
            dr = ImageDraw.Draw(im)
            i = -1
            for range_text in range_list:
                i += 1
                text1 = leaderBoard_list[i]
                dr.text(range_text, text1, font=font, fill="#F0FFFF")
            # dr.text((x_max+5,15),text2,font=font,fill="#F0FFFF")
            # im.show()
            im.save('syuu.png')
            with open('syuu.png', 'rb') as f:
                base64_data = base64.b64encode(f.read())
                output = str(base64_data)

            writelog(20, user, group, input, output)
            return None

        else:
            output = '未知指令!'
            writelog(30, user, group, input, output)
            return '无需发送'

        writelog(20, user, group, input, output)

        return output


    elif mode_input == '2' and command in command_list_namehistory:
        try:
            player = str.split(input)[1]
            url1 = 'https://api.mojang.com/users/profiles/minecraft/%s' % player
            data_player = requests.get(url1).json()
            uuid = data_player['id']
            url2 = 'https://api.mojang.com/user/profiles/%s/names' % uuid
            data_history = requests.get(url2).json()
            num_name = len(data_history)
            if num_name == 1:
                name_only = data_history[0]
                name_only = name_only['name']
                str_history = '该玩家无更名记录,当前名称为%s\nUUID:%s' % (name_only, uuid)
            else:
                change_times = num_name - 1
                str_history = '该玩家共有%s次更名记录\n' % change_times
                i = 0
                for data in reversed(data_history):
                    i += 1
                    x = i - 1
                    name = data['name']
                    try:
                        changed_time = data['changedToAt']
                        changed_time = timeStamp(changed_time)
                    except:
                        pass
                    if i == num_name:
                        str_history = '%s\n初始名称:%s\nUUID:%s' % (str_history, name, uuid)
                        break
                    if i == 1:
                        str_history = '%s当前名称:%s - %s' % (str_history, name, changed_time)
                    else:
                        str_history = '%s\n[%s]%s - %s' % (str_history, x, name, changed_time)

            output = str_history
            writelog(20, user, group, input, output)
            return output
        except:
            output = '玩家名有误或查询错误，请尝试输入玩家当前名称!'
            writelog(30, user, group, input, output)
            return output


    elif mode_input == '2' and command in command_list_ping:
        try:
            print(input)
            output = serverGet(str.split(input)[1])
            print(output)
            if output.startswith('*'):
                writelog(30, user, group, input, output)
                return '无需发送'

            writelog(20, user, group, input, output)
            return output
        except:
            output = '服务器信息获取失败!'
            writelog(30, user, group, input, output)
            return '无需发送'


    elif mode_input == '2' and command in command_list_syuu:
        try:
            player = str.split(input)[1]
            url1 = 'https://api.mojang.com/users/profiles/minecraft/%s' % player
            data_player = requests.get(url1).json()
            name = data_player['name']
            uuid = data_player['id']
            uuid = '%s-%s-%s-%s-%s' % (uuid[0:8], uuid[8:12], uuid[12:16], uuid[16:20], uuid[20:])
            url = 'https://www.syuu.net/user/%s' % uuid
            resp = requests.get(url).text
        except:
            output = '玩家不存在或该玩家无数据'
            writelog(30, user, group, input, output)
            return output

        par = re.compile(r'[0-9]{4}/[0-9]{2}/[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}')
        par_2 = re.compile(r'<td class="text-left">\d+<a /></td>')
        par_3 = re.compile(r'\d+')
        par_4 = re.compile(r'(?<=<h1>).*?(?=\n)')
        par_5 = re.compile(r'(?<=<td class="text-left">).*?(?=</td>\n)')

        gameType_list = ['Sharp2Prot2', 'MCSG', 'OCTC', 'Gapple', 'Archer', 'NoDelay', 'Soup', 'BuildUHC', 'Debuff',
                         'Sharp4Prot3', 'Sumo', 'Axe', 'Spleef', 'FinalUHC', 'Bridge', 'MLGRush', 'Boxing', 'Parkour']

        time_syuu_list = par.findall(resp)
        data_syuu_list = par_2.findall(resp)
        name_player = par_4.findall(resp)[0]
        games_syuu_list = par_5.findall(resp)
        games_syuu_list2 = []
        data_syuu1 = []
        text = ''
        i = 0

        for games in games_syuu_list:
            if games in gameType_list:
                games_syuu_list2.append(games)
            else:
                pass

        for x in data_syuu_list:
            a = par_3.findall(x)[0]
            data_syuu1.append(a)

        for types in games_syuu_list2:
            i += 1
            text += '[%s] Elo:%s 胜场:%s 败场:%s\n' % (
                types, data_syuu1[3 * i - 3], data_syuu1[3 * i - 2], data_syuu1[3 * i - 1])
        if text == '':
            text = '该玩家无Rank数据'
        try:
            firstlogin = time_syuu_list[0]
        except:
            firstlogin = 'Invalid'
        try:
            lastlogin = time_syuu_list[1]
        except:
            lastlogin = 'Invalid'
        data_syuu = [name, firstlogin, lastlogin, text]

        output = '%s的Syuu(Rank)数据:\n首次登入时间:%s\n最后登入时间:%s\n%s' % tuple(data_syuu)
        writelog(20, user, group, input, output)
        return output


    elif mode_input == '2' and command in command_list_hypixel:

        player = str.split(input)[1]
        # url = 'https://api.mojang.com/users/profiles/minecraft/%s' % (player)
        # start_mojang = datetime.datetime.now()

        try:
            # uuiddata = requests.get(url).json()

            async def uuidGet(player):
                while True:
                    url = 'https://api.mojang.com/users/profiles/minecraft/%s' % player
                    async with aiohttp.ClientSession(timeout=3) as session:
                        try:
                            async with session.get(url, timeout=3) as resp:
                                data = await resp.json()
                                print('success_uuid_get')
                                return data
                        except:
                            async with session.get(url, timeout=3) as resp:
                                data = await resp.json()
                                print('success_uuid_get_retry')
                                return data
            uuiddata = await uuidGet(player)
            uuid = uuiddata['id']
            # print(uuid)


            # end_mojang = datetime.datetime.now()
            # used_mojang = end_mojang - start_mojang

            # url = 'https://crafatar.com/renders/head/%s?size=512&overlay' % uuid
            # resp = requests.get(url)
            # print(resp)
            # with open('player.png', 'wb') as f:
            #     f.write(resp.content)

        except:
            output = '玩家未找到!'
            writelog(30, user, group, input, output)
            return output

        start_hyp = datetime.datetime.now()


        async def game_stats_get(uuid, key):
            while True:
                url = 'https://api.hypixel.net/player?key=%s&uuid=%s' % (key, uuid)
                async with aiohttp.ClientSession(timeout=timeout_hyp) as session:
                    try:
                        async with session.get(url, timeout=timeout_hyp) as resp:
                            data = await resp.json()
                            print('success_game_stats_get')
                            return data
                    except:
                        async with session.get(url, timeout=timeout_hyp) as resp:
                            data = await resp.json()
                            print('success_game_stats_get_retry')
                            return data


        async def online_stats_get(uuid, key):
            while True:
                url = 'https://api.hypixel.net/status?key=%s&uuid=%s' % (key, uuid)
                async with aiohttp.ClientSession(timeout=timeout_hyp) as session:
                    try:
                        async with session.get(url, timeout=timeout_hyp) as resp:
                            data = await resp.json()
                            print('success_online_stats_get')
                            return data
                    except:
                        async with session.get(url, timeout=timeout_hyp) as resp:
                            data = await resp.json()
                            print('success_online_stats_get_retry')
                            return data


        async def rsw_stats_get(uuid, key):
            while True:
                url = 'https://api.hypixel.net/player/ranked/skywars?key=%s&uuid=%s' % (key, uuid)
                async with aiohttp.ClientSession(timeout=timeout_hyp) as session:
                    try:
                        async with session.get(url, timeout=timeout_hyp) as resp:
                            data = await resp.json()
                            print('success_rsw_stats_get')
                            return data
                    except:
                        async with session.get(url, timeout=timeout_hyp) as resp:
                            data = await resp.json()
                            print('success_rsw_stats_get_retry')
                            return data


        async def guild(uuid, key):
            while True:
                url = 'https://api.hypixel.net/guild?key=%s&player=%s' % (key, uuid)
                async with aiohttp.ClientSession(timeout=timeout_hyp) as session:
                    try:
                        async with session.get(url, timeout=timeout_hyp) as resp:
                            data = await resp.json()
                            print('success_guild')
                            return data
                    except:
                        async with session.get(url, timeout=timeout_hyp) as resp:
                            data = await resp.json()
                            print('success_guild_retry')
                            return data

            # async def pic(uuid):
            #     while True:
            #         url = 'https://crafatar.com/renders/head/%s' % (uuid)
            #         async with aiohttp.ClientSession(timeout=timeout_hyp) as session:
            #             try:
            #                 async with session.get(url,timeout=timeout_hyp) as resp:
            #                     data = await resp.read()
            #                     with open('player.png', 'wb') as p:
            #                         p.write(data)
            #                         print('success_pic',url)
            #                         return None
            #             except:
            #                 async with session.get(url,timeout=timeout_hyp) as resp:
            #                     data = await resp.read()
            #                     with open('player.png', 'wb') as p:
            #                         p.write(data)
            #                         print('success_pic_retry')
            #                         return None

        if command in command_hyp:

            result = await asyncio.gather(game_stats_get(uuid, key),online_stats_get(uuid, key))
            end_hyp = datetime.datetime.now()
            used_hyp = end_hyp - start_hyp
            data_stats = result[0]
            data_online = result[1]

        elif command in command_sw:

            result = await asyncio.gather(game_stats_get(uuid, key),rsw_stats_get(uuid, key))
            end_hyp = datetime.datetime.now()
            used_hyp = end_hyp - start_hyp
            data_stats = result[0]
            data_rsw = result[1]

        elif command in command_guild:

            result = await asyncio.gather(game_stats_get(uuid, key),guild(uuid, key))
            end_hyp = datetime.datetime.now()
            used_hyp = end_hyp - start_hyp
            data_stats = result[0]
            data_guild = result[1]

        else:

            result = await asyncio.gather(game_stats_get(uuid, key))
            end_hyp = datetime.datetime.now()
            used_hyp = end_hyp - start_hyp
            data_stats = result[0]


        '''---------------------------------------------STATS---------------------------------------------'''
        try:
            ifsuccess = data_stats['success']
        except:
            output = '获取玩家信息失败!'
            writelog(30, user, group, input, output)
            return output

        if ifsuccess is True:
            result = data_stats['player']
            if result is None:
                output = '玩家不存在或未进入过服务器！'
                writelog(30, user, group, input, output)
                return output
            else:
                try:
                    try:
                        name = data_stats['player']['displayname']
                        name_pure = name
                        name += '^*&$#'
                    except:
                        name = player
                    try:
                        prefix = delcolor(data_stats['player']['prefix'])
                        if prefix == 'NONE':
                            prefix = ''
                        elif prefix is None:
                            prefix = ''
                    except:
                        prefix = ''
                    try:
                        rank_pro = '[%s]' % data_stats['player']['rank']
                        if rank_pro == 'NORMAL':
                            rank_pro = ''
                        elif rank_pro == '[NORMAL]':
                            rank_pro = ''
                    except:
                        rank_pro = ''
                    try:
                        rank = data_stats['player']['newPackageRank']
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
                            rank_plusplus = data_stats['player']['monthlyPackageRank']
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
                    log = '{"time":"%s","level":"error","user":"%s","group":"%s","input":"%s","result":"%s"}' % (
                    time_now, user, group, text_input, output.replace('\n', '  '))
                    writelog(40, user, group, input, output)
                    await app.sendFriendMessage(OWNER, MessageChain.create(Plain('运行出错!', log)))
                    return log

                tryapi = True
                online_apioff = False

                try:
                    firstlogin = timeStamp(data_stats['player']['firstLogin'])
                except:
                    firstlogin = 'Invalid'
                try:
                    lastlogin = data_stats['player']['lastLogin']
                except:
                    lastlogin = 'Invalid'
                    tryapi = False
                try:
                    lastlogout = data_stats['player']['lastLogout']
                except:
                    lastlogout = 'Invalid'
                    tryapi = False

                if tryapi is True:
                    delta = lastlogout - lastlogin
                    if delta < 0:
                        online_apioff = True
                    else:
                        online_apioff = False
                    try:
                        lastlogin = timeStamp(lastlogin)
                    except:
                        lastlogin = 'Invalid'
                    try:
                        lastlogout = timeStamp(lastlogout)
                    except:
                        lastlogout = 'Invalid'


        else:
            try:
                output = data_stats['cause']
                if output == 'Invalid API key':
                    output = 'API key为空,请检查是否正确配置API key!'
                    writelog(50, user, group, input, output)
                    return '无需发送'
                elif output == 'Key throttle':
                    output = 'API key达到查询上限,请稍后再试!'
                    writelog(40, user, group, input, output)
                    return '无需发送'
                else:
                    output = '从api.hypixel.net获取数据失败，原因:%s' % output
                    writelog(30, user, group, input, output)
                    return '无需发送'
            except:
                output = '从api.hypixel.net获取数据失败，原因未知'
                writelog(30, user, group, input, output)
                return '无需发送'

        '''---------------------------------------------ONLINE---------------------------------------------'''
        if command in command_hyp:
            ifsuccess2 = data_online['success']
            if ifsuccess2 is True:
                status = data_online['session']['online']
                if status is True:
                    try:
                        mode = '|%s' % translate_mode(data_online['session']['mode'])
                    except:
                        mode = ''
                    try:
                        map = '|%s' % translate_map(data_online['session']['map'])
                    except:
                        map = ''
                    gametype = translate_game(data_online['session']['gameType'])
                    playing = '%s%s%s' % (gametype, mode, map)
                    online = '[在线]'
                else:
                    if online_apioff is True:
                        online = '[在线]'
                        playing = '*该玩家关闭了在线状态API'
                    else:
                        if tryapi is False:
                            online = '[未知]'
                            playing = '*该玩家关闭了最近游戏/在线状态API'
                        else:
                            online = '[离线]'
                            try:
                                recentgame = translate_game(data_stats['player']['mostRecentGameType'])
                                playing = ' 最近游戏:%s' % recentgame
                            except:
                                playing = '*该玩家关闭了最近游戏API'

            else:
                playing = error
                online = '[ERROR]'
        else:
            pass

        '''---------------------------------------------RSW---------------------------------------------'''
        if command in command_sw:
            ifsuccess3 = data_rsw['success']
            if ifsuccess3 is True:
                try:
                    position_rsw = data_rsw['result']['position']
                except:
                    position_rsw = 'Invalid'
                try:
                    score_rsw = data_rsw['result']['score']
                except:
                    score_rsw = '0'
                rsw = 'Rank分数:%s Rank排名:%s' % (score_rsw, position_rsw)
            else:
                rsw = 'Rank数据未找到!'
        else:
            pass


    elif mode_input == '2' and command in command_list_randomstr:
        try:
            num = math.floor(float(str.split(input)[1]))
        except:
            return 'Error'
        str_random = ''.join(random.sample(string.ascii_letters + string.digits, num))
        output = f'长度为{num}的随机字符串:\n{str_random}'
        return output


    elif command in command_list_send:
        if str(user_id) in ADMIN:
            output = '复读' + str.split(input, ' ', 1)[1]
        else:
            output = '您没有使用该指令的权限!'
        return output



    elif (mode_input == '3' or '4') and (command in command_list_random):
        try:
            num1 = math.floor(float(str.split(input)[1]))
            num2 = math.floor(float(str.split(input)[2]))
            if num1 > num2:
                num1, num2 = num2, num1
            if mode_input == '3':
                num3 = 1
                num_out = random.randint(num1, num2)
            elif mode_input == '4':
                num3 = math.floor(float(str.split(input)[3]))
                num_range = range(num1, num2)
                num_out = random.sample(num_range, num3)
            else:
                raise ValueError
        except:
            return 'Error'
        output = f'{num3}个随机数生成自[{num1},{num2}]:\n{str(num_out)}'
        return output


    else:
        output = '未知指令'
        writelog(30, user, group, input, output)
        return '无需发送'

    '''--------------------------------------------------MATCH RESULT--------------------------------------------------'''
    output = '未识别的指令,请检查拼写是否有误!'
    try:
        if command in command_hyp:
            try:
                exp = float(data_stats['player']['networkExp'])
                level = ('%.2f' % ((exp / 1250 + 12.25) ** 0.5 - 2.5))
            except:
                level = '1'
            try:
                karma = data_stats['player']['karma']
            except:
                karma = '0'
            try:
                achievement = data_stats['player']['achievementPoints']
            except:
                achievement = '0'

            output = "%s%s%s%s[Lv.%s]\n%s%s\n成就点数:%s 人品值:%s\n首次登入时间:%s\n上次登入时间:%s\n上次下线时间:%s" % intformat(
                [rank_pro, prefix, rank, name, level, online, playing, achievement, karma, firstlogin, lastlogin,
                 lastlogout])

        elif command in command_sw:
            '''---------------------------------------------SKYWARS---------------------------------------------'''
            gamename = 'SkyWars'
            level_sw = formhandlerSW(getintdata(data_stats, gamename, 'levelFormatted'))
            coins_sw = getintdata(data_stats, gamename, 'coins')
            heads_sw = getintdata(data_stats, gamename, 'heads')
            assists_sw = getintdata(data_stats, gamename, 'assists')
            deaths_sw = getintdata(data_stats, gamename, 'deaths')
            kills_sw = getintdata(data_stats, gamename, 'kills')
            wins_sw = getintdata(data_stats, gamename, 'wins')
            losses_sw = getintdata(data_stats, gamename, 'losses')
            kd_sw = quotient(kills_sw, deaths_sw)
            wl_sw = quotient(wins_sw, losses_sw)

            # arrows_sw_shot = getintdata(data_stats,gamename,'arrows_shot')
            # arrows_sw_hit = getintdata(data_stats,gamename,'arrows_hit')
            # arrows_sw_acc = '{}%'.format(quotient(arrows_sw_hit,arrows_sw_shot)*100)
            # thrown_sw = getintdata(data_stats,gamename,'egg_thrown')
            # chestsopened_sw = getintdata(data_stats,gamename,'chests_opened')
            # enderpearls_thrown_sw = getintdata(data_stats,gamename,'enderpearls_thrown')
            # blocksplaced_sw = getintdata(data_stats,gamename,'blocks_placed')
            # blocksbroken_sw = getintdata(data_stats,gamename,'blocks_broken')
            # playedtime_sw_1 = timeconvert(getintdata(data_stats,gamename,'time_played_solo'))
            # playedtime_sw_2 = timeconvert(getintdata(data_stats,gamename,'time_played_team'))
            # playedtime_sw = timeconvert(getintdata(data_stats,gamename,'time_played'))
            # sw_list = ['levelFormatted','coins','heads','assists','kills','deaths','wins','losses']
            # text_sw = '%a%a%a%a[%s]\n硬币:%s 头颅:%s 总助攻:%s\n总击杀:%s 总死亡:%s 总K/D:%a\n总胜场:%s 总败场:%s 总W/L:%a\n%a'
            # output = jsonhandler(data_stats,sw_list,text_sw,'player','stats','SkyWars')
            # output = delcolor(fillin(output,[rank_pro,prefix,rank,name,quotient_json(data_stats,['kills','deaths'],'player','stats','SkyWars'),quotient_json(data_stats,['wins','losses'],'player','stats','SkyWars'),rsw]))

            output = "%s%s%s%s[%s]\n硬币:%s 头颅:%s 总助攻:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总胜场:%s 总败场:%s 总W/L:%s\n%s" % intformat(
                [rank_pro, prefix, rank, name, level_sw, coins_sw, heads_sw, assists_sw, kills_sw, deaths_sw, kd_sw,
                 wins_sw, losses_sw, wl_sw, rsw])


        elif command in command_bw:
            '''---------------------------------------------BEDWARS---------------------------------------------'''
            gamename = 'Bedwars'
            try:
                level_bw = data_stats['player']['achievements']['bedwars_level']
            except:
                level_bw = 0
            coins_bw = getintdata(data_stats, gamename, 'coins')
            kills_bw = getintdata(data_stats, gamename, 'kills_bedwars')
            deaths_bw = getintdata(data_stats, gamename, 'deaths_bedwars')
            kills_bw_final = getintdata(data_stats, gamename, 'final_kills_bedwars')
            deaths_bw_final = getintdata(data_stats, gamename, 'final_deaths_bedwars')
            wins_bw = getintdata(data_stats, gamename, 'wins_bedwars')
            losses_bw = getintdata(data_stats, gamename, 'losses_bedwars')
            beds_bw = getintdata(data_stats, gamename, 'beds_broken_bedwars')
            winstreak_bw = getintdata(data_stats, gamename, 'winstreak')
            kd_bw = quotient(kills_bw, deaths_bw)
            kd_bw_final = quotient(kills_bw_final, deaths_bw_final)
            wl_bw = quotient(wins_bw, losses_bw)

            output = "%s%s%s%s[Lv.%s]\n硬币:%s 破坏床数:%s 当前连胜:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总最终击杀:%s 总最终死亡:%s 总最终K/D:%s\n总胜场:%s 总败场:%s 总W/L:%s" % intformat(
                [rank_pro, prefix, rank, name, level_bw, coins_bw, beds_bw, winstreak_bw, kills_bw, deaths_bw, kd_bw,
                 kills_bw_final, deaths_bw_final, kd_bw_final, wins_bw, losses_bw, wl_bw])


        elif command in command_mw:
            '''---------------------------------------------MEGAWALLS---------------------------------------------'''
            gamename = 'Walls3'
            coins_walls3 = getintdata(data_stats, gamename, 'coins')
            witherdamage_walls3 = getintdata(data_stats, gamename, 'wither_damage')
            kills_walls3_defender = getintdata(data_stats, gamename, 'defender_kills')
            kills_walls3 = getintdata(data_stats, gamename, 'kills')
            deaths_walls3 = getintdata(data_stats, gamename, 'deaths')
            assists_walls3 = getintdata(data_stats, gamename, 'assists')
            kills_walls3_final = getintdata(data_stats, gamename, 'final_kills')
            deaths_walls3_final = getintdata(data_stats, gamename, 'final_deaths')
            assists_walls3_final = getintdata(data_stats, gamename, 'final_assists')
            wins_walls3 = getintdata(data_stats, gamename, 'wins')
            losses_walls3 = getintdata(data_stats, gamename, 'losses')
            kd_walls3 = quotient(kills_walls3, deaths_walls3)
            kd_walls3_final = quotient(kills_walls3_final, deaths_walls3_final)
            wl_walls3 = quotient(wins_walls3, losses_walls3)

            output = "%s%s%s%s\n硬币:%s 总伤害凋灵:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总最终击杀:%s 总最终死亡:%s 总最终K/D:%s\n总胜场:%s 总败场:%s 总W/L:%s\n总助攻:%s 总最终助攻:%s" % intformat(
                [rank_pro, prefix, rank, name, coins_walls3, witherdamage_walls3, kills_walls3, deaths_walls3,
                 kd_walls3, kills_walls3_final, deaths_walls3_final, kd_walls3_final, wins_walls3, losses_walls3,
                 wl_walls3, assists_walls3, assists_walls3_final])


        elif command in command_uhc:
            '''---------------------------------------------UHC---------------------------------------------'''
            gamename = 'UHC'
            coins_uhc = getintdata(data_stats, gamename, 'coins')
            kills_uhc_2 = getintdata(data_stats, gamename, 'kills')
            kills_uhc_1 = getintdata(data_stats, gamename, 'kills_solo')
            deaths_uhc_2 = getintdata(data_stats, gamename, 'deaths')
            deaths_uhc_1 = getintdata(data_stats, gamename, 'deaths_solo')
            score_uhc = getintdata(data_stats, gamename, 'score')
            headseaten_uhc_2 = getintdata(data_stats, gamename, 'heads_eaten')
            headseaten_uhc_1 = getintdata(data_stats, gamename, 'heads_eaten_solo')
            wins_uhc_2 = getintdata(data_stats, gamename, 'wins')
            wins_uhc_1 = getintdata(data_stats, gamename, 'wins_solo')
            wins_uhc = wins_uhc_1 + wins_uhc_2
            kills_uhc = kills_uhc_1 + kills_uhc_2
            deaths_uhc = deaths_uhc_1 + deaths_uhc_2
            headseaten_uhc = headseaten_uhc_1 + headseaten_uhc_2
            kd_uhc = quotient(kills_uhc, deaths_uhc)

            output = "%s%s%s%s\n硬币:%s 分数:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总胜场:%s 总金头使用:%s" % intformat(
                [rank_pro, prefix, rank, name, coins_uhc, score_uhc, kills_uhc, deaths_uhc, kd_uhc, wins_uhc,
                 headseaten_uhc])


        elif command in command_duel:
            '''---------------------------------------------DUELS---------------------------------------------'''
            gamename = 'Duels'
            coins_duels = getintdata(data_stats, gamename, 'coins')
            kills_duels = getintdata(data_stats, gamename, 'kills')
            deaths_duels = getintdata(data_stats, gamename, 'deaths')
            wins_duels = getintdata(data_stats, gamename, 'wins')
            losses_duels = getintdata(data_stats, gamename, 'losses')
            wl_duels = quotient(wins_duels, losses_duels)
            kd_duels = quotient(kills_duels, deaths_duels)
            arrows_shots_duels = getintdata(data_stats, gamename, 'bow_shots')
            arrows_hits_duels = getintdata(data_stats, gamename, 'bow_hits')
            arrows_acc_duels = '{}%'.format(round(quotient(arrows_hits_duels * 100, arrows_shots_duels), 2))
            melee_swings_duels = getintdata(data_stats, gamename, 'melee_swings')
            melee_hits_duels = getintdata(data_stats, gamename, 'melee_hits')
            melee_acc_duels = '{}%'.format(round(quotient(melee_hits_duels * 100, melee_swings_duels), 2))

            output = "%s%s%s%s\n硬币:%s\n近战命中率:%s 射击命中率:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总胜场:%s 总败场:%s 总W/L:%s" % intformat(
                [rank_pro, prefix, rank, name, coins_duels, melee_acc_duels, arrows_acc_duels, kills_duels,
                 deaths_duels, kd_duels, wins_duels, losses_duels, wl_duels])


        elif command in command_bsg:
            '''---------------------------------------------BSG---------------------------------------------'''
            gamename = 'HungerGames'
            coins_bsg = getintdata(data_stats, gamename, 'coins')
            kills_bsg = getintdata(data_stats, gamename, 'kills')
            deaths_bsg = getintdata(data_stats, gamename, 'deaths')
            kd_bsg = quotient(kills_bsg, deaths_bsg)
            wins_bsg = getintdata(data_stats, gamename, 'wins')
            gamesplayed_bsg = deaths_bsg + wins_bsg
            timeplayed_bsg = timeconvert(getintdata(data_stats, gamename, 'time_played'))
            kg_bsg = quotient(kills_bsg, gamesplayed_bsg)

            output = "%s%s%s%s\n硬币:%s 总胜场:%s\n总击杀:%s 总死亡:%s 总K/D:%s\n总游戏时长:%s 总游戏场数:%s 总K/G:%s" % intformat(
                [rank_pro, prefix, rank, name, coins_bsg, wins_bsg, kills_bsg, deaths_bsg, kd_bsg, timeplayed_bsg,
                 gamesplayed_bsg, kg_bsg])


        elif command in command_hg:
            '''---------------------------------------------MURDER MYSTERY---------------------------------------------'''
            gamename = 'MurderMystery'
            coins_murder = getintdata(data_stats, gamename, 'coins')
            kills_murder = getintdata(data_stats, gamename, 'kills')
            deaths_murder = getintdata(data_stats, gamename, 'deaths')
            wins_murder = getintdata(data_stats, gamename, 'wins')
            gamesplayed_murder = getintdata(data_stats, gamename, 'games')
            kills_murder_knife = getintdata(data_stats, gamename, 'knife_kills')
            kills_murder_bow = getintdata(data_stats, gamename, 'bow_kills')
            kills_murder_knife_thrown = getintdata(data_stats, gamename, 'thrown_knife_kills')
            kills_murder_infected = getintdata(data_stats, gamename, 'kills_as_infected')
            kills_murder_survivor = getintdata(data_stats, gamename, 'kills_as_survivor')
            wins_murder_infected = getintdata(data_stats, gamename, 'survivor_wins')

            output = "%s%s%s%s\n硬币:%s 总胜场:%s\n总击杀:%s 总死亡:%s\n弓箭击杀:%s 飞刀击杀:%s 总游戏场数:%s\n感染者击杀:%s 生存者击杀:%s 感染模式胜场:%s" % intformat(
                [rank_pro, prefix, rank, name, coins_murder, wins_murder, kills_murder, deaths_murder, kills_murder_bow,
                 kills_murder_knife_thrown, gamesplayed_murder, kills_murder_infected, kills_murder_survivor,
                 wins_murder_infected])


        elif command in command_tnt:

            '''---------------------------------------------TNT GAMES---------------------------------------------'''
            gamename = 'TNTGames'
            coins_tnt = getintdata(data_stats, gamename, 'coins')
            wins_tnt_tntrun = getintdata(data_stats, gamename, 'wins_tntrun')
            wins_tnt_pvprun = getintdata(data_stats, gamename, 'wins_pvprun')
            wins_tnt_tntag = getintdata(data_stats, gamename, 'wins_tntag')
            wins_tnt_bow = getintdata(data_stats, gamename, 'wins_bowspleef')
            wins_tnt_wizard = getintdata(data_stats, gamename, 'wins_capture')
            kills_tnt_pvp = getintdata(data_stats, gamename, 'kills_pvprun')
            kills_tnt_tag = getintdata(data_stats, gamename, 'kills_tntag')
            kills_tnt_wizard = getintdata(data_stats, gamename, 'kills_capture')
            deaths_tnt_wizard = getintdata(data_stats, gamename, 'deaths_capture')
            assists_tnt_wizard = getintdata(data_stats, gamename, 'assists_capture')
            record_tnt_tntrun = timeconvert(getintdata(data_stats, gamename, 'record_tntrun'))
            record_tnt_pvprun = timeconvert(getintdata(data_stats, gamename, 'record_pvprun'))
            kd_tnt_wizard = quotient(kills_tnt_wizard, deaths_tnt_wizard)

            output = "%s%s%s%s\n硬币:%s\nTNTRun: 胜场:%s 纪录:%s\nPVPRun: 胜场:%s 击杀数:%s 纪录:%s\nTNTag: 胜场数:%s 击杀数:%s\nBowspleef: 胜场数:%s\nWizards: 胜场数:%s 助攻数:%s\n击杀数:%s 死亡数:%s K/D:%s" % intformat(
                [rank_pro, prefix, rank, name, coins_tnt, wins_tnt_tntrun, record_tnt_tntrun, wins_tnt_pvprun,
                 kills_tnt_pvp, record_tnt_pvprun, wins_tnt_tntag, kills_tnt_tag, wins_tnt_bow, wins_tnt_wizard,
                 assists_tnt_wizard, kills_tnt_wizard, deaths_tnt_wizard, kd_tnt_wizard])


        elif command in command_parkour:
            try:
                records = data_stats['player']['parkourCheckpointBests']
                total_list = data_stats['player']['parkourCompletions']

                dict_1 = {}
                dict_2 = {}
                for lobby in records:
                    lobby_str = '%s:' % lobby
                    lobby_1 = sorted(records[lobby].items(), key=lambda x: x[0], reverse=False)
                    # print(lobby)
                    for point in lobby_1:
                        time_used = datetime.datetime.fromtimestamp(point[1] / 1000) - datetime.datetime.fromtimestamp(
                            0.0)
                        print(time_used)
                        lobby_str += '\n记录点[%s]%s' % (int(point[0]) + 1, str(time_used)[2:-3])
                    print(lobby)
                    dict_1[lobby] = lobby_str
                for total in total_list:
                    print(total_list[total])
                    time_took = datetime.datetime.fromtimestamp(
                        total_list[total][0]['timeTook'] / 1000) - datetime.datetime.fromtimestamp(0.0)
                    time_start = datetime.datetime.fromtimestamp(total_list[total][0]['timeStart'] / 1000)
                    str_out = '总用时:%s\n创建时间:%s' % (str(time_took)[2:-3], str(time_start)[:-7])
                    dict_2[total] = str_out
                print(dict_2)
                str_out = ''
                for a in dict_1:
                    try:
                        str_out += (dict_1[a] + '\n' + dict_2[a] + '\n\n')
                    except:
                        str_out += (dict_1[a] + '\n' + '该跑酷未完成' + '\n\n')
                output = str_out[:-1]
                # output = translate_game(str.upper(output))
                output = "%s%s%s%s\n%s" % intformat([rank_pro, prefix, rank, name, output])
                string_to_image(output, font_file=FONT, file_name='parkour.png')
                '''transfor parkour.png to base64'''
                with open('parkour.png', 'rb') as f:
                    str_out = str(base64.b64encode(f.read()))
                output = ''
                writelog(20, user, group, input, str_out)
                return output
            except:
                output = '%s%s%s%s\nInvalid\n获取失败或该玩家无数据!' % (rank_pro, prefix, rank, name_pure)
                writelog(30, user, group, input, output)
                return output



        elif command in command_guild:
            ifsuccess_guild = data_guild['success']
            if ifsuccess_guild is True:
                guild = data_guild['guild']
                if guild is None:
                    output = '玩家%s%s%s%s未加入公会' % (rank_pro, prefix, rank, name)
                else:
                    name_guild = guild['name']
                    coins_guild = guild['coins']
                    coins_ever = guild['coinsEver']
                    created_guild = guild['created']
                    created_guild = timeStamp(created_guild)
                    member = guild['members']
                    num_guild = len(member)
                    try:
                        description = guild['description']
                    except:
                        description = 'Invalid'
                    try:
                        preferred_list = guild['preferredGames']
                        i = 0

                        for game in preferred_list:
                            i += 1
                            if i == 1:
                                game_prefer = game
                            else:
                                game_prefer = '%s,%s' % (game_prefer, game)
                                game_prefer = translate_game(game_prefer)
                    except:
                        game_prefer = 'Invalid'
                    try:
                        tag_guild = guild['tag']
                    except:
                        tag_guild = 'Invalid'

                    exp_guild = guild['exp']
                    exp_guild = int(exp_guild)
                    level = 0
                    level_list = [range(0, 100001), range(100001, 250001), range(250001, 500001),
                                  range(500001, 1000001), range(1000001, 1750001), range(1750001, 2750001),
                                  range(2750001, 4000001), range(4000001, 5500001), range(5500001, 7500001),
                                  range(7500001, 15000001)]
                    if exp_guild in range(0, 15000001):
                        for level_range in level_list:
                            if exp_guild in level_range:
                                level = level_list.index(level_range)
                                if level == 9:
                                    level = math.floor((exp_guild - 7500000) / 2500000) + 9
                                break
                            else:
                                pass
                    else:
                        level = math.floor((exp_guild - 15000000) / 3000000) + 13

                    output = '%s%s%s%s目前所处公会:\n名称:%s 显示tag:%s\n等级:%s 人数:%s\n介绍:%s\n创建时间:%s\n成员常玩游戏:%s' % (
                    rank_pro, prefix, rank, name_pure, name_guild, tag_guild, level, num_guild, description,
                    created_guild, game_prefer)



    except Exception as error:
        output = '输出缺少变量，请联系开发者!报错信息:%s' % error
        log = '{"time":"%s","level":"error","user":"%s","group":"%s","input":"%s","result":"%s"}' % (
        time_now, user, group, text_input, output.replace('\n', '  '))
        writelog(40, user, group, input, output)
        print(error)
        await app.sendFriendMessage(OWNER, MessageChain.create(Plain('运行出错!', log)))
        return '无需发送'

    end = datetime.datetime.now()
    used = end - start
    used = '%s秒' % str(used)[5:10]
    if output == 'error':
        pass
    else:
        output = '%s\n查询用时:%s  by %s' % (output, used, BOTNAME)
        try:
            writelog(20, user, group, input, output)
        except:
            pass
        return output


command_list_ping = (f'{COMMAND}PING', f'{COMMAND}SERVER', f'{COMMAND}MCPING', f'{COMMAND}查服')
command_list_syuulb = (f'{COMMAND}SYUULB', f'{COMMAND}SYUU', f'{COMMAND}SYUULEADERBOARD')

command_hyp = (f'{COMMAND}HYPIXEL', f'{COMMAND}HYP', f'{COMMAND}查', f'{COMMAND}查询', f'{COMMAND}信息')
command_sw = (f'{COMMAND}SW', f'{COMMAND}SKYWARS', f'{COMMAND}空岛', f'{COMMAND}空岛战争')
command_bw = (f'{COMMAND}BW', f'{COMMAND}BEDWARS' f'{COMMAND}起床', f'{COMMAND}起床战争')
command_mw = (f'{COMMAND}MW', f'{COMMAND}MEGAWALLS', f'{COMMAND}超战', f'{COMMAND}超级战墙')
command_uhc = (f'{COMMAND}UHC', f'{COMMAND}极限生存', f'{COMMAND}极限生存冠军')
command_duel = (f'{COMMAND}DUEL', f'{COMMAND}DUELS', f'{COMMAND}决斗', f'{COMMAND}决斗游戏')
command_bsg = (
f'{COMMAND}BSG', f'{COMMAND}HG', f'{COMMAND}HUNGERGAMES', f'{COMMAND}饥饿游戏', f'{COMMAND}闪电饥饿游戏', f'{COMMAND}饥饿')
command_hg = (f'{COMMAND}MM', f'{COMMAND}MURDER', f'{COMMAND}密室', f'{COMMAND}密室杀手')
command_tnt = (f'{COMMAND}TNT', 'TNTGAMES')
command_guild = (f'{COMMAND}GUILD', f'{COMMAND}公会')
command_parkour = (f'{COMMAND}PARKOUR', f'{COMMAND}跑酷')

command_list_needimage = (command_parkour,command_guild + command_tnt + command_hg + command_bsg + command_uhc + command_duel + command_sw + command_bw + command_hyp + command_mw)



loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host=config['Mirai-Api-Http_host'],  # 填入 HTTP API 服务运行的地址
        verify_key=config["Mirai-Api-Http_authKey"],  # 填入 verifyKey
        account=config['Mirai-Api-Http_account'],  # 你的机器人的 qq 号
    )
)

@bcc.receiver("GroupMessage")
async def group_message_handler(message: MessageChain, app: Ariadne, group: Group, member: Member):
    if message.asDisplay().startswith(f'{COMMAND}'):

        input = str.upper(message.asDisplay())
        if str.split(input)[0] in command_list_ping:
            output = await hyp(message.asDisplay(), [str(member.id), member.name], [str(group.id), group.name])
            print(output)
            if ('无需发送' or '未知指令') in output:
                pass
            else:
                if output.startswith(r'{') or output.startswith('服务器信息获取'):
                    await app.sendGroupMessage(group, MessageChain.create([Plain('获取失败或服务器不存在!')]), quote=message.dict()['__root__'][0]['id'])
                else:
                    await app.sendGroupMessage(group, MessageChain.create([At(member.id), IMAGE(path='1.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])

        elif str.split(input)[0] in command_list_syuulb and len(str.split(input)) == 1:
            output = await hyp(message.asDisplay(), [str(member.id), member.name], [str(group.id), group.name])
            await app.sendGroupMessage(group, MessageChain.create([At(member.id), IMAGE(path='syuu.png')]), quote=message.dict()['__root__'][0]['id'])

        elif str.split(input)[0] in command_parkour and len(str.split(input)) == 2:
            output = await hyp(message.asDisplay(), [str(member.id), member.name], [str(group.id), group.name])
            if '玩家' not in output:
                await app.sendGroupMessage(group, MessageChain.create([At(member.id), IMAGE(path='parkour.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])
            else:
                await app.sendGroupMessage(group, MessageChain.create([At(member.id), Plain('\n' + output)]), quote=message.dict()['__root__'][0]['id'])

        else:
            output = await hyp(message.asDisplay(), [str(member.id), member.name], [str(group.id), group.name])
            if ('无需发送' or '未知指令') in output:
                pass
            else:
                if (str.split(input)[0] in command_list_needimage) and ('玩家' not in output) and ('复读' not in output):
                    await app.sendGroupMessage(group, MessageChain.create([At(member.id), Plain('\n'), IMAGE.fromLocalFile('player.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])
                elif '复读' in output:
                    await app.sendGroupMessage(group, MessageChain.create([Plain(output[2:])]))
                else:
                    await app.sendGroupMessage(group, MessageChain.create([At(member.id), Plain('\n' + output)]), quote=message.dict()['__root__'][0]['id'])


@bcc.receiver("FriendMessage")
async def friend_message_handler(message: MessageChain, app: Ariadne, friend: Friend):
    if message.asDisplay().startswith(f'{COMMAND}'):

        input = str.upper(message.asDisplay())
        if str.split(input)[0] in command_list_ping:
            output = await hyp(message.asDisplay(), [str(friend.id), friend.nickname])
            print(output)
            if ('无需发送' or '未知指令') in output:
                pass
            else:
                if output.startswith(r'{') or output.startswith('服务器信息获取'):
                    await app.sendFriendMessage(friend, MessageChain.create([Plain('获取失败或服务器不存在!')]), quote=message.dict()['__root__'][0]['id'])
                else:
                    await app.sendFriendMessage(friend, MessageChain.create([IMAGE(path='1.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])

        elif str.split(input)[0] in command_list_syuulb and len(str.split(input)) == 1:
            output = await hyp(message.asDisplay(), [str(friend.id), friend.nickname])
            await app.sendFriendMessage(friend, MessageChain.create([IMAGE(path='syuu.png')]), quote=message.dict()['__root__'][0]['id'])

        elif str.split(input)[0] in command_parkour and len(str.split(input)) == 2:
            output = await hyp(message.asDisplay(), [str(friend.id), friend.nickname])
            if '玩家' not in output:
                await app.sendFriendMessage(friend, MessageChain.create([IMAGE(path='parkour.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])
            else:
                await app.sendFriendMessage(friend, MessageChain.create([Plain(output)]), quote=message.dict()['__root__'][0]['id'])

        else:
            output = await hyp(message.asDisplay(), [str(friend.id), friend.nickname])
            if ('无需发送' or '未知指令') in output:
                pass
            else:
                if (str.split(input)[0] in command_list_needimage) and ('玩家' not in output) and ('复读' not in output):
                    await app.sendFriendMessage(friend, MessageChain.create([IMAGE.fromLocalFile('player.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])
                elif '复读' in output:
                    await app.sendFriendMessage(friend, MessageChain.create([Plain(output[2:])]))
                else:
                    await app.sendFriendMessage(friend, MessageChain.create([Plain(output)]), quote=message.dict()['__root__'][0]['id'])


@bcc.receiver("NudgeEvent")
async def nudge_message_handler(event: NudgeEvent):
    event_dict = event.dict()
    # print(event_dict)
    # print(app.account)
    if event_dict['fromId'] == app.account or event_dict['target'] != app.account:
        pass
    else:
        if str(event_dict['fromId']) in ADMIN:

            if event_dict['context_type'] == 'friend':
                await app.sendNudge(event_dict['fromId'])
                output = await hyp(f'{COMMAND}.status', [str(event_dict['fromId']), event_dict['fromId']])
                await app.sendFriendMessage(event_dict['fromId'],MessageChain.create([Plain(output)]))
            elif event_dict['context_type'] == 'group':
                output = await hyp(f'{COMMAND}.status', [str(event_dict['fromId']), event_dict['fromId']])
                await app.sendNudge(event_dict['fromId'],event_dict['subject']['id'])
                await app.sendGroupMessage(event_dict['subject']['id'],MessageChain.create([At(event_dict['fromId']),Plain('\n'+output)]))
        else:
            if event_dict['context_type'] == 'friend':
                await app.sendNudge(event_dict['fromId'])
            elif event_dict['context_type'] == 'group':
                await app.sendNudge(event_dict['fromId'], event_dict['subject']['id'])



@bcc.receiver("BotInvitedJoinGroupRequestEvent")
async def group_join_handler(event: BotInvitedJoinGroupRequestEvent):
    user = str(event.supplicant)
    username = str(event.nickname)
    group = str(event.groupId)
    groupname = str(event.groupName)
    message = str(event.message)
    timenow = datetime.datetime.now()
    output = '新入群申请已同意:\n用户qq:%s\n用户名:%s\n群号:%s\n群名:%s\n入群描述:%s\n时间:%s' % (user, username, group, groupname, message, timenow)
    await event.accept('【请勿拉入广告群/拉人有福利群等无意义群】自动加入群聊成功，如有任何疑问请咨询开发者hycx233：3442535256')
    await app.sendFriendMessage(int(user), MessageChain.create([Plain('【请勿拉入广告群/拉人有福利群等无意义群】自动加入群聊成功，如有任何疑问请咨询开发者hycx233：3442535256')]))
    await app.sendFriendMessage(3442535256, MessageChain.create([Plain(output)]))


loop.run_until_complete(app.lifecycle())