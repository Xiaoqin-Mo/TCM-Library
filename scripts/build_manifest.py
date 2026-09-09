#!/usr/bin/env python3
"""build_manifest.py — 生成机读总清单 manifest.json。

确定性生成：遍历 library/ 全部条目，聚合为单一 JSON 文件，供检索引擎与
RAG 管线一次性加载。无时间戳、顺序稳定（路径排序）。

用法: python3 scripts/build_manifest.py [--out manifest.json]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from typing import Any, Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tcm_lib import (  # noqa: E402
    CATEGORIES,
    CATEGORY_MAP,
    MATCH_FIELDS,
    SKIP_FILENAMES,
    iter_entry_files,
    parse_frontmatter,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_DIR = os.path.join(ROOT, "library")
DEFAULT_OUT = os.path.join(ROOT, "manifest.json")

SCHEMA_VERSION = 2
NAME = "TCM-Library 中医知识百科全书检索库"
MATCH_RULE = ("entry is recalled iff, for every non-empty declared field, it intersects "
              "the query's same-field set; results sort by hit specificity, then weight, "
              "then path. keywords performs containment recall.")


def tier_from_weight(weight: int) -> int:
    if weight >= 8:
        return 1
    if weight >= 5:
        return 2
    return 3


def tier_name(tier: int) -> str:
    return {1: "核心", 2: "重要", 3: "拓展"}[tier]


def build() -> Dict[str, Any]:
    books: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    entries: List[Dict[str, Any]] = []

    for fp in iter_entry_files(LIBRARY_DIR):
        fm, _body = parse_frontmatter(open(fp, encoding="utf-8").read())
        if not fm or "id" not in fm:
            continue
        rel = os.path.relpath(fp, ROOT)
        parts = os.path.relpath(os.path.dirname(fp), LIBRARY_DIR).split(os.sep)
        category = parts[0]
        subcategory = parts[1] if len(parts) > 1 else ""
        weight = int(fm.get("weight", 0))
        entry = {
            "id": fm["id"],
            "book": fm.get("book", ""),
            "type": fm.get("type", ""),
            "tier": tier_from_weight(weight),
            "category": category,
            "subcategory": subcategory,
            "path": rel,
            "weight": weight,
            "title": fm.get("section_title", ""),
            "chapter": fm.get("chapter", ""),
            "conditions": fm.get("conditions", {}),
        }
        entries.append(entry)
        books[os.path.relpath(os.path.dirname(fp), LIBRARY_DIR)].append(entry)

    entries.sort(key=lambda e: e["path"])
    book_list = []
    for rel in sorted(books):
        group = books[rel]
        weights = [e["weight"] for e in group]
        tier = tier_from_weight(max(weights))
        parts = rel.split(os.sep)
        book_list.append({
            "dir": rel,
            "tier": tier,
            "tier_name": tier_name(tier),
            "category": parts[0],
            "subcategory": parts[1] if len(parts) > 1 else "",
            "count": len(group),
        })

    categories = []
    for cid, czh, subs in CATEGORIES:
        categories.append({
            "id": cid,
            "name": cid,
            "name_zh": czh,
            "subcategories": [{"id": sid, "name": sid, "name_zh": szh} for sid, szh in subs],
        })

    roots: Dict[str, Dict[str, Any]] = {}
    for rel in sorted(books):
        parts = rel.split(os.sep)
        cat = parts[0]
        sub = parts[1] if len(parts) > 1 else ""
        roots.setdefault(cat, {})[sub] = {"dir": rel, "count": len(books[rel])}

    return {
        "schema_version": SCHEMA_VERSION,
        "name": NAME,
        "match_fields": MATCH_FIELDS,
        "match_rule": MATCH_RULE,
        "roots": roots,
        "categories": categories,
        "books": book_list,
        "total": len(entries),
        "entries": entries,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Build manifest.json")
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()
    manifest = build()
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")
    print(f"manifest 生成完成：{manifest['total']} 条 → {args.out}")


if __name__ == "__main__":
    main()
