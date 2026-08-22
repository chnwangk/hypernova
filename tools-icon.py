#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H 字母章：按 Helvetica Bold 的比例用矩形构造，保证任何环境下渲染一致"""
from PIL import Image, ImageDraw
import os
SS=10; BG=(4,7,10); FG=(45,212,191)
# Helvetica Bold: 字干/字高 = 0.220，H 宽/字高 ≈ 1.011
CAP=14.0            # 24 网格内的字高
STEM=CAP*0.220      # 3.08
WIDTH=CAP*1.011     # 14.15
BAR=STEM*0.88       # 横杠略细于竖干，视觉上才等重

def geom():
    x0=(24-WIDTH)/2; x1=x0+WIDTH
    y0=(24-CAP)/2;   y1=y0+CAP
    by0=12-BAR/2;    by1=12+BAR/2
    return [(x0,y0,x0+STEM,y1), (x1-STEM,y0,x1,y1), (x0,by0,x1,by1)]

def png(size):
    # 满幅不留圆角：圆角外是透明像素，在 Safari 这类浅色标签栏上会露出白边。
    # 系统需要圆角时会自己裁切（如 iOS 主屏图标），不该由图标自己留透明区。
    S=size*SS
    img=Image.new("RGBA",(S,S),BG+(255,)); d=ImageDraw.Draw(img)
    u=S/24
    for (a,b,c,e) in geom(): d.rectangle([a*u,b*u,c*u,e*u], fill=FG+(255,))
    return img.resize((size,size), Image.LANCZOS)

OUT="/Users/wangkun/hypernova"
png(64).save(OUT+"/favicon.ico", format="ICO", sizes=[(16,16),(32,32),(48,48),(64,64)])
for n,s in [("apple-touch-icon.png",180),("icon-192.png",192),("icon-512.png",512)]:
    png(s).save(OUT+"/"+n, format="PNG", optimize=True)
for f in ["favicon.ico","apple-touch-icon.png","icon-192.png","icon-512.png"]:
    print("  %-22s %d 字节" % (f, os.path.getsize(OUT+"/"+f)))

# 供内联 SVG 用的矩形坐标
print("\n内联 SVG 矩形（24 网格）：")
for (a,b,c,e) in geom():
    print("  <rect x='%.2f' y='%.2f' width='%.2f' height='%.2f'/>" % (a,b,c-a,e-b))

# 16px 预览
prev=Image.new("RGBA",(16*6*3+80,16*6+40),(18,18,22,255))
for i,s in enumerate((16,20,32)):
    im=png(s).resize((s*5,s*5), Image.NEAREST)
    prev.paste(im,(20+i*150, 20+(32*5-s*5)//2), im)
prev.save("/private/tmp/claude-501/-Users-wangkun/55b2ea92-81e7-4993-8b64-bbdf64459f60/scratchpad/H_preview.png")
