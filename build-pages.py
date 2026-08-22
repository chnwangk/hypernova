#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成法务页面：terms/ privacy/ 及其英文版。

设计令牌直接从 index.html 的 :root 块读取后注入，不复制第二份——
本项目此前多次吃过“同一份值散落多处然后各自漂移”的亏。
内容来自 pages/legal.{zh,en}.json，中英章节数不一致时报错退出。

用法：python3 build-pages.py
"""
import io, json, os, re, sys, html

SITE = "https://hypernova.vip"
EYEBROW = {"zh": {"legal":"法务", "releases":"版本记录"},
           "en": {"legal":"Legal", "releases":"Release notes"}}

def read(p): return io.open(p, encoding="utf-8").read()

def tokens_from_index():
    s = read("index.html")
    m = re.search(r'(  :root\{.*?\n  \})', s, re.S)
    if not m: sys.exit("无法从 index.html 提取 :root 令牌块")
    return m.group(1)

CSS = """
  *{box-sizing:border-box;margin:0;padding:0}
  html{background:var(--bg);-webkit-text-size-adjust:100%;overflow-x:clip;scroll-padding-top:84px}
  body{
    font-family:var(--sans);background:var(--bg);color:var(--text);
    line-height:1.75;min-height:100vh;font-size:var(--fs-md);
    -webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;
    font-variant-numeric:lining-nums tabular-nums;overflow-x:clip;
  }
  a{color:inherit;text-decoration:none}
  a,button{-webkit-tap-highlight-color:transparent}
  ::selection{background:color-mix(in srgb, var(--accent) 24%, transparent)}
  :focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px}
  *{scrollbar-width:thin;scrollbar-color:var(--line-strong) transparent}
  ::-webkit-scrollbar{width:10px}
  ::-webkit-scrollbar-thumb{background:var(--line-strong);border-radius:99px;border:3px solid var(--bg);background-clip:padding-box}
  .wrap{max-width:820px;margin:0 auto;padding:0 24px}

  /* 顶栏：与主页一致的浮动小块，各自带不透明底色，不设整条横栏 */
  header{position:sticky;top:0;z-index:50;padding:14px 0;pointer-events:none}
  header a{pointer-events:auto}
  .nav{display:flex;align-items:center;gap:10px}
  .chip{
    display:inline-flex;align-items:center;gap:8px;height:44px;padding:0 15px;
    background:var(--panel2);border:1px solid var(--line);border-radius:var(--r-lg);
    color:var(--text2);font-size:var(--fs-sm);font-weight:600;white-space:nowrap;
    transition:background-color .15s,border-color .15s,color .15s;
  }
  .chip:hover{background:var(--panel);border-color:var(--line-strong);color:var(--text)}
  .chip-brand{padding:0 17px;color:var(--text)}
  .chip-brand b{font-family:var(--wordmark);font-size:17px;font-weight:500;letter-spacing:.1em;line-height:1}
  .chip-brand span{font-weight:500;letter-spacing:.1em}
  .chip-end{margin-left:auto;display:flex;align-items:center;gap:6px}
  .chip-lang{padding:0 13px;font-size:var(--fs-xs);font-weight:700;letter-spacing:.06em;color:var(--muted)}

  main{padding:52px 0 40px}
  .eyebrow{font-size:var(--fs-micro);letter-spacing:.14em;color:var(--accent);font-weight:700;text-transform:uppercase;margin-bottom:10px}
  h1{font-size:30px;font-weight:700;letter-spacing:-.02em;margin-bottom:10px;text-wrap:balance}
  .updated{color:var(--faint);font-size:var(--fs-xs);font-family:var(--mono);margin-bottom:26px}
  .lede{
    color:var(--text2);font-size:var(--fs-lg);line-height:1.8;margin-bottom:34px;
    border-left:2px solid var(--line-strong);padding-left:16px;text-wrap:pretty;
  }
  section.doc{margin-bottom:32px}
  h2{font-size:var(--fs-lg);font-weight:700;margin-bottom:12px;letter-spacing:-.01em}
  .doc p{color:var(--muted);font-size:var(--fs-base);line-height:1.85;margin-bottom:10px;text-wrap:pretty}
  .doc p:last-child{margin-bottom:0}
  .doc p.code{font-family:var(--mono);color:var(--accent);font-size:var(--fs-sm);
    background:var(--inset);border:1px solid var(--line);border-radius:var(--r-sm);padding:10px 13px;overflow-x:auto}
  .doc p.item{padding-left:14px}

  /* 更新日志 */
  .rel{border-top:1px solid var(--line);padding:22px 0}
  .rel:first-of-type{border-top:none;padding-top:0}
  .rel-h{display:flex;align-items:baseline;gap:12px;margin-bottom:14px;flex-wrap:wrap}
  .rel-v{font-family:var(--mono);font-size:var(--fs-lg);font-weight:700;color:var(--accent);letter-spacing:-.01em}
  .rel-d{font-family:var(--mono);font-size:var(--fs-xs);color:var(--faint)}
  .chg{display:flex;gap:12px;padding:7px 0;align-items:baseline}
  .tag{
    flex-shrink:0;min-width:52px;text-align:center;
    font-size:var(--fs-micro);font-weight:700;letter-spacing:.06em;
    padding:2px 7px;border-radius:var(--r-sm);border:1px solid;
  }
  .tag.add{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 40%,transparent);
           background:color-mix(in srgb,var(--accent) 10%,transparent)}
  .tag.fix{color:var(--amber-text);border-color:color-mix(in srgb,var(--amber) 40%,transparent);
           background:color-mix(in srgb,var(--amber) 10%,transparent)}
  .tag.imp{color:var(--muted);border-color:var(--line-strong)}
  .chg p{color:var(--muted);font-size:var(--fs-base);line-height:1.8;margin:0;text-wrap:pretty}
  @media(max-width:560px){
    .chg{flex-direction:column;gap:5px}
    .tag{align-self:flex-start;min-width:0}
  }

  .backlink{display:inline-flex;align-items:center;gap:7px;margin-top:8px;
    color:var(--accent);font-size:var(--fs-sm);font-weight:600}
  .backlink:hover{color:var(--text)}

  footer{border-top:1px solid var(--line);margin-top:48px;color:var(--muted);font-size:var(--fs-sm)}
  .foot{display:flex;flex-wrap:wrap;gap:14px 22px;align-items:center;padding:24px 0}
  .foot a{color:var(--muted);transition:color .15s}
  .foot a:hover{color:var(--text)}
  .foot .sep{color:var(--line-strong)}
  .foot-note{border-top:1px solid var(--line-soft);padding:16px 0 26px;color:var(--faint);font-size:var(--fs-xs);line-height:1.7}

  @media(max-width:680px){
    main{padding:34px 0 26px}
    h1{font-size:25px}
    .lede,.doc p{text-align:justify;text-justify:inter-ideograph}
    header{padding:10px 0}
    .nav{flex-wrap:wrap;gap:6px}
    .chip{height:40px;padding:0 13px;font-size:var(--fs-xs)}
    .chip-brand{padding:0 14px 0 11px}
    .chip-brand b{font-size:var(--fs-md)}
  }
  @media print{
    :root{--bg:#fff;--panel:#fff;--inset:#fff;--text:#000;--text2:#222;--muted:#333;--faint:#555;
          --line:#bbb;--line-strong:#888;--line-soft:#ddd}
    body{background:#fff;color:#000}
    header,footer,.backlink{display:none!important}
  }
  @media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

STR = {
 "zh": {"home":"返回计算器","terms":"服务条款","privacy":"隐私政策","changelog":"更新日志","github":"源码",
        "updated":"最后更新","other":"/en/","otherLabel":"EN","otherHreflang":"en",
        "note":"HYPERNOVA 是独立的第三方工具，与 Hyperliquid Labs 无隶属、赞助或背书关系。"
               "Hyperliquid 及其他提及的名称与标识为其各自所有者的商标。"
               "本站内容仅供研究与参考，不构成投资建议。",
        "copy":"© 2026 HYPERNOVA"},
 "en": {"home":"Back to calculator","terms":"Terms of Service","privacy":"Privacy Policy","changelog":"Changelog","github":"Source",
        "updated":"Last updated","other":"/","otherLabel":"中文","otherHreflang":"zh-Hans",
        "note":"HYPERNOVA is an independent third-party tool with no affiliation, sponsorship or endorsement "
               "relationship with Hyperliquid Labs. Hyperliquid and any other names or marks mentioned are "
               "trademarks of their respective owners. Content is provided for research and reference only "
               "and does not constitute investment advice.",
        "copy":"© 2026 HYPERNOVA"},
}

def build(lang, key, doc, tokens):
    L = STR[lang]
    base = "" if lang=="zh" else "/en"
    other_base = "/en" if lang=="zh" else ""
    url = "%s%s/%s/" % (SITE, base, doc["slug"])
    alt = "%s%s/%s/" % (SITE, other_base, doc["slug"])
    htmllang = "zh-CN" if lang=="zh" else "en"

    body=[]
    if "releases" in doc:
        TAGCLS={"新增":"add","修复":"fix","改进":"imp",
                "Added":"add","Fixed":"fix","Improved":"imp"}
        for r in doc["releases"]:
            rows=[]
            for typ, text in r["items"]:
                rows.append('        <div class="chg"><span class="tag %s">%s</span><p>%s</p></div>'
                            % (TAGCLS.get(typ,"imp"), html.escape(typ), html.escape(text)))
            body.append('      <section class="rel">\n'
                        '        <div class="rel-h"><span class="rel-v">v%s</span>'
                        '<span class="rel-d">%s</span></div>\n%s\n      </section>'
                        % (html.escape(r["v"]), html.escape(r["date"]), "\n".join(rows)))
        return TPL(lang, doc, tokens, body)

    for title, paras in doc["sections"]:
        ps=[]
        for p in paras:
            cls = ""
            if p.startswith("POST "): cls = ' class="code"'
            elif p.startswith("· "):  cls = ' class="item"'
            ps.append("        <p%s>%s</p>" % (cls, html.escape(p)))
        body.append('      <section class="doc">\n        <h2>%s</h2>\n%s\n      </section>'
                    % (html.escape(title), "\n".join(ps)))
    return TPL(lang, doc, tokens, body)

def TPL(lang, doc, tokens, body):
    L = STR[lang]
    base = "" if lang=="zh" else "/en"
    other_base = "/en" if lang=="zh" else ""
    url = "%s%s/%s/" % (SITE, base, doc["slug"])
    htmllang = "zh-CN" if lang=="zh" else "en"
    zh_url = "%s/%s/" % (SITE, doc["slug"])
    en_url = "%s/en/%s/" % (SITE, doc["slug"])

    return """<!DOCTYPE html>
<html lang="{htmllang}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="format-detection" content="telephone=no,date=no,address=no,email=no" />
<title>{title} · HYPERNOVA</title>
<meta name="description" content="{desc}" />
<link rel="canonical" href="{url}" />
<link rel="alternate" hreflang="zh-Hans" href="{zh_url}" />
<link rel="alternate" hreflang="en" href="{en_url}" />
<link rel="alternate" hreflang="x-default" href="{zh_url}" />
<meta name="robots" content="index, follow" />
<meta name="theme-color" content="#04070a" />
<meta name="color-scheme" content="dark" />
<link rel="icon" href="/favicon.ico?v=2" sizes="16x16 32x32 48x48" />
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2" sizes="180x180" />
<link rel="manifest" href="/site.webmanifest" />
<style>
{tokens}
{css}
</style>
</head>
<body>
<header>
  <div class="wrap nav">
    <a class="chip chip-brand" href="{home}" aria-label="HYPERNOVA"><b>HYPER<span>NOVA</span></b></a>
    <div class="chip-end">
      <a class="chip" href="{home}">{home_label}</a>
      <a class="chip chip-lang" href="{other}{slug}/" rel="alternate" hreflang="{oh}">{ol}</a>
    </div>
  </div>
</header>

<main class="wrap">
  <div class="eyebrow">{eyebrow}</div>
  <h1>{title}</h1>
  <div class="updated">{updated_label} {updated}</div>
  <p class="lede">{lede}</p>

{body}

  <a class="backlink" href="{home}">← {home_label}</a>
</main>

<footer>
  <div class="wrap">
    <div class="foot">
      <span>{copy}</span><span class="sep">·</span>
      <a href="{base}/terms/">{terms}</a><span class="sep">·</span>
      <a href="{base}/privacy/">{privacy}</a><span class="sep">·</span>
      <a href="{base}/changelog/">{changelog}</a><span class="sep">·</span>
      <a href="https://github.com/chnwangk/hypernova" rel="noopener">{github}</a><span class="sep">·</span>
      <a href="mailto:contact@hypernova.vip">contact@hypernova.vip</a>
    </div>
    <div class="foot-note">{note}</div>
  </div>
</footer>
</body>
</html>
""".format(htmllang=htmllang, title=html.escape(doc["title"]),
           desc=html.escape(doc["lede"][:150]), url=url,
           zh_url=zh_url, en_url=en_url,
           tokens=tokens, css=CSS,
           home=("/" if lang=="zh" else "/en/"), home_label=L["home"],
           other=(other_base+"/"), slug=doc["slug"], oh=L["otherHreflang"], ol=L["otherLabel"],
           eyebrow=EYEBROW[lang]["releases" if "releases" in doc else "legal"],
           updated_label=L["updated"], updated=doc["updated"],
           lede=html.escape(doc["lede"]), body="\n\n".join(body),
           copy=L["copy"], terms=L["terms"], privacy=L["privacy"], github=L["github"],
           changelog=L["changelog"],
           note=html.escape(L["note"]), base=base)

def main():
    tokens = tokens_from_index()
    zh, en = {}, {}
    for name in ("legal", "changelog"):
        zh.update(json.load(io.open("pages/%s.zh.json" % name, encoding="utf-8")))
        en.update(json.load(io.open("pages/%s.en.json" % name, encoding="utf-8")))
    for k in zh:
        if k not in en: sys.exit("英文缺少文档: %s" % k)
        key = "releases" if "releases" in zh[k] else "sections"
        if key not in en[k] or len(zh[k][key]) != len(en[k][key]):
            sys.exit("文档 %s 的中英条目数不一致" % k)
    n=0
    for lang, data in (("zh", zh), ("en", en)):
        for key, doc in data.items():
            d = doc["slug"] if lang=="zh" else os.path.join("en", doc["slug"])
            os.makedirs(d, exist_ok=True)
            io.open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(build(lang, key, doc, tokens))
            n+=1
    print("已生成 %d 个法务页面（令牌取自 index.html，%d 个变量）" % (n, tokens.count("--")))

if __name__ == "__main__":
    main()
