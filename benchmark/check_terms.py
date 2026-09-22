#!/usr/bin/env python3
"""check_terms.py — 检查候选术语在语料中的命中分布（查询集构造辅助）。

对每个术语报告：在原文层 / 白话层 / conditions 值（证型、治法、病名等）
中出现（子串匹配）的条目数，帮助判断查询目标是否存在于库内。
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

CORPUS = os.path.join(ROOT, "benchmark", "data", "corpus.jsonl")


def load():
    out = []
    with open(CORPUS, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


TERMS = sys.argv[1:] or [
    # modern
    "感冒", "咳嗽", "失眠", "便秘", "糖尿病", "高血压", "荨麻疹", "月经不调", "痛经",
    "哮喘", "湿疹", "带状疱疹", "面瘫", "过敏性鼻炎", "胃炎", "腰痛", "头痛", "眩晕", "水肿", "黄疸",
    # classical
    "太阳中风", "阳明病", "少阳病", "往来寒热", "少阴病", "太阴病", "厥阴病", "消渴",
    "百合病", "胸痹", "心下悸", "不得眠", "不寐", "积聚", "水气病", "风寒湿痹", "咳逆上气",
    "奔豚气", "肠痈", "梅核气", "狐惑", "霍乱", "呕吐下利",
    # zhenjiu
    "足三里", "合谷", "大椎", "内关", "三阴交", "太冲", "曲池", "委中",
    # herbs / formulas
    "麻黄", "桂枝", "柴胡", "黄芪", "当归", "人参", "附子", "白芷",
    "桂枝汤", "麻黄汤", "小柴胡汤", "白虎汤", "四逆汤", "六味地黄丸", "逍遥散", "归脾汤",
    "补中益气汤", "理中丸", "四君子汤", "银翘散",
    # syndromes / treatments
    "风寒束表", "风热犯肺", "肝阳上亢", "气血两虚", "脾胃虚弱", "肝气郁结", "阴虚火旺",
    "解表散寒", "发汗解表", "清热化痰", "平肝潜阳", "疏肝理气", "健脾益气", "活血化瘀",
    "温经散寒", "祛风止痒", "通乳", "消食导滞",
]


def main() -> None:
    corpus = load()
    books = {}
    for e in corpus:
        books.setdefault(e["book"], 0)
        books[e["book"]] += 1
    print(f"语料 {len(corpus)} 条；书目 {sorted(books.items(), key=lambda x: -x[1])}\n")
    print(f"{'术语':<10} {'原文':>5} {'白话':>5} {'条件值':>6} {'书目(top3)'}")
    for t in TERMS:
        cnt = {"original": 0, "baihua": 0, "cond": 0}
        hit_books = {}
        for e in corpus:
            if t in (e.get("original") or ""):
                cnt["original"] += 1
            if t in (e.get("baihua") or ""):
                cnt["baihua"] += 1
            conds = e.get("conditions") or {}
            vals = []
            for v in conds.values():
                vals += v if isinstance(v, list) else [v]
            if any(t in str(x) for x in vals):
                cnt["cond"] += 1
            if t in (e.get("original") or "") + (e.get("baihua") or ""):
                hit_books[e["book"]] = hit_books.get(e["book"], 0) + 1
        top = ", ".join(sorted(hit_books, key=lambda b: -hit_books[b])[:3]) or "-"
        print(f"{t:<10} {cnt['original']:>5} {cnt['baihua']:>5} {cnt['cond']:>6} {top}")


if __name__ == "__main__":
    main()
