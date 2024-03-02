import os

from hoshino import R

# 图片跟路径
root_path = R.img('PalWorld').path
if not os.path.exists(root_path):
    os.mkdir(root_path)

# 模块名称
module_list = ['breeding','rcon']

for module in module_list:
    module_path = os.path.join(R.img('PalWorld').path, 'breeding')
    if not os.path.exists(module_path):
        os.mkdir(module_path)
