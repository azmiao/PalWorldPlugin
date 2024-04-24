import yaml
import binascii
import base64
import json

from pypinyin import pinyin, Style
from asyncio import sleep as asleep

import sys, os
_current_dir = os.path.dirname(__file__)
if _current_dir not in sys.path:
    sys.path.insert(-1, _current_dir)

from .async_rcon import rcon
# from rcon.source import rcon
from rcon.exceptions import WrongPassword
from asyncio.exceptions import TimeoutError

import hoshino
from hoshino import Service,priv,aiorequests

from .RSA import RSAworker, PrivateKeyNotMatchError
from .util import *

sv = Service(
    name = 'PalServerManage',  #功能名
    use_priv = priv.NORMAL, #使用权限   
    manage_priv = priv.ADMIN, #管理权限
    visible = True, #False隐藏
    enable_on_default = True, #是否默认启用
    )

help_msg = f'''=== 帕鲁Rcon帮助 ===
帕鲁服务器绑定
帕鲁服务器信息
谁在帕鲁
帕鲁关服
帕鲁广播 + 广播内容
帕鲁rcon指令 + 指令
'''.strip()
# showplayers和broadcast都是残废，遇到非英文就出问题，broadcast显示不会换行

bind_help1 = "请使用以下指令：\n帕鲁服务器绑定\n服务器ip\nrcon端口\nrestapi端口\n公钥加密的AdminPassword"

bind_help2 = '''
帕鲁服务器绑定
192.168.0.10
0
8212
DHR3peGBwROMsUhwykRoYhizuA375KhUngRRaIkBq8BXZcMEFawcklLZ4VMwiZbpFmDrT7cu273bq2YsaMsv+jmXsK1WBdYM3rQn4jwDcj7f80Q2+o6ek6lieWcKPkAVpXe8oFrcQFsk5yaP8DmzW+JoSyP/NJAIwAbg+JIq1PeO3IKORoTEvJDN6ogd2y1Q1uyW7dEiP0xT635soO5qnujXc62ZwYartBYGSccXntYuCptcWV+KnsV67ic8Z+FSF8P/jypngiIflV5pKvnK3dm1gBaImtfoLN1vpZJWHGE1NCprIFF4VS7kL6muym8aV3NhMfu0AdAoUv+N+H7JKA==
'''

_timeout_return = "连接超时，请依次排查\n ·IP是否配置正确\n ·rcon端口是否配置正确\n ·服务端是否启用rcon\n ·PalServer是否在运行中\n ·是否放行rcon端口（tcp）。"

rsa = RSAworker()  # 初始化一个RSAworker。首次调用自动生成RSA2048公私钥对

async def send_rcon_command(SERVER_ADDRESS, SERVER_PORT,RCON_PASSWORD, command, timeout=2):
    """异步发送rcon指令"""
    _success = False
    # 创建RCON连接
    try:
        response = await rcon(command,host=SERVER_ADDRESS, port=SERVER_PORT, passwd=RCON_PASSWORD, timeout=2, enforce_id=False)
    except WrongPassword:
        return [_success, "WrongPassword!"]
    except TimeoutError as e:
        return [_success, f"TimeoutError: {str(e)}\n{_timeout_return}"]
    # except Exception as e:
    #     return [_success, f"Unknow Error:{str(e)}"]
    else:
        _success = True
        return [_success, response.strip()]

