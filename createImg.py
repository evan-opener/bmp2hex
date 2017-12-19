# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

Width = 640
Height = 384

def creatImage():
    im = Image.new('1', (Width, Height), 1)
    draw = ImageDraw.Draw(im)
    Cfont = ImageFont.truetype('./msyh.ttf', 24)
    draw.rectangle((0, 50, 50, 100), 0)
    draw.arc((100, 100, 300, 300), 0, 180, 0)
    draw.text((50, 50), u'中文', font = Cfont)
    im.save('Image.bmp')
    
    

# Only run if launched from commandline
if __name__ == '__main__': creatImage()