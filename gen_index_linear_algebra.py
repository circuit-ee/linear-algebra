#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扫描仓库根目录，为每个 chapt* 文件夹生成章节卡片，
列出文件夹内的 .html 文件（index.html 作为章节入口优先），最终生成 index.html。

用法：把本文件放到 linear-algebra 仓库根目录（与各 chapt 文件夹同级），
      在终端执行  python3 gen_index.py
"""
import os
import re
from html import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "index.html")

COURSE_TITLE = "线性代数"   # 网站大标题，按需修改


def page_title(path):
    """尝试从 html 文件的 <title> 或第一个 <h1>/<h2> 读取标题，失败则返回文件名。"""
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            content = f.read(2000)
    except Exception:
        return None
    m = re.search(r"<title>(.*?)</title>", content, re.I | re.S)
    if m:
        return m.group(1).strip()
    m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", content, re.I | re.S)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return None


# 收集章节
chapters = []
for name in os.listdir(ROOT):
    full = os.path.join(ROOT, name)
    if not os.path.isdir(full) or not name.lower().startswith("chapt"):
        continue
    # 解析章节号与标题（兼容 "chapt1 行列式" 与 "chapt 2 矩阵..." 两种写法）
    num_match = re.match(r"chapt\s*(\d+)\s*(.*)", name, re.I)
    num = int(num_match.group(1)) if num_match else 0
    title = num_match.group(2).strip() if num_match else name

    # 收集该章节内的 html 文件
    pages = []
    for fname in sorted(os.listdir(full)):
        if fname.lower().endswith(".html"):
            label = page_title(os.path.join(full, fname)) or fname
            pages.append((fname, label))
    # index.html 优先排在最前
    pages.sort(key=lambda p: (p[0].lower() != "index.html", p[0].lower()))
    chapters.append((num, name, name, title, pages))

# 按章节号排序（1, 2, 3 ...），而非字符串排序
chapters.sort(key=lambda c: c[0])

# 生成章节块
cards_html = ""
for num, display, folder, title, pages in chapters:
    links = ""
    for fname, label in pages:
        href = f"{folder}/{fname}"
        href_enc = escape(href, quote=True)
        links += f'''
          <li>
            <a href="{href_enc}">{escape(label)}</a>
          </li>'''
    cards_html += f'''
    <section class="chapter">
      <div class="chapter-head">
        <span class="num">{num:02d}</span>
        <h2>{escape(title or display)}</h2>
      </div>
      <ul class="page-list">{links}
      </ul>
    </section>'''

count = sum(len(c[4]) for c in chapters)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{COURSE_TITLE} · 课程网页</title>
  <style>
    :root {{
      --bg: #0f1420;
      --card: #1a2133;
      --accent: #00d4ff;
      --text: #e6edf3;
      --sub: #9aa7b8;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
      background: linear-gradient(160deg, #0f1420, #131c2e);
      color: var(--text);
      line-height: 1.7;
    }}
    header {{
      text-align: center;
      padding: 60px 20px 40px;
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }}
    header h1 {{
      font-size: 2.2rem;
      margin: 0 0 10px;
      background: linear-gradient(90deg, #00d4ff, #7bffcf);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }}
    header p {{ color: var(--sub); margin: 4px 0; }}
    main {{
      max-width: 960px;
      margin: 30px auto 80px;
      padding: 0 20px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 20px;
    }}
    .chapter {{
      background: var(--card);
      border: 1px solid rgba(0,212,255,0.15);
      border-radius: 14px;
      padding: 20px;
      transition: transform .2s, border-color .2s;
    }}
    .chapter:hover {{
      transform: translateY(-4px);
      border-color: var(--accent);
    }}
    .chapter-head {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 14px;
    }}
    .chapter-head .num {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 38px;
      height: 38px;
      padding: 0 6px;
      border-radius: 10px;
      background: linear-gradient(135deg, #00d4ff, #0099c4);
      color: #001018;
      font-weight: 700;
      font-size: 1rem;
    }}
    .chapter-head h2 {{
      font-size: 1.05rem;
      margin: 0;
      color: var(--text);
    }}
    .page-list {{ list-style: none; padding: 0; margin: 0; }}
    .page-list li {{ padding: 6px 0; border-top: 1px dashed rgba(255,255,255,0.06); }}
    .page-list a {{
      color: var(--sub);
      text-decoration: none;
      font-size: 0.92rem;
      transition: color .15s;
    }}
    .page-list a:hover {{ color: var(--accent); }}
    footer {{
      text-align: center;
      color: var(--sub);
      font-size: 0.85rem;
      padding: 30px;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{COURSE_TITLE}</h1>
    <p>课程交互式网页 · 共 {len(chapters)} 章 / {count} 个页面</p>
  </header>
  <main>{cards_html}
  </main>
  <footer>由 gen_index.py 自动生成 · 点击章节即可查看对应网页</footer>
</body>
</html>'''

os.makedirs(ROOT, exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"已生成 {OUT}")
print(f"章节数: {len(chapters)}, 页面数: {count}")
for num, display, folder, title, pages in chapters:
    print(f"  {num:2d} {title} -> {len(pages)} 页")
