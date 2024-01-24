from utils import *


# 正向查询 | 根据父母查询子代
def forward_calculate(mother_id: str, father_id: str) -> PalChar:
    pal_data = read_data()
    special_data = read_special()

    # 先找特殊表 | 找到就不用后面的了
    special_char = find_child_by_special(special_data, pal_data, mother_id, father_id)
    if special_char:
        return special_char

    # 父母power
    mother_data = pal_data.get(mother_id, None)
    father_data = pal_data.get(father_id, None)
    mother_power = mother_data.power
    father_power = father_data.power
    print(f'mother_power={mother_power}, father_power={father_power}')

    # 子代power
    child_power = (mother_power + father_power) / 2
    # 寻找最接近的前后两条数据
    prev_data: PalChar
    next_data: PalChar
    prev_data, next_data = find_nearest_power(special_data, pal_data, child_power)
    # 一方为None就取另一方
    if prev_data is None or next_data is None:
        child = prev_data if prev_data is not None else next_data
    else:
        # 优先power数值接近的
        prev_delta = abs(prev_data.power - child_power)
        next_delta = abs(next_data.power - child_power)
        child = prev_data if prev_delta < next_delta else next_data
        # 相等的话 | 优先先出的角色
        if prev_delta == next_delta:
            index_list = read_index()
            prev_index = index_list.index(prev_data.en_name)
            next_index = index_list.index(next_data.en_name)
            child = prev_data if prev_index < next_index else next_data
    return child
