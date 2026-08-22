# HYPERNOVA

面向 Hyperliquid 交易者的合约仓位计算器与交易复盘日志。
线上地址：https://hypernova.vip

## 仓库结构

```
index.html        中文版（唯一真源）
en/index.html     英文版（由 build-en.py 自动生成，请勿直接编辑）
build-en.py       英文版生成脚本
404.html          品牌化 404 页
_headers          Cloudflare 安全头与缓存策略
wrangler.jsonc    Cloudflare Workers 静态资源配置
sitemap.xml       含双语 hreflang 声明
robots.txt        含内容信号（search / ai-input / ai-train）
og.png            社交分享卡片
favicon.ico / apple-touch-icon.png / icon-192.png / icon-512.png
site.webmanifest  PWA 清单
```

## 改动流程

**所有内容改动只改 `index.html`**，改完必须重新生成英文版：

```bash
python3 build-en.py
```

英文版由中文版加上 i18n 文案表生成。两份手工维护的文件必然漂移——
本项目此前就出现过静态 HTML 与文案表不一致达 43 处、以及计算方法章节
在英文下仍显示中文标签的问题。生成脚本会在英文文案缺失时直接报错退出。

新增文案时：在 `T` 表的 `zh` 与 `en` 两侧都加上键，并在 HTML 元素上标
`data-i18n="键名"`。生成脚本会校验英文键是否齐全。

## 部署

推送到 `main` 即由 Cloudflare Workers 自动构建部署。
资源配置在 `wrangler.jsonc`（config as code——**后台改动会被仓库覆盖**）。

## 数据来源

合约参数（最大杠杆、下单精度）取自 Hyperliquid 公开接口
`POST https://api.hyperliquid.xyz/info` `{"type":"meta"}`，
浏览器端直接请求，缓存 24 小时，不携带任何用户输入。
请求失败时静默降级为手动填写，计算器功能不受影响。

维持保证金率按 `1 / (2 × 最大杠杆)` 推算，对应 Hyperliquid 的规则：
维持保证金为最大杠杆下初始保证金的一半。

## 免责

本工具输出的全部数值均为基于所填参数的理论估算，仅供研究与参考，
不构成投资建议。与 Hyperliquid Labs 无隶属、赞助或背书关系。
