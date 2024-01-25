import re
from typing import Optional

from hoshino import Service

from .calculate import forward_calculate, reverse_calculate
from .pal_class import PalChar
from .utils import find_char_by_raw_name

sv = Service('pal_breeding')


help_msg = f'''
帕鲁配种 帕鲁1+帕鲁2=?
帕鲁配种 ?+?=帕鲁1
'''.strip()


# 帮助界面
@sv.on_fullmatch('帕鲁帮助')
async def get_help(bot, ev):
    await bot.send(ev, '帕鲁配种 帕鲁1+帕鲁2=?')


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
    mother: Optional[PalChar]
    father: Optional[PalChar]
    child: Optional[PalChar]
    found, mother = find_char_by_raw_name(mother_raw) if mother_raw != '?' else True, None
    if not found:
        await bot.send(ev, f'根据父母名称[{mother_raw}]查不到对应帕鲁！')
        return
    found, father = find_char_by_raw_name(father_raw) if father_raw != '?' else True, None
    if not found:
        await bot.send(ev, f'根据父母名称[{father_raw}]查不到对应帕鲁！')
        return
    found, child = find_char_by_raw_name(child_raw) if child_raw != '?' else True, None
    if not found:
        await bot.send(ev, f'根据子代名称[{child_raw}]查不到对应帕鲁！')
        return

    # 分门别类
    if not mother and not father and not child:
        await bot.send(ev, '请至少输入父亲或母亲或子代里的任意一个数据！')
        return

    if not mother and not father:
        # 根据子代查所有配方
        parent_list = reverse_calculate(child.pal_id)
        msg = '\n'.join([f'> {pair[0].cn_name} + {pair[1].cn_name} = {child.cn_name}'
                         for pair in parent_list])
        await bot.send(ev, msg)
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
