#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
由 index.html（中文版）生成 en/index.html（英文版）。

index.html 是唯一的真源。英文版永远由它生成，不要直接编辑 en/index.html——
两份手工维护的文件必然漂移，这个站之前就吃过静态 HTML 与文案表不一致的亏。

改完 index.html 后运行：  python3 build-en.py
"""
import io, os, re, sys

SRC = "index.html"
OUT = os.path.join("en", "index.html")

def read(p):
    return io.open(p, encoding="utf-8").read()

def extract_table(s, name):
    """从 var T = {...} / var MSG = {...} 中取出某一语言的键值对（仅字符串字面量）"""
    m = re.search(r"var %s = \{\s*zh: \{(.*?)\n    \},\s*\n    en: \{(.*?)\n    \}\s*\n  \};" % name, s, re.S)
    if not m:
        sys.exit("无法解析 %s 表，结构可能已变动" % name)
    def parse(block):
        return {mm.group(1): mm.group(2) for mm in re.finditer(r"(\w+):'((?:[^'\\]|\\.)*)'", block)}
    return parse(m.group(1)), parse(m.group(2))

def main():
    s = read(SRC)
    T_zh, T_en = extract_table(s, "T")
    missing = [k for k in T_zh if k not in T_en]
    if missing:
        sys.exit("以下文案缺少英文版本，请先补齐: %s" % ", ".join(missing))

    # 1) 语言标识
    s = s.replace('<html lang="zh-CN" data-lang="zh">', '<html lang="en" data-lang="en">', 1)

    # 2) 把所有 data-i18n 元素的内容替换为英文
    pat = re.compile(r'<([a-z0-9]+)([^>]*\bdata-i18n="([^"]+)"[^>]*)>(.*?)</\1>', re.S)
    n = [0]
    def sub(m):
        tag, attrs, key, _inner = m.groups()
        if key in T_en:
            n[0] += 1
            return '<%s%s>%s</%s>' % (tag, attrs, T_en[key], tag)
        return m.group(0)
    s = pat.sub(sub, s)

    # 3) 头部元信息
    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % T_en['title'], s, count=1)
    s = s.replace('<link rel="canonical" href="https://hypernova.vip/" />',
                  '<link rel="canonical" href="https://hypernova.vip/en/" />', 1)
    s = s.replace('<meta property="og:url" content="https://hypernova.vip/" />',
                  '<meta property="og:url" content="https://hypernova.vip/en/" />', 1)
    s = s.replace('<meta property="og:locale" content="zh_CN" />',
                  '<meta property="og:locale" content="en_US" />', 1)
    s = s.replace('<meta property="og:locale:alternate" content="en_US" />',
                  '<meta property="og:locale:alternate" content="zh_CN" />', 1)
    s = re.sub(r'<meta name="description" content="[^"]*" />',
               '<meta name="description" content="Position size calculator for Hyperliquid traders: enter a symbol and the contract&rsquo;s '
               'max leverage and maintenance margin are filled in automatically. Derive position size, required margin, estimated liquidation '
               'price and R:R from the loss you can accept. Every formula is published. All computation runs locally in your browser." />',
               s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*" />',
               '<meta property="og:title" content="HYPERNOVA &middot; Hyperliquid Position Calculator" />', s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*" />',
               '<meta property="og:description" content="Size positions from risk, with Hyperliquid contract parameters filled in automatically. '
               'Every formula published. Runs locally." />', s, count=1)

    # 4) 语言切换链接反向
    s = s.replace('<a href="/en/" id="langToggle" class="lang-btn" rel="alternate" hreflang="en" '
                  'aria-label="View this page in English">EN</a>',
                  '<a href="/" id="langToggle" class="lang-btn" rel="alternate" hreflang="zh-Hans" '
                  'aria-label="以中文查看本页">中文</a>', 1)

    # 5) 站内链接指向英文版对应页面（只翻译文字而不改链接会把用户带回中文页）
    s = s.replace('href="/terms/"', 'href="/en/terms/"')
    s = s.replace('href="/privacy/"', 'href="/en/privacy/"')

    # 6) 结构化数据里的语言与地址
    s = s.replace('"@id": "https://hypernova.vip/#website"', '"@id": "https://hypernova.vip/en/#website"')
    s = s.replace('"@id": "https://hypernova.vip/#app"', '"@id": "https://hypernova.vip/en/#app"')

    os.makedirs("en", exist_ok=True)
    io.open(OUT, "w", encoding="utf-8").write(s)
    print("已生成 %s（替换 %d 处文案，英文键 %d 个）" % (OUT, n[0], len(T_en)))

if __name__ == "__main__":
    main()
