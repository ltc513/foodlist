# -*- coding: utf-8 -*-
"""把 Desktop/pic 下的照片处理进网页：压缩、重命名、生成列表，并用指定图做 App 图标。
新增照片后重新运行本脚本即可，会自动升 SW 缓存版本。
"""
import os
import re
import glob
import json
from PIL import Image

SRC = r'C:\Users\litiancheng\Desktop\pic'
WEB = r'C:\Users\litiancheng\Desktop\美食清单-web'
PICS = os.path.join(WEB, 'pics')
ICON_SRC = os.path.join(SRC, '微信图片_20261019201533_60145_2.jpg')
MAX_SIDE = 900
QUALITY = 82

os.makedirs(PICS, exist_ok=True)

# 清掉旧的生成图，避免删照片后残留
for old in glob.glob(os.path.join(PICS, '[0-9][0-9].jpg')):
    os.remove(old)

files = sorted(glob.glob(os.path.join(SRC, '*.jpg')))
names = []
for idx, path in enumerate(files, 1):
    name = '%02d.jpg' % idx
    img = Image.open(path).convert('RGB')
    img.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    img.save(os.path.join(PICS, name), 'JPEG', quality=QUALITY, optimize=True, progressive=True)
    names.append('pics/' + name)

with open(os.path.join(PICS, 'list.js'), 'w', encoding='utf-8') as f:
    f.write('self.FOOD_PICS = %s;\n' % json.dumps(names, ensure_ascii=False))

# 主屏图标：整图居中放进方形画布，底色取图片四角平均色
img = Image.open(ICON_SRC).convert('RGB')
w, h = img.size
corners = [img.getpixel((0, 0)), img.getpixel((w - 1, 0)), img.getpixel((0, h - 1)), img.getpixel((w - 1, h - 1))]
bg = tuple(sum(c[i] for c in corners) // 4 for i in range(3))
canvas = Image.new('RGB', (1024, 1024), bg)
scale = 1024 / max(w, h)
small = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
canvas.paste(small, ((1024 - small.width) // 2, (1024 - small.height) // 2))

os.makedirs(os.path.join(WEB, 'icons'), exist_ok=True)
for size, fname in ((512, 'icon-512.png'), (192, 'icon-192.png'), (180, 'icon-180.png')):
    canvas.resize((size, size), Image.LANCZOS).save(os.path.join(WEB, 'icons', fname))

# 升 SW 缓存版本，保证换图后生效
sw_path = os.path.join(WEB, 'sw.js')
with open(sw_path, encoding='utf-8') as f:
    sw = f.read()
m = re.search(r"foodlist-v(\d+)", sw)
if m:
    sw = sw.replace(m.group(0), 'foodlist-v%d' % (int(m.group(1)) + 1))
    with open(sw_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(sw)

print('photos: %d, icon bg: %s' % (len(names), bg))
