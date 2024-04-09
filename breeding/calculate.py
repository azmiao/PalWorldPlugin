from .utils import *


# 正向查询 | 根据父母查询子代
async def forward_calculate(mother_id: str, father_id: str) -> PalChar:
    pal_data = await read_data()
    special_data = await read_special()

    # 先找特殊表 | 找到就不用后面的了
    special_char = await find_child_by_special(special_data, pal_data, mother_id, father_id)
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
    prev_data, next_data = await find_nearest_power(special_data, pal_data, child_power, True)
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
            index_list = await read_index()
            prev_index = index_list.index(prev_data.en_name)
            next_index = index_list.index(next_data.en_name)
            child = prev_data if prev_index < next_index else next_data
    return child


# 逆向查询 | 根据子代查父母
async def reverse_calculate(child_id: str) -> List[Tuple[PalChar, PalChar]]:

    # 当前子代
    pal_data = await read_data()
    child_data = pal_data.get(child_id, None)
    child_power = child_data.power

    # 先找特殊表
    special_data = await read_special()
    if child_id in special_data:
        parent_tuple = special_data.get(child_id)
        return [
            (child_data, child_data),
            (pal_data.get(parent_tuple[0]), pal_data.get(parent_tuple[1])),
        ]

    exclude_list = await read_exclude()
    if child_id in exclude_list:
        return []

    # 再查普通图鉴表
    index_list = await read_index()

    # 1.先获取当前子代对应power前后两个的帕鲁
    prev_data, next_data = await find_nearest_power(special_data, pal_data, child_power, False)
    # 一方为None说明到头了 | 该子代无法杂交生成
    if prev_data is None or next_data is None:
        return [(child_data, child_data)]

    # 2.判断一下三个的索引并求取值区间 | 前后的某一个小于当前子代：不能取到中间值（开区间），否则能取到（闭区间）
    child_index = index_list.index(child_data.en_name)
    prev_index = index_list.index(prev_data.en_name)
    next_index = index_list.index(next_data.en_name)

    prev_equal = False if prev_index < child_index else True
    next_equal = False if next_index < child_index else True

    # 3.计算父母power总和的可能值
    prev_sum_power = child_data.power + prev_data.power
    next_sum_power = child_data.power + next_data.power

    # 4.生成枚举列表并合并特殊
    return await find_power_combinations(special_data, pal_data, prev_sum_power, next_sum_power, prev_equal, next_equal)


# 逆向查询 | 根据子代和父亲查母亲
async def reverse_calculate_with_parent(child_id: str, parent_id: str) -> List[Tuple[PalChar, PalChar]]:
    pal_data = await read_data()
    parent_data = pal_data.get(parent_id)
    # 查所有的列表
    parent_list = await reverse_calculate(child_id)
    return list(filter(lambda parent_tuple: parent_data in parent_tuple, parent_list))
