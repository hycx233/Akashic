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
VERSION += '-??'

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
    ???????????????????????????
    :param string: ?????????
    :param font_size: ????????????
    :param font_color: ????????????
    :param background_color: ????????????
    :return: ??????
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
    command_help = (f'{COMMAND}HELP', f'{COMMAND}??????')
    command_hyp = (f'{COMMAND}HYPIXEL', f'{COMMAND}HYP', f'{COMMAND}???', f'{COMMAND}??????', f'{COMMAND}??????')
    command_sw = (f'{COMMAND}SW', f'{COMMAND}SKYWARS', f'{COMMAND}??????', f'{COMMAND}????????????')
    command_bw = (f'{COMMAND}BW', f'{COMMAND}BEDWARS' f'{COMMAND}??????', f'{COMMAND}????????????')
    command_mw = (f'{COMMAND}MW', f'{COMMAND}MEGAWALLS', f'{COMMAND}??????', f'{COMMAND}????????????')
    command_uhc = (f'{COMMAND}UHC', f'{COMMAND}????????????', f'{COMMAND}??????????????????')
    command_duel = (f'{COMMAND}DUEL', f'{COMMAND}DUELS', f'{COMMAND}??????', f'{COMMAND}????????????')
    command_bsg = (
    f'{COMMAND}BSG', f'{COMMAND}HG', f'{COMMAND}HUNGERGAMES', f'{COMMAND}????????????', f'{COMMAND}??????????????????', f'{COMMAND}??????')
    command_hg = (f'{COMMAND}MM', f'{COMMAND}MURDER', f'{COMMAND}??????', f'{COMMAND}????????????')
    command_tnt = (f'{COMMAND}TNT', 'TNTGAMES')
    command_ban = (f'{COMMAND}BAN', f'{COMMAND}BANNED', f'{COMMAND}??????')
    command_guild = (f'{COMMAND}GUILD', f'{COMMAND}??????')
    command_parkour = (f'{COMMAND}PARKOUR', f'{COMMAND}??????')

    command_list_hypixel = command_parkour + command_help + command_hyp + command_sw + command_bw + command_mw + command_uhc + command_duel + command_bsg + command_hg + command_tnt + command_ban + command_guild

    command_list_namehistory = (f'{COMMAND}NAME', f'{COMMAND}HISTORY', f'{COMMAND}HISTORYNAME', f'{COMMAND}NAMEHISTORY', f'{COMMAND}MC', f'{COMMAND}MINECRAFT')
    command_list_ping = (f'{COMMAND}PING', f'{COMMAND}SfERVER', f'{COMMAND}MCPING', f'{COMMAND}??????')
    command_list_api = (f'{COMMAND}API', f'{COMMAND}APISTATS')
    command_list_status = (f'{COMMAND}.STATUS', f'{COMMAND}SERVERSTATUS')
    command_list_luck = (f'{COMMAND}LUCK', f'{COMMAND}FORTUNE', f'{COMMAND}??????')
    command_list_random = (f'{COMMAND}RANDOM', f'{COMMAND}??????', f'{COMMAND}?????????')
    command_list_randomstr = (f'{COMMAND}RANDOMSTR', f'{COMMAND}STR', f'{COMMAND}???????????????', f'{COMMAND}????????????')
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
        ''' ?????????CPU????????? '''
        mem = psutil.virtual_memory()
        # ????????????????????????
        memory = '???????????????: ' + str(psutil.virtual_memory().percent) + '%'
        mem_str = "???????????????: " + str(round(mem.used / EXPAND, 2)) + "MB/"
        mem_str += str(round(mem.total / EXPAND, 2)) + "MB"

        # ??????cpu???????????????
        cpu = 'CPU?????????: ' + str(psutil.cpu_percent(0)) + '%'
        output = '????????????????????????:\n' + cpu + '\n' + memory + '\n' + mem_str
        return output

    def serverGet(text):

        def formhandle(string):
            for color in (
                    '??0', '??1', '??2', '??3', '??4', '??5', '??6', '??7', '??8', '??9', '??a', '??b', '??c', '??d', '??e', '??f',
                    '??k',
                    '??l', '??m',
                    '??n', '??o', '??r'):
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

                output = '[???ip]%s:%s\n[??????]%s\n[??????]%s(%s)\n[??????]%s/%s\n[??????]%s\n[??????]%s\n[mod]%s' % (
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
            output = '?????????????????????????????????!'

        time_2 = datetime.datetime.now()
        used = time_2 - time_1
        used = '%s???' % str(used)[5:10]
        output = '%s\n????????????:%s  by Akashic' % (output, used)
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
        '??0', '??1', '??2', '??3', '??4', '??5', '??6', '??7', '??8', '??9', '??a', '??b', '??c', '??d', '??e', '??f', '??k', '??l',
        '??m', '??n', '??o', '??r'):
            string = string.replace(color, '')
        return string

    def formhandlerSW(string):
        string = str(string)
        string_output = ''
        for color in (
        '??0', '??1', '??2', '??3', '??4', '??5', '??6', '??7', '??8', '??9', '??a', '??b', '??c', '??d', '??e', '??f', '??k', '??l',
        '??m', '??n', '??o', '??r'):
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
        translate_dic = {'QUAKECRAFT': '????????????', 'WALLS3': '????????????', 'WALLS': '??????', 'PAINTBALL': '????????????',
                         'SURVIVAL_GAMES': '??????????????????', 'TNTGAMES': '????????????', 'VAMPIREZ': '?????????', 'WALLS3': '????????????',
                         'ARCADE': '????????????', 'ARENA': '?????????', 'UHC': '??????????????????', 'MCGO': '????????????', 'BATTLEGROUND': '????????????',
                         'SUPER_SMASH': '????????????', 'GINGERBREAD': '????????????', 'HOUSING': '????????????', 'SKYWARS': '????????????',
                         'TRUE_COMBAT': '????????????', 'SPEED_UHC': '??????????????????', 'SKYCLASH': '???????????????', 'LEGACY': '????????????',
                         'PROTOTYPE': '???????????????', 'BEDWARS': '????????????', 'MURDER_MYSTERY': '????????????', 'BUILD_BATTLE': '????????????',
                         'DUELS': '????????????', 'SKYBLOCK': '????????????', 'PIT': '????????????', 'REPLAY': '????????????', 'SMP': 'Hypixel SMP',
                         'MAIN': '??????'}
        for word in translate_dic.keys():
            text = text.replace(word, translate_dic[word])
        return text

    def translate_mode(text):
        translate_dic = {'LOBBY': '??????', 'ctf_mini': '????????????', 'domination': '???????????????', 'team_deathmatch': '????????????????????????',
                         'standard': '????????????', 'face_off': '????????????', 'solo_normal': '????????????', 'teams_normal': '????????????',
                         '2v2_normal': ' 2v2 ??????', 'teams_normal': ' 2v2v2 ??????', '1v1_normal': ' 1v1 ??????',
                         'friends_normal': ' Friends 1v1v1v1 ??????', 'dynamic': '????????????', 'hub': '?????????', 'farming_1': '????????????',
                         'combat_1': '????????????', 'combat_2': '????????????', 'combat_3': '??????', 'mining_1': '????????????',
                         'mining_2': '????????????', 'mining_3': ' Dwarven Mine ', 'mining_4': ' Crystal Hollows ',
                         'foraging_1': '??????', 'dungeon_hub': '????????????', 'dungeon': '??????', 'ranked_normal': '????????????',
                         'solo_normal': '??????????????????', 'solo_insane': '??????????????????', 'teams_normal': '??????????????????',
                         'teams_insane': '??????????????????', 'mega_normal': ' ??????????????????', 'mega_doubles': '?????? Doubles ??????',
                         'solo_insane_tnt_madness': '???????????? TNT ??????', 'teams_insane_tnt_madness': '???????????? TNT ??????',
                         'solo rush': '??????????????????', 'teams_insane_rush': '??????????????????', 'solo_insane_slime': '?????????????????????',
                         'teams_insane_slime': '?????????????????????', 'solo_insane_lucky': '????????????????????????',
                         'teams_insane_lucky': '????????????????????????', 'solo_insane_hunters_vs_beasts': '??????????????????', 'TNTRUN': '????????????',
                         'PVPRUN': 'PVP ????????????', 'BOWSPLEEF': '????????????', 'TNTAG': '?????? TNT ', 'CAPTURE': '????????????',
                         'BEDWARS_EIGHT_ONE': '????????????', 'BEDWARS_EIGHT_TWO': '????????????', 'BEDWARS_FOUR_THREE': ' 3v3v3v3 ??????',
                         'BEDWARS_FOUR_FOUR': ' 4v4v4v4 ??????', 'BEDWARS_CAPTURE': '????????????',
                         'BEDWARS_EIGHT_TWO_RUSH': '??????????????????', 'BEDWARS_FOUR_FOUR_RUSH': ' 4v4v4v4 ????????????',
                         'BEDWARS_EIGHT_TWO_ULTIMATE': '?????????????????????', 'BEDWARS_FOUR_FOUR_ULTIMATE': ' 4v4v4v4 ???????????????',
                         'BEDWARS_CASTLE': '40v40?????????????????????', 'BEDWARS_TWO_FOUR': '4V4 ??????',
                         'BEDWARS_EIGHT_TWO_VOIDLESS': '?????????????????????', 'BEDWARS_FOUR_FOUR_VOIDLESS': ' 4v4v4v4 ???????????????',
                         'BEDWARS_EIGHT_TWO_ARMED': '??????????????????', 'BEDWARS_FOUR_FOUR_ARMED': ' 4v4v4v4 ????????????',
                         'BEDWARS_EIGHT TWO_LUCKY': '????????????????????????', 'BEDWARS_FOUR_FOUR_LUCKY': ' 4v4v4v4 ??????????????????',
                         'BEDWARS_PRACTICE': '????????????', 'HOLE_IN_THE_WALL': '???????????????', 'SOCCER': '??????',
                         'BOUNTY_HUNTERS': '????????????', 'PIXEL_PAINTERS': '????????????', 'DRAGON_WARS': '?????????',
                         'ENDER_SPLEEF': '????????????', 'STARWARS': '????????????', 'THROW_OUT': '????????????', 'DEFENDER': '??????????????????',
                         'PARTY_GAMES_1': '????????????', 'FARM_HUNT': '???????????????', 'ZOMBIES_DEAD_END': '????????????',
                         'ZOMBIES_BAD_BLOOD': '????????????', 'ZOMBIES_ALIEN_ARCADIUM': '????????????',
                         'HIDE_AND_SEEK_PROP_HUNT': '???????????????', 'HIDE_AND_SEEK_PARTY_POOPER': '???????????????',
                         'SIMON_SAYS': '????????????', 'SANTA_SAYS': '?????????????????????', 'MINI_WALLS': '????????????', 'DAYONE': '????????????',
                         'PVP_CTW': '?????????????????????', 'normal': '????????????', 'deathmatch': '????????????????????????',
                         'NORMAL_PARTY': '???????????? - ????????????', 'DEATHMATCH_PARTY': '???????????? - ????????????????????????',
                         'BUILD_BATTLE_SOLO_NORMAL': '????????????', 'BUILD_BATTLE_TEAMS_NORMAL': '????????????',
                         'BUILD_BATTLE_SOLO_PRO': '????????????', 'BUILD_BATTLE_GUESS_THE_BUILD': '???????????????',
                         'DUELS_CLASSIC_DUEL': '????????????', 'DUELS_SW_DUEL': '??????????????????', 'DUELS_SW_DOUBLES': '??????????????????????????????',
                         'DUELS_BOW_DUEL': '????????????', 'DUELS_UHC_DUEL': '??????????????????', 'DUELS_UHC_DOUBLES': '??????????????????????????????',
                         'DUELS_UHC_FOUR': '??????????????????????????????', 'DUELS_UHC_MEETUP': '????????????????????????????????????',
                         'DUELS_POTION_DUEL': '????????????', 'DUELS_COMBO_DUEL': '????????????', 'DUELS_OP_DUEL': '????????????',
                         'DUELS_OP_DOUBLES': '??????????????????', 'DUELS_MW_DUEL': '??????????????????', 'DUELS_MW_DOUBLES': '????????????????????????',
                         'DUELS_SUMO_DUEL': '????????????', 'DUELS_BLITZ_DUEL': '?????????????????????', 'DUELS_BOWSPLEEF_DUEL': '??????????????????',
                         'DUELS_BRIDGE_DUEL': '????????????', 'DUELS_BRIDGE_DOUBLES': '??????????????????', 'DUELS_BRIDGE_FOUR': '??????????????????',
                         'DUELS_BRIDGE_2V2V2V2': '?????? 2v2v2v2 ??????', 'DUELS_BRIDGE_3V3V3V3': '?????? 4v4v4v4 ??????',
                         'MURDER_CLASSIC': '????????????', 'MURDER_DOUBLE_UP': '????????????', 'MURDER_ASSASSINS': '????????????',
                         'MURDER_INFECTION': '????????????', 'TOWERWARS_SOLO': '????????????', 'TOWERWARS_TEAM_OF_TWO': '????????????',
                         'SOLO': '????????????', 'TEAMS': '????????????', 'EVENTS': '????????????'}
        for word in translate_dic.keys():
            text = text.replace(word, translate_dic[word])
        return text

    def translate_map(text):
        translate_dic = {'DeadEnd': '????????????', 'BadBlood': '????????????', 'AlienArcadium': '???????????????', 'Amazon': '???????????????',
                         'Waterfall': '??????', 'Airshow': '??????????????????', 'Aquarium': '?????????', 'Archway': '????????????', 'Ashore': '??????',
                         'Boletum': '?????????', 'Chained': '????????????', 'Crypt': '??????', 'Eastwood': '????????????', 'Glacier': '????????????',
                         'Hollow': '????????????', 'Invasion': '????????????', 'Lectus': '???????????????', 'Lighthouse': '??????', 'Lotus': '?????????',
                         'Pernicious': '????????????', 'Playground': '?????????', 'Rooftop': '??????', 'Speedway': '??????',
                         'Stonekeep': '????????????', 'Swashbuckle': '?????????', 'Treenan': '????????????', 'IvoryCastle': '????????????',
                         'Cauldron': '?????????', 'Nomad': '????????????', 'Memorial': '????????????', 'Palette': '????????????', 'Winterhelm': '?????????',
                         'Villa': '????????????', 'Chronos': '????????????', 'Mothership': '????????????', 'Oasis': '????????????', 'Onionring': '????????????',
                         'Aegis': '????????????', 'AgniTemple': '???????????????', 'Anchored': '????????????', 'Aquarius': '???????????????',
                         'Aqueduct': '????????????', 'ArxCitadel': '???????????????', 'Clearing': '????????????', 'Coherence': '??????',
                         'Crumble': '????????????', 'DessertedIslands': '????????????', 'DwarfFortress': '????????????', 'Dwarven': '????????????',
                         'Dynasty': '????????????', 'Eden': '?????????', 'Eirene': '??????', 'Elven': '??????', 'ElvenTowers': '????????????',
                         'Entangled': '????????????', 'Equinox': '????????????', 'FirelinkShrine': '????????????', 'Frostbite': '????????????',
                         'Fortress': '??????', 'Fossil': '????????????', 'Foundation': '????????????', 'Fungi': '?????????', 'Hontori': '????????????',
                         'Humidity': '??????', 'Jinzhou': '????????????', 'LongIsland': '????????????', 'Maereen': '?????????',
                         'Magnolite': '????????????', 'Marooned': '????????????', 'Martian': '????????????', 'MegaShire': '??????', 'Meteor': '??????',
                         'Onionring2': '?????????v2', 'Onset': '?????????', 'Overfall': '????????????', 'Pitfall': '????????????', 'Plateau': '??????',
                         'Railroad': '??????', 'Reef': '????????????', 'Rocky': '????????????', 'Sanctuary': '??????', 'Sanctum': '??????',
                         'Sandbox': '??????', 'Sawmill': '?????????', 'Siege': '?????????', 'Sentinel': '????????????', 'Shire': '??????',
                         'Shrooms': '????????????', 'Skychurch': '????????????', 'Strata': '????????????', 'Submerged': '????????????', 'Templar': '??????',
                         'Towers': '????????????', 'Tribal': '????????????', 'Tribute': '????????????', 'Tundra': '??????', 'FrostBound': '????????????',
                         'TwistedGrove': '????????????', 'AncientTomb': '??????', 'Towerfall': '?????????', 'Transport': '?????????',
                         'Archives': '?????????', 'HypixelWorld': 'Hypixel?????????', 'Headquarters': '??????', 'Library': '?????????',
                         'GoldRush': '?????????', 'CruiseShip': '??????', 'Hollywood': '?????????', 'ArchivesTopFloor': '???????????????',
                         'Widow\'sDen': '???????????????', 'Aquarium': '?????????', 'Snowglobe': '?????????', 'TheBridge': '??????',
                         'Arena': '?????????', 'Sumo': '??????', 'Aquatica': '??????', 'Thornhill': '????????????', 'TheRift': '????????????',
                         'Stormwind': '????????????', 'Scorched': '????????????', 'Ruins': '????????????', 'Neolithic': '????????????', 'Gorge': '????????????',
                         'FalstadGate': '????????????', 'DorivenBasin': '????????????', 'DeathValley': '????????????', 'Crossfire': '????????????',
                         'BlackTemple': '????????????', 'AtherroughValley': '????????????', 'Arches': '????????????', 'Arathi': '????????????'}
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
            output = f'????????????\nmc??????-{COMMAND}ping <ip/addr>\nhyp????????????-{COMMAND}hyp <player>\n????????????-{COMMAND}sw <player>\n????????????-{COMMAND}bw <player>\n????????????-{COMMAND}mw <player>\n????????????-{COMMAND}duels <player>\n??????????????????-{COMMAND}bsg <player>\nUHC-{COMMAND}uhc <player>\n????????????-{COMMAND}mm <player>\nTNT??????-{COMMAND}tnt <player>\n????????????-{COMMAND}guild <player>\nsyuu??????-{COMMAND}syuu <player>\nsyuu?????????-{COMMAND}syuulb'

        elif command in command_list_test:
            # v = await app.uploadVoice(base64.b64decode(open(r"C:\Users\18622\Downloads\arcaea_3.11.0c\assets\songs\aegleseeker\aegleseeker.ogg",'rb').read()))
            await app.sendFriendMessage(3442535256,MessageChain.create([Voice()]))

        elif command in command_list_api:
            if str(user_id) not in ADMIN:
                output = '?????????????????????????????????!'
                writelog(30, user, group, input, output)
                return output
            data = requests.get('https://api.hypixel.net/key?key=%s' % key).json()
            if data['success'] is True:
                owner = data['record']['owner']
                limit = data['record']['limit']
                queries = data['record']['queriesInPastMin']
                total = data['record']['totalQueries']
                output = '??????api??????:\napi?????????UUID:%s\n???????????????:%s\n??????1min????????????:%s\n????????????:%s' % intformat(
                    [owner, str(limit), str(queries), str(total)])
            else:
                output = 'api??????????????????'

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
            output = f'?????????????????????????????????{random_c}%\n*???????????? by Akashic'
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

                output = 'hypixel?????????????????????:\nWatchdog?????????????????????:%s\nWatchdog????????????:%s\nWatchdog?????????:%s\nStaff????????????:%s\nStaff?????????:%s' % intformat(
                    [watchdog_minute, watchdog_daily, watchdog_total, staff_daily, staff_total])
                writelog(20, user, group, input, output)

                return output
            except:
                output = 'hypixel?????????????????????????????????!'
                writelog(30, user, group, input, output)

                return output

        elif command in command_list_status:
            if str(user_id) not in ADMIN:
                output = '?????????????????????????????????!'
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
                output = 'Bot????????????:%s\n?????????:hycx233\n??????????????????:%s\n??????????????????:%s\n??????????????????:%s\n??????????????????:Python%s\n%s' % (
                VERSION, info_update, info_time, info_env, info_py, info_sys)
                writelog(20, user, group, input, output)

                return output
            except Exception as e:
                output = f'??????????????????????????????!{e}'
                writelog(30, user, group, input, output)

                print(e)
                return output

        elif command in command_list_friend:
            if str(user_id) not in ADMIN:
                output = '?????????????????????????????????!'
                writelog(30, user, group, input, output)
                return output

            friendList = await app.getFriendList()
            friend_str = '????????????:\n'
            for f in friendList:
                f_id = f.id
                f_name = f.nickname
                friend_str += f'{f_id} - {f_name}\n'
            friend_str += f'????????????: {str(len(friendList))}'
            print(friend_str)
            output = friend_str

        elif command in command_list_group:
            if str(user_id) not in ADMIN:
                output = '?????????????????????????????????!'
                writelog(30, user, group, input, output)
                return output

            groupList = await app.getGroupList()
            group_str = '????????????:\n'
            for group1 in groupList:
                g_id = group1.id
                g_name = group1.name
                g_perm = group1.accountPerm
                group_str += f'{g_id} - {g_name}\n'
            group_str += f'?????????????????????: {str(len(groupList))}'
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
                leaderBoard_str = '%s????????????' % gameType
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
            time_cached = '????????????:'
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
            output = '????????????!'
            writelog(30, user, group, input, output)
            return '????????????'

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
                str_history = '????????????????????????,???????????????%s\nUUID:%s' % (name_only, uuid)
            else:
                change_times = num_name - 1
                str_history = '???????????????%s???????????????\n' % change_times
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
                        str_history = '%s\n????????????:%s\nUUID:%s' % (str_history, name, uuid)
                        break
                    if i == 1:
                        str_history = '%s????????????:%s - %s' % (str_history, name, changed_time)
                    else:
                        str_history = '%s\n[%s]%s - %s' % (str_history, x, name, changed_time)

            output = str_history
            writelog(20, user, group, input, output)
            return output
        except:
            output = '??????????????????????????????????????????????????????????????????!'
            writelog(30, user, group, input, output)
            return output


    elif mode_input == '2' and command in command_list_ping:
        try:
            print(input)
            output = serverGet(str.split(input)[1])
            print(output)
            if output.startswith('*'):
                writelog(30, user, group, input, output)
                return '????????????'

            writelog(20, user, group, input, output)
            return output
        except:
            output = '???????????????????????????!'
            writelog(30, user, group, input, output)
            return '????????????'


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
            output = '????????????????????????????????????'
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
            text += '[%s] Elo:%s ??????:%s ??????:%s\n' % (
                types, data_syuu1[3 * i - 3], data_syuu1[3 * i - 2], data_syuu1[3 * i - 1])
        if text == '':
            text = '????????????Rank??????'
        try:
            firstlogin = time_syuu_list[0]
        except:
            firstlogin = 'Invalid'
        try:
            lastlogin = time_syuu_list[1]
        except:
            lastlogin = 'Invalid'
        data_syuu = [name, firstlogin, lastlogin, text]

        output = '%s???Syuu(Rank)??????:\n??????????????????:%s\n??????????????????:%s\n%s' % tuple(data_syuu)
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
            output = '???????????????!'
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
            output = '????????????????????????!'
            writelog(30, user, group, input, output)
            return output

        if ifsuccess is True:
            result = data_stats['player']
            if result is None:
                output = '??????????????????????????????????????????'
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
                    output = '?????????????????????????????????!????????????:%s' % Error
                    log = '{"time":"%s","level":"error","user":"%s","group":"%s","input":"%s","result":"%s"}' % (
                    time_now, user, group, text_input, output.replace('\n', '  '))
                    writelog(40, user, group, input, output)
                    await app.sendFriendMessage(OWNER, MessageChain.create(Plain('????????????!', log)))
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
                    output = 'API key??????,???????????????????????????API key!'
                    writelog(50, user, group, input, output)
                    return '????????????'
                elif output == 'Key throttle':
                    output = 'API key??????????????????,???????????????!'
                    writelog(40, user, group, input, output)
                    return '????????????'
                else:
                    output = '???api.hypixel.net???????????????????????????:%s' % output
                    writelog(30, user, group, input, output)
                    return '????????????'
            except:
                output = '???api.hypixel.net?????????????????????????????????'
                writelog(30, user, group, input, output)
                return '????????????'

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
                    online = '[??????]'
                else:
                    if online_apioff is True:
                        online = '[??????]'
                        playing = '*??????????????????????????????API'
                    else:
                        if tryapi is False:
                            online = '[??????]'
                            playing = '*??????????????????????????????/????????????API'
                        else:
                            online = '[??????]'
                            try:
                                recentgame = translate_game(data_stats['player']['mostRecentGameType'])
                                playing = ' ????????????:%s' % recentgame
                            except:
                                playing = '*??????????????????????????????API'

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
                rsw = 'Rank??????:%s Rank??????:%s' % (score_rsw, position_rsw)
            else:
                rsw = 'Rank???????????????!'
        else:
            pass


    elif mode_input == '2' and command in command_list_randomstr:
        try:
            num = math.floor(float(str.split(input)[1]))
        except:
            return 'Error'
        str_random = ''.join(random.sample(string.ascii_letters + string.digits, num))
        output = f'?????????{num}??????????????????:\n{str_random}'
        return output


    elif command in command_list_send:
        if str(user_id) in ADMIN:
            output = '??????' + str.split(input, ' ', 1)[1]
        else:
            output = '?????????????????????????????????!'
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
        output = f'{num3}?????????????????????[{num1},{num2}]:\n{str(num_out)}'
        return output


    else:
        output = '????????????'
        writelog(30, user, group, input, output)
        return '????????????'

    '''--------------------------------------------------MATCH RESULT--------------------------------------------------'''
    output = '??????????????????,???????????????????????????!'
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

            output = "%s%s%s%s[Lv.%s]\n%s%s\n????????????:%s ?????????:%s\n??????????????????:%s\n??????????????????:%s\n??????????????????:%s" % intformat(
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
            # text_sw = '%a%a%a%a[%s]\n??????:%s ??????:%s ?????????:%s\n?????????:%s ?????????:%s ???K/D:%a\n?????????:%s ?????????:%s ???W/L:%a\n%a'
            # output = jsonhandler(data_stats,sw_list,text_sw,'player','stats','SkyWars')
            # output = delcolor(fillin(output,[rank_pro,prefix,rank,name,quotient_json(data_stats,['kills','deaths'],'player','stats','SkyWars'),quotient_json(data_stats,['wins','losses'],'player','stats','SkyWars'),rsw]))

            output = "%s%s%s%s[%s]\n??????:%s ??????:%s ?????????:%s\n?????????:%s ?????????:%s ???K/D:%s\n?????????:%s ?????????:%s ???W/L:%s\n%s" % intformat(
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

            output = "%s%s%s%s[Lv.%s]\n??????:%s ????????????:%s ????????????:%s\n?????????:%s ?????????:%s ???K/D:%s\n???????????????:%s ???????????????:%s ?????????K/D:%s\n?????????:%s ?????????:%s ???W/L:%s" % intformat(
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

            output = "%s%s%s%s\n??????:%s ???????????????:%s\n?????????:%s ?????????:%s ???K/D:%s\n???????????????:%s ???????????????:%s ?????????K/D:%s\n?????????:%s ?????????:%s ???W/L:%s\n?????????:%s ???????????????:%s" % intformat(
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

            output = "%s%s%s%s\n??????:%s ??????:%s\n?????????:%s ?????????:%s ???K/D:%s\n?????????:%s ???????????????:%s" % intformat(
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

            output = "%s%s%s%s\n??????:%s\n???????????????:%s ???????????????:%s\n?????????:%s ?????????:%s ???K/D:%s\n?????????:%s ?????????:%s ???W/L:%s" % intformat(
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

            output = "%s%s%s%s\n??????:%s ?????????:%s\n?????????:%s ?????????:%s ???K/D:%s\n???????????????:%s ???????????????:%s ???K/G:%s" % intformat(
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

            output = "%s%s%s%s\n??????:%s ?????????:%s\n?????????:%s ?????????:%s\n????????????:%s ????????????:%s ???????????????:%s\n???????????????:%s ???????????????:%s ??????????????????:%s" % intformat(
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

            output = "%s%s%s%s\n??????:%s\nTNTRun: ??????:%s ??????:%s\nPVPRun: ??????:%s ?????????:%s ??????:%s\nTNTag: ?????????:%s ?????????:%s\nBowspleef: ?????????:%s\nWizards: ?????????:%s ?????????:%s\n?????????:%s ?????????:%s K/D:%s" % intformat(
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
                        lobby_str += '\n?????????[%s]%s' % (int(point[0]) + 1, str(time_used)[2:-3])
                    print(lobby)
                    dict_1[lobby] = lobby_str
                for total in total_list:
                    print(total_list[total])
                    time_took = datetime.datetime.fromtimestamp(
                        total_list[total][0]['timeTook'] / 1000) - datetime.datetime.fromtimestamp(0.0)
                    time_start = datetime.datetime.fromtimestamp(total_list[total][0]['timeStart'] / 1000)
                    str_out = '?????????:%s\n????????????:%s' % (str(time_took)[2:-3], str(time_start)[:-7])
                    dict_2[total] = str_out
                print(dict_2)
                str_out = ''
                for a in dict_1:
                    try:
                        str_out += (dict_1[a] + '\n' + dict_2[a] + '\n\n')
                    except:
                        str_out += (dict_1[a] + '\n' + '??????????????????' + '\n\n')
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
                output = '%s%s%s%s\nInvalid\n?????????????????????????????????!' % (rank_pro, prefix, rank, name_pure)
                writelog(30, user, group, input, output)
                return output



        elif command in command_guild:
            ifsuccess_guild = data_guild['success']
            if ifsuccess_guild is True:
                guild = data_guild['guild']
                if guild is None:
                    output = '??????%s%s%s%s???????????????' % (rank_pro, prefix, rank, name)
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

                    output = '%s%s%s%s??????????????????:\n??????:%s ??????tag:%s\n??????:%s ??????:%s\n??????:%s\n????????????:%s\n??????????????????:%s' % (
                    rank_pro, prefix, rank, name_pure, name_guild, tag_guild, level, num_guild, description,
                    created_guild, game_prefer)



    except Exception as error:
        output = '???????????????????????????????????????!????????????:%s' % error
        log = '{"time":"%s","level":"error","user":"%s","group":"%s","input":"%s","result":"%s"}' % (
        time_now, user, group, text_input, output.replace('\n', '  '))
        writelog(40, user, group, input, output)
        print(error)
        await app.sendFriendMessage(OWNER, MessageChain.create(Plain('????????????!', log)))
        return '????????????'

    end = datetime.datetime.now()
    used = end - start
    used = '%s???' % str(used)[5:10]
    if output == 'error':
        pass
    else:
        output = '%s\n????????????:%s  by %s' % (output, used, BOTNAME)
        try:
            writelog(20, user, group, input, output)
        except:
            pass
        return output


command_list_ping = (f'{COMMAND}PING', f'{COMMAND}SERVER', f'{COMMAND}MCPING', f'{COMMAND}??????')
command_list_syuulb = (f'{COMMAND}SYUULB', f'{COMMAND}SYUU', f'{COMMAND}SYUULEADERBOARD')

command_hyp = (f'{COMMAND}HYPIXEL', f'{COMMAND}HYP', f'{COMMAND}???', f'{COMMAND}??????', f'{COMMAND}??????')
command_sw = (f'{COMMAND}SW', f'{COMMAND}SKYWARS', f'{COMMAND}??????', f'{COMMAND}????????????')
command_bw = (f'{COMMAND}BW', f'{COMMAND}BEDWARS' f'{COMMAND}??????', f'{COMMAND}????????????')
command_mw = (f'{COMMAND}MW', f'{COMMAND}MEGAWALLS', f'{COMMAND}??????', f'{COMMAND}????????????')
command_uhc = (f'{COMMAND}UHC', f'{COMMAND}????????????', f'{COMMAND}??????????????????')
command_duel = (f'{COMMAND}DUEL', f'{COMMAND}DUELS', f'{COMMAND}??????', f'{COMMAND}????????????')
command_bsg = (
f'{COMMAND}BSG', f'{COMMAND}HG', f'{COMMAND}HUNGERGAMES', f'{COMMAND}????????????', f'{COMMAND}??????????????????', f'{COMMAND}??????')
command_hg = (f'{COMMAND}MM', f'{COMMAND}MURDER', f'{COMMAND}??????', f'{COMMAND}????????????')
command_tnt = (f'{COMMAND}TNT', 'TNTGAMES')
command_guild = (f'{COMMAND}GUILD', f'{COMMAND}??????')
command_parkour = (f'{COMMAND}PARKOUR', f'{COMMAND}??????')

command_list_needimage = (command_parkour,command_guild + command_tnt + command_hg + command_bsg + command_uhc + command_duel + command_sw + command_bw + command_hyp + command_mw)



loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = Ariadne(
    broadcast=bcc,
    connect_info=MiraiSession(
        host=config['Mirai-Api-Http_host'],  # ?????? HTTP API ?????????????????????
        verify_key=config["Mirai-Api-Http_authKey"],  # ?????? verifyKey
        account=config['Mirai-Api-Http_account'],  # ?????????????????? qq ???
    )
)

@bcc.receiver("GroupMessage")
async def group_message_handler(message: MessageChain, app: Ariadne, group: Group, member: Member):
    if message.asDisplay().startswith(f'{COMMAND}'):

        input = str.upper(message.asDisplay())
        if str.split(input)[0] in command_list_ping:
            output = await hyp(message.asDisplay(), [str(member.id), member.name], [str(group.id), group.name])
            print(output)
            if ('????????????' or '????????????') in output:
                pass
            else:
                if output.startswith(r'{') or output.startswith('?????????????????????'):
                    await app.sendGroupMessage(group, MessageChain.create([Plain('?????????????????????????????????!')]), quote=message.dict()['__root__'][0]['id'])
                else:
                    await app.sendGroupMessage(group, MessageChain.create([At(member.id), IMAGE(path='1.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])

        elif str.split(input)[0] in command_list_syuulb and len(str.split(input)) == 1:
            output = await hyp(message.asDisplay(), [str(member.id), member.name], [str(group.id), group.name])
            await app.sendGroupMessage(group, MessageChain.create([At(member.id), IMAGE(path='syuu.png')]), quote=message.dict()['__root__'][0]['id'])

        elif str.split(input)[0] in command_parkour and len(str.split(input)) == 2:
            output = await hyp(message.asDisplay(), [str(member.id), member.name], [str(group.id), group.name])
            if '??????' not in output:
                await app.sendGroupMessage(group, MessageChain.create([At(member.id), IMAGE(path='parkour.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])
            else:
                await app.sendGroupMessage(group, MessageChain.create([At(member.id), Plain('\n' + output)]), quote=message.dict()['__root__'][0]['id'])

        else:
            output = await hyp(message.asDisplay(), [str(member.id), member.name], [str(group.id), group.name])
            if ('????????????' or '????????????') in output:
                pass
            else:
                if (str.split(input)[0] in command_list_needimage) and ('??????' not in output) and ('??????' not in output):
                    await app.sendGroupMessage(group, MessageChain.create([At(member.id), Plain('\n'), IMAGE.fromLocalFile('player.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])
                elif '??????' in output:
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
            if ('????????????' or '????????????') in output:
                pass
            else:
                if output.startswith(r'{') or output.startswith('?????????????????????'):
                    await app.sendFriendMessage(friend, MessageChain.create([Plain('?????????????????????????????????!')]), quote=message.dict()['__root__'][0]['id'])
                else:
                    await app.sendFriendMessage(friend, MessageChain.create([IMAGE(path='1.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])

        elif str.split(input)[0] in command_list_syuulb and len(str.split(input)) == 1:
            output = await hyp(message.asDisplay(), [str(friend.id), friend.nickname])
            await app.sendFriendMessage(friend, MessageChain.create([IMAGE(path='syuu.png')]), quote=message.dict()['__root__'][0]['id'])

        elif str.split(input)[0] in command_parkour and len(str.split(input)) == 2:
            output = await hyp(message.asDisplay(), [str(friend.id), friend.nickname])
            if '??????' not in output:
                await app.sendFriendMessage(friend, MessageChain.create([IMAGE(path='parkour.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])
            else:
                await app.sendFriendMessage(friend, MessageChain.create([Plain(output)]), quote=message.dict()['__root__'][0]['id'])

        else:
            output = await hyp(message.asDisplay(), [str(friend.id), friend.nickname])
            if ('????????????' or '????????????') in output:
                pass
            else:
                if (str.split(input)[0] in command_list_needimage) and ('??????' not in output) and ('??????' not in output):
                    await app.sendFriendMessage(friend, MessageChain.create([IMAGE.fromLocalFile('player.png'), Plain(output)]), quote=message.dict()['__root__'][0]['id'])
                elif '??????' in output:
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
    output = '????????????????????????:\n??????qq:%s\n?????????:%s\n??????:%s\n??????:%s\n????????????:%s\n??????:%s' % (user, username, group, groupname, message, timenow)
    await event.accept('????????????????????????/???????????????????????????????????????????????????????????????????????????????????????????????????hycx233???3442535256')
    await app.sendFriendMessage(int(user), MessageChain.create([Plain('????????????????????????/???????????????????????????????????????????????????????????????????????????????????????????????????hycx233???3442535256')]))
    await app.sendFriendMessage(3442535256, MessageChain.create([Plain(output)]))


loop.run_until_complete(app.lifecycle())