async def send_rest_command(SERVER_ADDRESS, SERVER_PORT, SERVER_PASSWORD , action, data={}, timeout=3):
    """异步发送restapi指令"""
    _success = False
    base_url = f"http://{SERVER_ADDRESS}:{SERVER_PORT}/v1/api"
    url = f"{base_url}/{action}"  # 构造restapi的url
    auth = base64.b64encode(f"admin:{SERVER_PASSWORD}".encode('utf-8')).decode()  # Basic认证
    method_map = {"info":"GET", 
                  "players": "GET", 
                  "settings": "GET", 
                  "metrics": "GET", 
                  "announce": "POST", 
                  "kick": "POST", 
                  "ban": "POST", 
                  "unban": "POST", 
                  "save": "POST", 
                  "shutdown": "POST", 
                  "stop": "POST"
                  }
    if action not in method_map:
        return [_success, f"不支持的action: {action}"]
    method = method_map[action]

    headers = {"Authorization": f"Basic {auth}"}
    # 根据请求方法设置对应的请求头信息
    if method == "GET":  
        headers["Accept"] = "application/json"  # 如果是GET请求，设置Accept字段为application/json
    else:
        headers["Content-Type"] = "application/json"  # 如果是POST请求，设置Content-Type字段为application/json
    
    # GET不需要payload，置空。POST按接口文档要求设置payload
    payload = json.dumps(data) if method == "POST" else {}

    try:
        # 发送请求
        resp = await aiorequests.request(method, url, headers=headers, data=payload, timeout=timeout)
        if resp.status_code == 400:  # 代码错误
            return [_success, "Bad request.请反馈"]
        elif resp.status_code == 401:  # 认证失败
            return [_success, "Unauthorized.请检查密码是否正确"]
        elif resp.status_code == 404:  # 路径不存在，也是代码问题
            return [_success, "Not found.错误的请求路径，请反馈"]
        elif resp.status_code == 200:   # 正常
            _success = True
            # 手动处理各种情况的返回数据，把json数据拼好看一点
            if action in ["info", "settings", "metrics"]:
                resp_json = await resp.json()
                msg = "" 
                for key in resp_json:
                    msg += f"{key}: {resp_json[key]}\n"
                msg = msg.strip()
                return [_success, msg]
            elif action == "players":
                resp_json = await resp.json()
                msg = "=====玩家列表=====\n"
                players = resp_json.get("players")
                for player in players:
                    # 没返回ip和坐标。playerId可以定位存档文件，userId是steamid
                    msg += f"name: {player.get('name')}\nlevel: {player.get('level')}\nplayerId: {player.get('playerId')}\nuserId:{player.get('userId')}\nping:{player.get('ping')}\n"
                    msg += "==================\n"
                msg = msg.strip()
                return [_success, msg]
            else:  # POST请求返回一个OK
                return [_success, (await resp.content).decode()]
        else:  # 其他错误
            return [_success, f"未知错误，状态码：{resp.status_code}"]
    except Exception as e:  # 有异常
        return [_success, f"请求失败，错误信息：{str(e)}"]


