import re
from typing import List, Tuple

from hoshino import Service

from .calculate import forward_calculate, reverse_calculate
from .pal_class import PalChar
from .utils import find_char_by_raw_name
from ..plugin_utils.page_util import Pagination

sv = Service('pal_breeding')


help_msg = f'''
帕鲁配种 帕鲁1+帕鲁2=?
帕鲁配种 ?+?=帕鲁1
'''.strip()


# 帮助界面
@sv.on_fullmatch('帕鲁配种帮助')
async def get_help(bot, ev):
    await bot.send(ev, help_msg)


@sv.on_prefix('帕鲁配种')
async def get_calculate(bot, ev):
    message = str(ev.message)
    if not message:
        return
    match = re.match(r'p?(\d+)? ?(.+)\+(.+)=(.+)', message)
    if not match:
        return

    # 处理查询
    all_raw = match.group(0).strip()
    page_num = match.group(1)
    page_num = int(page_num) if page_num else 1
    mother_raw = match.group(2)
    father_raw = match.group(3)
    child_raw = match.group(4)
    # 优先整个查询
    all_found = find_char_by_raw_name(all_raw)
    if all_found[0]:
        mother = None
        father = None
        child = all_found[1]
    else:
        # 查找对应帕鲁
        mother_found = find_char_by_raw_name(mother_raw) if mother_raw not in ['?', '？'] else (True, None)
        if not mother_found[0]:
            await bot.send(ev, f'根据父母名称[{mother_raw}]查不到对应帕鲁！')
            return
        father_found = find_char_by_raw_name(father_raw) if father_raw not in ['?', '？'] else (True, None)
        if not father_found[0]:
            await bot.send(ev, f'根据父母名称[{father_raw}]查不到对应帕鲁！')
            return
        child_found = find_char_by_raw_name(child_raw) if child_raw not in ['?', '？'] else (True, None)
        if not child_found[0]:
            await bot.send(ev, f'根据子代名称[{child_raw}]查不到对应帕鲁！')
            return
        mother = mother_found[1]
        father = father_found[1]
        child = child_found[1]
    sv.logger.info(f'配种查询参数：\n母亲：[{mother}]\n父亲：[{father}]\n孩子：[{child}]')

    # 分门别类
    if not mother and not father and not child:
        await bot.send(ev, '请至少输入父亲或母亲或子代里的任意一个数据！')
        return

    if not mother and not father:
        # 根据子代查所有配方
        parent_list = reverse_calculate(child.pal_id)
        if not parent_list:
            await bot.send(ev, f'当前帕鲁[{child.cn_name}]繁殖力过低，仅能与自己繁殖！')
            return
        # 分页
        parent_page = Pagination(parent_list, 20)
        pages = parent_page.get_num_pages()
        page_data: List[Tuple[PalChar, PalChar]]
        page_data = parent_page.get_page(page_num)
        if pages < page_num:
            await bot.send(ev, f'当前页码[{page_num}]超出最大页码[{pages}]！')
            return
        # 生成结果
        msg = f' = 配方(当前第{page_num}页/共{pages}页) = \n'
        msg += '\n'.join([f'> {pair[0].cn_name} + {pair[1].cn_name} = {child.cn_name}'
                         for pair in page_data])
        msg += '\n注：如需要查看其他页请输入"帕鲁配种 p5 ?+?=帕鲁1"，其中5为第五页'
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
