import itertools
import json
import os
from typing import Dict, List, Tuple, Optional

from .pal_class import PalChar


# 读取文件并解析
async def read_data() -> Dict[str, PalChar]:
    characters = {}
    with open(os.path.join(os.path.dirname(__file__), 'base_data', 'pal_data.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)
        for key, value in data.items():
            character = PalChar(
                value['pal_id'], value['number'], value['en_name'], value['cn_name'], value['power'], value['alias']
            )
            characters[key] = character
    return characters


# 按power逆向排序
async def read_data_sort_by_power() -> List[PalChar]:
    pal_data = await read_data()
    pal_list = list(pal_data.values())
    return sorted(pal_list, key=lambda x: x.power, reverse=True)


# 获取角色索引
async def read_index() -> List[str]:
    with open(os.path.join(os.path.dirname(__file__), 'base_data', 'char_index.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)
    return list(data)


# 获取排除列表
async def read_exclude() -> List[str]:
    with open(os.path.join(os.path.dirname(__file__), 'base_data', 'cal_exclude.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)
    return list(data)


# 获取特殊配表
async def read_special() -> dict:
    with open(os.path.join(os.path.dirname(__file__), 'base_data', 'special_data.json'), 'r', encoding='utf-8') as file:
        data = json.load(file)
    return dict(data)


# 寻找最接近的前后两条数据
async def find_nearest_power(
        special_data: dict,
        pal_data: Dict[str, PalChar],
        power: float,
        have_self: bool) -> (PalChar, PalChar):
    exclude_list = await read_exclude()
    sorted_data = sorted(pal_data.values(), key=lambda x: x.power)
    # 寻找最接近的前一条数据
    prev_data = None
    for data in sorted_data:
        # 去除特殊
        if data.pal_id in special_data or data.pal_id in exclude_list:
            continue
        if (have_self and data.power <= power) or (not have_self and data.power < power):
            prev_data = data
        else:
            break
    # 寻找最接近的后一条数据
    next_data = None
    sorted_data_reverse = sorted_data[::-1]
    for data in sorted_data_reverse:
        # 去除特殊
        if data.pal_id in special_data or data.pal_id in exclude_list:
            continue
        if (have_self and data.power >= power) or (not have_self and data.power > power):
            next_data = data
        else:
            break
    return prev_data, next_data


# 特殊表 | 根据父母查子代
async def find_child_by_special(
        special_data: Dict[str, List[str]],
        pal_data: Dict[str, PalChar],
        mother_id: str,
        father_id: str) -> PalChar:
    pal_char = None
    for key, value_list in special_data.items():
        if mother_id in value_list and father_id in value_list:
            pal_char = pal_data.get(key, None)
            break
    return pal_char


# 根据名字和别称寻找唯一
async def find_char_by_raw_name(raw_name: str) -> Tuple[bool, Optional[PalChar]]:
    pal_data = await read_data()
    pal_char = None
    for value in pal_data.values():
        if raw_name == value.en_name or raw_name == value.cn_name:
            pal_char = value
            break
        for alias in value.alias:
            if raw_name == alias:
                pal_char = value
                break
    return pal_char is not None, pal_char


# 查询power组合
async def find_power_combinations(
        special_data: Dict[str, List[str]],
        data: Dict[str, PalChar],
        prev_power: int,
        next_power: int,
        prev_equal: bool,
        next_equal: bool) -> List[Tuple[PalChar, PalChar]]:
    # 排除掉特殊的
    power_values = []
    for key, value in data.items():
        if key not in special_data:
            power_values.append(value.power)
    combinations = list(itertools.combinations(power_values, 2))

    result = []
    # 获取排列组合枚举
    for pair in combinations:
        if (((prev_equal and pair[0] + pair[1] >= prev_power)
             or (not prev_equal and pair[0] + pair[1] > prev_power))
                and
                ((next_equal and pair[0] + pair[1] <= next_power)
                 or (not next_equal and pair[0] + pair[1] < next_power))):
            for pal1, pal2 in itertools.combinations(data.values(), 2):
                if pal1.power == pair[0] and pal2.power == pair[1]:
                    result.append((pal1, pal2))
    return result


# 转图片路径
async def get_img_cq(img_path):
    return f'[CQ:image,file=file:///{os.path.abspath(img_path)}]'