async def read_config():
    '''读配置文件'''
    with open(os.path.join(_current_dir, "config.yaml"), "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data

async def write_config(data):
    '''写配置文件'''
    with open(os.path.join(_current_dir, "config.yaml"), "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f)

async def decrypt_admin_password(cipher):
    '''解密服务器私钥'''
    try:
        RCON_PASSWORD = rsa.decrypt(cipher)
        return [True, "", RCON_PASSWORD]
    except PrivateKeyNotMatchError:
        msg = "AdminPassword解密失败，可能是由于服务端密钥重置导致的。请重新绑定。"
        return [False, msg, ""]
    except binascii.Error:
        msg = "AdminPassword解密失败，可能是错误地修改配置文件中的密文导致的，请重新绑定"
        return [False, msg, ""]
    except Exception as e:
        return [False, "Unkonwn Error: \ne", ""]

@sv.on_prefix("帕鲁服务器绑定")
async def pal_server_register(bot, ev):
    is_admin = hoshino.priv.check_priv(ev, hoshino.priv.ADMIN)
    if not is_admin:
        await bot.send("权限不足")
        return 
    messages = str(ev.message).split()  # split("\n")在ntqq好像有兼容性问题
    if len(messages) != 4:
        help_img = "[CQ:image,file=https://s2.loli.net/2024/03/02/NWfxYkHFSndiUap.jpg]"
        bind_help_forward = render_forward_msg(msg_list = [bind_help1, "如果不使用RCON或RESTAPI，请将0作为端口号发送", "为保证AdminPassword不被泄漏，请使用服务端公钥加密后，发送密文", "加密公钥如下：", rsa.get_pub_key(), "请使用RSA加密工具加密AdminPassword，如https://www.toolhelper.cn/AsymmetricEncryption/RSA/", help_img, "例如\n"+bind_help2])
        await bot.send_group_forward_msg(group_id=ev.group_id, messages=bind_help_forward)
        return
    if not is_valid_ip(messages[0].strip()):
        await bot.send(ev, f"{messages[0]}不是一个有效的IP地址，请检查")
        return
    if not is_valid_port(int(messages[1].strip())):
        await bot.send(ev, f"{messages[1]}不是一个有效的端口号，请检查")
        return
    if not is_valid_port(int(messages[2].strip())):
        await bot.send(ev, f"{messages[2]}不是一个有效的端口号，请检查")
        return
    try:
        plain_AdminPassword = rsa.decrypt(messages[3].strip())
    except:
        await bot.send(ev, f"密文解密失败！请仔细阅读说明后再试。")
        return 
    server_address = messages[0].strip()
    rcon_port = messages[1].strip()
    rest_port = messages[2].strip()
    work_mode = "rest"
    if int(rest_port) == 0:
        work_mode = "rcon"
        if int(rcon_port) == 0:
            await bot.send(ev, f"不能同时将rcon和restapi端口设置为0")
            return 
    admin_password = messages[3].strip()
    data = await read_config()
    _ori = data['groups'].get(ev.group_id)  # 可能存在的原配置
    data['groups'][ev.group_id] = {"server_address":str(server_address), "rcon_port":rcon_port, "rest_port":rest_port, "admin_password":str(admin_password), "work_mode":work_mode}
    await write_config(data)
    if _ori is not None:
        msg = f"群帕鲁服务器连接信息已经更新！\n原IP: {_ori['server_address']}\n原RCON端口: {_ori['rcon_port']}\n原RESTAPI端口: {_ori.get('rest_port')}"
        msg += f"\n\n新IP: {server_address}\n新RCON端口: {rcon_port}\n新RESTAPI端口: {rest_port}\n新工作模式: {work_mode}"
    else:
        msg = f"群帕鲁服务器连接信息配置成功！\nIP: {server_address}\nRCON端口: {rcon_port}\nRESTAPI端口: {rest_port}\n工作模式: {work_mode}"
    await bot.send(ev, msg)

@sv.on_fullmatch("帕鲁服务器解绑")
async def pal_server_unregister(bot, ev):
    is_admin = hoshino.priv.check_priv(ev, hoshino.priv.ADMIN)
    if not is_admin:
        await bot.send("权限不足")
        return 
    gid = ev.group_id
    data = await read_config()
    group_server_data = data['groups'].get(gid)
    if group_server_data is None:
        msg = "群聊还未绑定帕鲁服务器，无需解绑。"
    else:
        data['groups'].pop(gid)
        await write_config(data)
        msg = "群聊已解绑帕鲁服务器。"
    await bot.send(ev,msg)

@sv.on_fullmatch("帕鲁服务器信息")
async def pal_server_info(bot, ev):
    gid = ev.group_id
    data = await read_config()
    group_server_data = data['groups'].get(gid)
    if group_server_data is None:
        msg = "群聊还未绑定帕鲁服务器，请发送“帕鲁服务器绑定”进一步了解。"
    else:
        SERVER_ADDRESS = group_server_data.get("server_address")
        REST_PORT = group_server_data.get("rest_port")
        RCON_PORT = group_server_data.get("rcon_port")
        decrypted = await decrypt_admin_password(group_server_data.get("admin_password"))
        if not decrypted[0]:  # 解密失败:
            msg = decrypted[1]
        else:  # 解密成功
            SERVER_PASSWORD = decrypted[2]
            if group_server_data.get("work_mode") == "rest":  # 工作模式为rest
                res = await send_rest_command(SERVER_ADDRESS, REST_PORT, SERVER_PASSWORD, "info")
                msg = res[1] if res[0] else "error: " + res[1]
            else:  # 工作模式为空或rcon
                res = await send_rcon_command(SERVER_ADDRESS, RCON_PORT, SERVER_PASSWORD, "Info")
                msg = res[1] if res[0] else "error: " + res[1]
    await bot.send(ev,msg)

@sv.on_fullmatch("谁在帕鲁")
async def pal_server_info(bot, ev):
    gid = ev.group_id
    data = await read_config()
    group_server_data = data['groups'].get(gid)
    if group_server_data is None:
        msg = "群聊还未绑定帕鲁服务器，请发送“帕鲁服务器绑定”进一步了解。"
    else:
        SERVER_ADDRESS = group_server_data.get("server_address")
        REST_PORT = group_server_data.get("rest_port")
        RCON_PORT = group_server_data.get("rcon_port")
        decrypted = await decrypt_admin_password(group_server_data.get("admin_password"))
        if not decrypted[0]:  # 解密失败:
            msg = decrypted[1]
        else:  # 解密成功
            SERVER_PASSWORD = decrypted[2]
            if group_server_data.get("work_mode") == "rest":  # 工作模式为rest
                res = await send_rest_command(SERVER_ADDRESS, REST_PORT, SERVER_PASSWORD, "players")
                msg = res[1] if res[0] else "error: " + res[1]
            else:  # 工作模式为空或rcon
                await bot.send(ev, "正在查询，如果服内有ID非英文的玩家，可能需要等待数十秒")
                res = await send_rcon_command(SERVER_ADDRESS, RCON_PORT, SERVER_PASSWORD, "ShowPlayers", timeout=60)
                res[1] = res[1].replace("\x00\x00","")
                msg = res[1] if res[0] else "error: " + res[1]
    await bot.send(ev,msg)

@sv.on_fullmatch("帕鲁关服")
async def pal_server_shutdown(bot, ev):
    is_admin = hoshino.priv.check_priv(ev, hoshino.priv.ADMIN)
    if not is_admin:
        await bot.send("权限不足")
        return 
    gid = ev.group_id
    data = await read_config()
    group_server_data = data['groups'].get(gid)
    if group_server_data is None:
        msg = "群聊还未绑定帕鲁服务器，请发送“帕鲁服务器绑定”进一步了解。"
    else:
        SERVER_ADDRESS = group_server_data.get("server_address")
        REST_PORT = group_server_data.get("rest_port")
        RCON_PORT = group_server_data.get("rcon_port")
        decrypted = await decrypt_admin_password(group_server_data.get("admin_password"))
        if not decrypted[0]:  # 解密失败:
            msg = decrypted[1]
        else:  # 解密成功
            SERVER_PASSWORD = decrypted[2]
            if group_server_data.get("work_mode") == "rest":  # 工作模式为rest
                data = {"waittime": 10,
                        "message": "服务器将在10秒后关闭，请及时下线"
                        }
                res = await send_rest_command(SERVER_ADDRESS, REST_PORT, SERVER_PASSWORD, "shutdown",data=data)
                msg = res[1] if res[0] else "error: " + res[1]
            else:  # 工作模式为空或rcon
                RCON_PASSWORD = decrypted[2]
                res = await send_rcon_command(SERVER_ADDRESS, RCON_PORT, RCON_PASSWORD, "Shutdown 10 Server_will_shutdown_in_10s.")
                msg = res[1] if res[0] else "error: " + res[1]
    await bot.send(ev,msg)

@sv.on_prefix("帕鲁广播")
async def pal_server_broadcast(bot, ev):
    # is_admin = hoshino.priv.check_priv(ev, hoshino.priv.DEFAULT)
    # if not is_admin:
    #     await bot.send("权限不足")
    #     return
    # 姑且允许所有人广播
    bc_message = str(ev.message).strip()
    uid = ev.user_id
    gid = ev.group_id
    data = await read_config()
    group_server_data = data['groups'].get(gid)
    if group_server_data is None:
        msg = "群聊还未绑定帕鲁服务器，请发送“帕鲁服务器绑定”进一步了解。"
    else:
        SERVER_ADDRESS = group_server_data.get("server_address")
        REST_PORT = group_server_data.get("rest_port")
        RCON_PORT = group_server_data.get("rcon_port")
        decrypted = await decrypt_admin_password(group_server_data.get("admin_password"))
        if not decrypted[0]:  # 解密失败:
            msg = decrypted[1]
        else:  # 解密成功
            SERVER_PASSWORD = decrypted[2]
            if group_server_data.get("work_mode") == "rest":  # 工作模式为rest
                data = {"message": f"announce fro QQ{uid}: {bc_message}"}
                res = await send_rest_command(SERVER_ADDRESS, REST_PORT, SERVER_PASSWORD, "announce",data=data)
                msg = res[1] if res[0] else "error: " + res[1]
            else:  # 工作模式为空或rcon
                if any(ord(c) > 127 for c in bc_message):
                    # 包含非ascii字符
                    bc_message = ' '.join(word_list[0] for word_list in pinyin(bc_message, style=Style.TONE3, heteronym=False))
                    await bot.send(ev, "广播内容包含游戏内无法显示的字符，已尝试将其中的汉字转换成拼音，其余文字无法处理，游戏内也无法正常显示。")
                # 空格等全部换成下划线
                trans_table = str.maketrans({' ': '_', '\t': '_', '\n': '_', '\r': '_', '\f': '_','，':',','。':'.','？':'?','！':'!'})
                bc_message_replaced = bc_message.translate(trans_table)
                # 游戏内广播不会自动换行，所以手动处理，每48个字符换一行
                bc_message_replaced = "-"*48 + f"broadcast_from_QQ:{uid}__"+bc_message_replaced
                msg = ""
                bc_msg_list = [bc_message_replaced[i:i+48] for i in range(0, len(bc_message_replaced), 48)]
                bc_msg_list.append("-"*48)
                for bc_msg in bc_msg_list:
                    res = await send_rcon_command(SERVER_ADDRESS, RCON_PORT, SERVER_PASSWORD, f"Broadcast {bc_msg}")
                    msg += res[1] if res[0] else "error: " + res[1] + "\n"
                    await asleep(0.5)# 确保分段消息顺序
                msg = msg.strip()
    await bot.send(ev,msg)

@sv.on_prefix("帕鲁rcon")
async def pal_server_rcon(bot, ev):
    is_admin = hoshino.priv.check_priv(ev, hoshino.priv.DEFAULT)
    if not is_admin:
        await bot.send("权限不足")
        return
    cmd = str(ev.message).strip()
    gid = ev.group_id
    data = await read_config()
    group_server_data = data['groups'].get(gid)
    if group_server_data is None:
        msg = "群聊还未绑定帕鲁服务器，请发送“帕鲁服务器绑定”进一步了解。"
    else:
        SERVER_ADDRESS = group_server_data.get("server_address")
        SERVER_PORT = group_server_data.get("rcon_port")
        decrypted = await decrypt_admin_password(group_server_data.get("admin_password"))
        if decrypted[0]:
            RCON_PASSWORD = decrypted[2]
            res = await send_rcon_command(SERVER_ADDRESS, SERVER_PORT, RCON_PASSWORD, cmd)
            msg = res[1] if res[0] else "error: " + res[1]
        else:
            msg = decrypted[1]
    await bot.send(ev,msg)


@sv.on_prefix("帕鲁服务器模式")
async def pal_server_mode(bot, ev):
    is_admin = hoshino.priv.check_priv(ev, hoshino.priv.DEFAULT)
    if not is_admin:
        await bot.send("权限不足")
        return
    # 检查绑定状态
    gid = ev.group_id
    data = await read_config()
    group_server_data = data['groups'].get(gid)
    if group_server_data is None:
        msg = "群聊还未绑定帕鲁服务器，请发送“帕鲁服务器绑定”进一步了解。"
        return 
    else:
        data = await read_config()
        group_server_data = data['groups'].get(gid)
    
    mode = str(ev.message).strip()
    if not mode:  # 查询工作模式
        now_mode = group_server_data.get("work_mode")
        if not now_mode:
            now_mode = "rcon"
        msg = f"群帕鲁服务器工作模式为{now_mode}！"
        await bot.send(ev,msg)
        return
    elif mode not in ["rest", "rcon"]:
        await bot.send(ev, "工作模式只能为rest或rcon")
        return
    else:  # 设置工作模式
        group_server_data["work_mode"] = mode
        await write_config(data)
        msg = f"群帕鲁服务器工作模式已设置为{mode}！"
        await bot.send(ev,msg)


# 以下待定
# rest专属 /v1/api/settings
# @sv.on_fullmatch(("帕鲁服务器设置","帕鲁服务器配置"))
async def pal_server_setting(bot, ev):
    is_admin = hoshino.priv.check_priv(ev, hoshino.priv.DEFAULT)
    if not is_admin:
        await bot.send("权限不足")
        return
    gid = ev.group_id
    data = await read_config()
    group_server_data = data['groups'].get(gid)
    if group_server_data is None:
        msg = "群聊还未绑定帕鲁服务器，请发送“帕鲁服务器绑定”进一步了解。"
        return 
    elif group_server_data.get("work_mode") == "rcon":
        msg = "rcon模式下无法获取服务器配置信息，请切换至rest模式。"
    else:
        # do something
        pass

# rest专属 /v1/api/metrics
# @sv.on_fullmatch(("帕鲁服务器状态","帕鲁服务器指标"))
async def pal_server_metrics(bot, ev):
    gid = ev.group_id
    data = await read_config()
    group_server_data = data['groups'].get(gid)
    if group_server_data is None:
        msg = "群聊还未绑定帕鲁服务器，请发送“帕鲁服务器绑定”进一步了解。"
        return 
    elif group_server_data.get("work_mode") == "rcon":
        msg = "rcon模式下无法获取服务器指标，请切换至rest模式。"
    else:
        # do something
        pass

# Kick，非英文游戏名的话，rcon拿不到steamid，所以只能用rest
# Ban，同上
# UnBan，同上
# Save，rcon和rest都可以，但好像没什么必要
# ForceStop，rcon和rest都可以，但好像没什么必要