#!/usr/bin/env python3
"""build_corpus.py — 从 manifest + library 导出基准语料（三层正文 + conditions）。

输出 benchmark/data/corpus.jsonl，每行一条：
  {
    "id", "book", "chapter", "section_title", "type",
    "category", "subcategory", "weight",
    "conditions": {...},
    "original": str, "guzhu": str, "baihua": str
  }

纯标准库实现；层标记兼容 `**【原文】**` 等三种写法。
"""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from scripts.tcm_lib import iter_entry_files, parse_frontmatter  # noqa: E402

LIBRARY_DIR = os.path.join(ROOT, "library")
OUT_DIR = os.path.join(ROOT, "benchmark", "data")
OUT_PATH = os.path.join(OUT_DIR, "corpus.jsonl")

# 三层标记：**【原文】** / **【古注】** / **【白话提要】**
SPLIT_RE = re.compile(r"\*\*【(原文|古注|白话提要)】\*\*")


def split_layers(body: str) -> dict:
    parts = SPLIT_RE.split(body or "")
    layers = {"original": "", "guzhu": "", "baihua": ""}
    # parts = [pre, name, text, name, text, ...]
    for i in range(1, len(parts) - 1, 2):
        name, text = parts[i], parts[i + 1]
        key = {"原文": "original", "古注": "guzhu", "白话提要": "baihua"}[name]
        layers[key] = text.strip()
    return layers


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    n = 0
    coverage = {"original": 0, "guzhu": 0, "baihua": 0}
    with open(OUT_PATH, "w", encoding="utf-8", newline="\n") as f:
        for fp in iter_entry_files(LIBRARY_DIR):
            text = open(fp, encoding="utf-8").read()
            fm, body = parse_frontmatter(text)
            if not fm:
                continue
            layers = split_layers(body)
            for k in coverage:
                if layers[k]:
                    coverage[k] += 1
            rec = {
                "id": fm.get("id"),
                "book": fm.get("book"),
                "chapter": fm.get("chapter"),
                "section_title": fm.get("section_title"),
                "type": fm.get("type"),
                "category": fm.get("category"),
                "subcategory": fm.get("subcategory"),
                "weight": fm.get("weight"),
                "conditions": fm.get("conditions") or {},
                **layers,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1
    print(f"导出 {n} 条 → {OUT_PATH}")
    print(f"层覆盖：原文 {coverage['original']}、古注 {coverage['guzhu']}、白话 {coverage['baihua']}")


if __name__ == "__main__":
    main()
