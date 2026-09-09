#!/usr/bin/env python3
"""build_index.py — 生成各级 INDEX.md（人读导航）。

- 每个书目录（含条目的最深层目录）：生成该书 INDEX.md（条目清单）
- 每个 subcategory / category 目录：生成索引（下级书/子类清单）
- 根目录：生成总 INDEX.md（收录进度 + 分类导航 + 检索字段速查）

确定性生成（按路径排序），可重复运行；不写时间戳。
用法: python3 scripts/build_index.py
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from typing import Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tcm_lib import (  # noqa: E402
    CATEGORIES,
    CATEGORY_MAP,
    CONDITION_FIELDS,
    MATCH_FIELDS,
    SKIP_FILENAMES,
    id_from_path,
    iter_entry_files,
    parse_frontmatter,
)

LIBRARY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "library")


def collect() -> Dict[str, List[Dict]]:
    """扫描 library/，返回 {相对书目录: [条目 dict, ...]}。"""
    books: Dict[str, List[Dict]] = defaultdict(list)
    for fp in iter_entry_files(LIBRARY_DIR):
        fm, _body = parse_frontmatter(open(fp, encoding="utf-8").read())
        if not fm or "id" not in fm:
            continue
        rel = os.path.relpath(os.path.dirname(fp), LIBRARY_DIR)
        title = fm.get("section_title") or fm.get("chapter") or fm.get("id")
        books[rel].append({
            "id": fm["id"],
            "title": title,
            "weight": fm.get("weight", 0),
            "type": fm.get("type", ""),
            "file": os.path.basename(fp),
        })
    for rel in books:
        books[rel].sort(key=lambda e: (e["file"]))
    return dict(sorted(books.items()))


def render_book_index(rel: str, entries: List[Dict]) -> str:
    parts = rel.split(os.sep)
    cat, sub = parts[0], (parts[1] if len(parts) > 1 else "")
    czh = CATEGORY_MAP.get(cat, {}).get("name_zh", cat)
    szh = ""
    if cat in CATEGORY_MAP and sub in CATEGORY_MAP[cat].get("subs", {}):
        szh = CATEGORY_MAP[cat]["subs"][sub]
    depth = len(parts)
    prefix = "../" * depth
    lines = [
        f"# {rel} · 索引",
        "",
        f"> {czh} / {szh} · 条目数 {len(entries)}",
        "",
        "| 条目 | 标题 | 类型 | 权重 |",
        "| --- | --- | --- | --- |",
    ]
    for e in entries:
        lines.append(f"| [{e['id']}](./{e['file']}) | {e['title']} | {e['type']} | {e['weight']} |")
    lines += ["", f"[返回总索引]({prefix}INDEX.md)"]
    return "\n".join(lines) + "\n"


def render_category_index(cat: str, books: Dict[str, List[Dict]]) -> str:
    czh = CATEGORY_MAP[cat]["name_zh"]
    subs: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    total = 0
    for rel in sorted(books):
        parts = rel.split(os.sep)
        if parts[0] != cat:
            continue
        sub = parts[1] if len(parts) > 1 else "(root)"
        subs[sub].append((rel, len(books[rel])))
        total += len(books[rel])
    lines = [
        f"# {cat} · {czh}",
        "",
        f"> 收录 {total} 条 · 下级 {len(subs)} 个子类",
        "",
    ]
    for sub in sorted(subs):
        szh = CATEGORY_MAP[cat]["subs"].get(sub, sub)
        lines.append(f"## {sub} · {szh}")
        lines.append("")
        lines.append("| 书目 | 条目数 | 索引 |")
        lines.append("| --- | --- | --- |")
        for rel, cnt in subs[sub]:
            lines.append(f"| {rel} | {cnt} | [索引](./{rel}/INDEX.md) |")
        lines.append("")
    lines.append("[返回总索引](../INDEX.md)")
    return "\n".join(lines) + "\n"


def render_root_index(books: Dict[str, List[Dict]]) -> str:
    total = sum(len(v) for v in books.values())
    lines = [
        "# TCM-Library · 全库总索引",
        "",
        f"> 中医知识百科全书检索库 · 当前收录 {total} 条（按目录自动生成）",
        "",
        "## 收录进度",
        "",
        "| 分类 | 中文名 | 书目数 | 条目数 | 索引 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for cat, czh, _subs in CATEGORIES:
        cat_books = [r for r in books if r.split(os.sep)[0] == cat]
        cat_total = sum(len(books[r]) for r in cat_books)
        link = f"[索引](./library/{cat}/INDEX.md)" if cat_books else "—"
        lines.append(f"| {cat} | {czh} | {len(cat_books)} | {cat_total} | {link} |")
    lines += [
        "",
        "## 检索字段速查",
        "",
        "结构化维度（组内 AND、维度间 OR）：",
        "| 字段 | 含义 | 示例 |",
        "| --- | --- | --- |",
        "| `zhengxing` | 证型 | 风寒束表、肝气郁结 |",
        "| `zhifa` | 治法 | 解表散寒、疏肝理气 |",
        "| `bingzheng` | 病症 | 感冒、消渴 |",
        "| `zhengzhuang` | 症状 | 发热、恶寒 |",
        "| `fangming` | 方名 | 桂枝汤 |",
        "| `yaoming` | 药名 | 麻黄、桂枝 |",
        "| `xuewei` | 腧穴 | 足三里 |",
        "| `jingluo` | 经络 | 手太阴肺经 |",
        "| `keywords` | 开放主题词 | 调护、禁忌（包含召回） |",
        "",
        "> 详细规范见 [docs/frontmatter-spec.md](../docs/frontmatter-spec.md)",
        "",
        "## 分类导航",
        "",
    ]
    for cat, czh, _subs in CATEGORIES:
        lines.append(f"- **{cat}** · {czh}" + (f"（{len([r for r in books if r.split(os.sep)[0] == cat])} 部书，"
                     f"{sum(len(books[r]) for r in books if r.split(os.sep)[0] == cat)} 条）"
                     if any(r.split(os.sep)[0] == cat for r in books) else "（待收录）"))
    lines.append("")
    lines.append("> 本文件由 `scripts/build_index.py` 确定性生成，勿手改。")
    return "\n".join(lines) + "\n"


def main() -> None:
    books = collect()
    # 每本书 INDEX.md
    for rel, entries in books.items():
        p = os.path.join(LIBRARY_DIR, rel, "INDEX.md")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(render_book_index(rel, entries))
    # 分类 INDEX.md（存在书的分类）
    cats_with_books = {r.split(os.sep)[0] for r in books}
    for cat in sorted(cats_with_books):
        p = os.path.join(LIBRARY_DIR, cat, "INDEX.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(render_category_index(cat, books))
    # 根 INDEX.md
    with open(os.path.join(LIBRARY_DIR, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(render_root_index(books))
    print(f"INDEX 生成完成：{len(books)} 部书，{sum(len(v) for v in books.values())} 条")


if __name__ == "__main__":
    main()
