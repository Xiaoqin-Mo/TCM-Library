# -*- coding: utf-8 -*-
"""经方生成器：从库内 shanghan/jingui 条文提取原文，生成 fangji/jingfang 条目。"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(r'F:\dev\TCM-Library')
os.chdir(ROOT)
sys.path.insert(0, 'raw')
from fang_data import FANGS  # noqa: E402

LIB = ROOT / 'library'
OUT = LIB / 'fangji' / 'jingfang'


def load_entries(dirs):
    """加载目录下所有条目：{path: (frontmatter_text, body_text)}"""
    entries = []
    for d in dirs:
        for p in sorted((LIB / d).glob('*.md')):
            if p.name == 'INDEX.md':
                continue
            t = p.read_text(encoding='utf-8')
            m = re.match(r'^---\n(.*?)\n---\n(.*)$', t, re.S)
            if not m:
                continue
            fm, body = m.group(1), m.group(2)
            entries.append((p, fm, body))
    return entries


def fm_get(fm, key):
    m = re.search(rf'^{key}:\s*"?([^"\n]+)"?', fm, re.M)
    return m.group(1).strip() if m else ''


def extract_yuanwen(body):
    """提取【原文】层（去掉标记与标题）"""
    m = re.search(r'\*\*【原文】\*\*\s*(.*?)\s*\*\*【古注】\*\*', body, re.S)
    if not m:
        return ''
    txt = m.group(1).strip()
    # 去掉可能残留的 markdown 标题
    txt = re.sub(r'^#+\s*', '', txt, flags=re.M)
    return txt


def main():
    entries = load_entries(['jingdian/shanghan', 'jingdian/jingui'])
    missing = []
    for f in FANGS:
        pid, name, match = f['pid'], f['name'], f['match']
        # 找含 match 的条文
        hit = None
        for p, fm, body in entries:
            if match in body:
                hit = (p, fm, body)
                break
        if hit is None:
            missing.append((pid, name, match))
            print(f'!! 未找到 {name}（{match}）')
            continue
        p, fm, body = hit
        yuan = extract_yuanwen(body)
        if not yuan:
            missing.append((pid, name, '原文层提取失败'))
            print(f'!! {name} 原文层提取失败')
            continue
        book = fm_get(fm, 'book') or '伤寒论'
        chapter = fm_get(fm, 'chapter') or '经方'
        src = fm_get(fm, 'source_version') or '宋本·明赵开美翻刻通行本'
        author = fm_get(fm, 'author') or '张仲景'
        dynasty = fm_get(fm, 'dynasty') or '汉'
        src_file = p.name

        zx = ', '.join(f'"{x}"' for x in f['zx'])
        zf = ', '.join(f'"{x}"' for x in f['zf'])
        bz = ', '.join(f'"{x}"' for x in f['bz'])
        zz = ', '.join(f'"{x}"' for x in f['zz'])
        ym = ', '.join(f'"{x}"' for x in f['ym'])
        kw = ', '.join(f'"{x}"' for x in f['kw'])

        md = f'''---
id: "{pid}_001"
book: "{book}"
chapter: "{chapter}"
section_title: "{name}方"
source_version: "{src}"
author: "{author}"
dynasty: "{dynasty}"
type: "fangji"
conditions:
  zhengxing: [{zx}]
  zhifa: [{zf}]
  bingzheng: [{bz}]
  zhengzhuang: [{zz}]
  fangming: ["{name}"]
  yaoming: [{ym}]
  xuewei: []
  jingluo: []
  siqi: []
  wuwei: []
  guijing: []
  keywords: [{kw}]
weight: 8
tags: ["方剂学", "经方"]
---

### {name}方

**【原文】**
{yuan}

**【古注】**
（暂无本条古注，从略）

**【白话提要】**
{f['note']}
'''
        out_dir = OUT / pid
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f'{pid}_001.md'
        out_file.write_text(md, encoding='utf-8')
        print(f'OK {pid} ({name}) <- {src_file}')

    print(f'\n生成完成：{len(FANGS) - len(missing)}/{len(FANGS)}，缺失 {len(missing)}')
    for m in missing:
        print('  MISS:', m)


if __name__ == '__main__':
    main()
