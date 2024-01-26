from PIL import Image, ImageDraw, ImageFont
from hoshino import R
from prettytable import PrettyTable

from .utils import *


# 生成图片
async def create_breed_img():
    pal_data = await read_data_sort_by_power()
    pal_index = await read_index()

    field_names = ('角色UID', '游戏编号', '中文名', '英文名', '繁殖力', '档案索引')
    table = PrettyTable(field_names=field_names)

    table.title = '帕鲁繁殖力汇总表'
    for pal in pal_data:
        en_name = pal.en_name
        table.add_row([pal.pal_id, pal.number, pal.cn_name, en_name, pal.power, pal_index.index(en_name) + 1])

    table_info = str(table)
    space = 5
    current_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simhei.ttf')
    font = ImageFont.truetype(current_dir, 20, encoding='utf-8')
    im = Image.new('RGB', (10, 10), (255, 255, 255, 0))
    draw = ImageDraw.Draw(im, 'RGB')
    img_size = draw.multiline_textsize(table_info, font=font)
    im_new = im.resize((img_size[0] + space * 2, img_size[1] + space * 2))
    del draw
    del im
    draw = ImageDraw.Draw(im_new, 'RGB')
    draw.multiline_text((space, space), table_info, fill=(0, 0, 0), font=font)
    path_dir = os.path.abspath(os.path.join(R.img('PalWorld').path, 'breeding/breed_chart.png'))
    im_new.save(path_dir, 'PNG')
    del draw


# 发送图片
async def send_image():
    path_dir = os.path.join(R.img('PalWorld').path, 'breeding/breed_chart.png')
    if not os.path.exists(path_dir):
        await create_breed_img()
    return await get_img_cq(path_dir)
