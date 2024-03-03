import ipaddress

def render_forward_msg(msg_list: list, uid=2854196306, name='bot'):
    forward_msg = []
    for msg in msg_list:
        forward_msg.append({
            "type": "node",
            "data": {
                "name": str(name),
                "uin": str(uid),
                "content": msg
            }
        })
    return forward_msg

def is_valid_ip(ip):  
    try:  
        ipaddress.ip_address(ip)  
        return True  
    except ValueError:  
        return False
    
def is_valid_port(port):  
    if 0 <= port <= 65535:  
        return True  
    else:  
        return False  