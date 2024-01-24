import re

from hoshino import Service

from .calculate import forward_calculate
from .utils import find_char_by_raw_name

sv = Service('pal_breeding')


# 帮助界面
@sv.on_fullmatch('帕鲁帮助')
async def get_help(bot, ev):
    await bot.send(ev, '')


@sv.on_prefix('帕鲁配种')
async def get_calculate(bot, ev):
    message = str(ev.message)
    if not message:
        return
    match = re.match(r'(.+)\+(.+)=(.+)', message)
    if not match:
        return

    # 处理查询
    mother_raw = match.group(1)
    father_raw = match.group(2)
    child_raw = match.group(3)
    # 查找对应帕鲁
    mother = find_char_by_raw_name(mother_raw) if mother_raw != '?' else None
    father = find_char_by_raw_name(father_raw) if father_raw != '?' else None
    child = find_char_by_raw_name(child_raw) if child_raw != '?' else None

    if not mother and not father and not child:
        await bot.send(ev, '请至少输入一个数据！')
        return

    if not mother and not father:
        # TODO 所有配方
        await bot.send(ev, '暂不支持查询所有配方！')
        return

    if not mother or not father and not child:
        # TODO 单个父代可能的配方
        await bot.send(ev, '该功能还没做！')
        return

    if not mother or not father and child:
        # TODO 通过父代子代查母
        await bot.send(ev, '该功能还没做！')
        return

    if mother or father and not child:
        # 根据父母查子代
        child = forward_calculate(mother.pal_id, father.pal_id)
        await bot.send(ev, f'> {mother.cn_name} + {father.cn_name} = {child.cn_name}')
    else:
        await bot.send(ev, '格式错误，请检查！')
