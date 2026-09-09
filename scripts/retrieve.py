#!/usr/bin/env python3
"""retrieve.py — 结构化检索器（CLI + 可导入）。

匹配语义（与 manifest.match_rule 一致）：
  - 组内 AND：查询中同一声明的字段须全部命中（如 zhengxing+zhifa）
  - 维度间 OR：不同字段任一命中即召回
  - keywords：开放主题词，包含式召回
  - 排序：命中特异性（非空声明字段命中数）→ weight → path

用法:
  python3 scripts/retrieve.py --zhengxing 风寒束表 --zhifa 解表散寒
  python3 scripts/retrieve.py --keyword 消渴 --limit 10 --detail
  python3 scripts/retrieve.py --show-fields
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "manifest.json")


def load_manifest(path: str = MANIFEST_PATH) -> Dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _intersects(declared: List[str], query_vals: Set[str]) -> bool:
    return bool(declared) and bool(set(declared) & query_vals)


def _keywords_hit(kw: List[str], query_kw: List[str]) -> bool:
    if not kw or not query_kw:
        return False
    for k in query_kw:
        for cand in kw:
            if k in cand or cand in k:
                return True
    return False


def query(manifest: Dict[str, Any], cond: Dict[str, List[str]], include_general: bool = True,
          limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """按 cond（结构化条件 dict）检索。cond 为空时按 include_general 决定是否全量返回。"""
    match_fields = manifest.get("match_fields", [])
    query_kw = cond.get("keywords", [])
    # 计算特异性：命中的声明字段数（组内 AND 计一次）
    specificity: Dict[str, int] = {}
    results: List[Dict[str, Any]] = []

    for e in manifest["entries"]:
        ec = e["conditions"]
        declared = [f for f in match_fields if ec.get(f) and cond.get(f)]
        if not declared and not query_kw:
            if not include_general:
                continue
            spec = 0
        else:
            ok = True
            for f in match_fields:
                if cond.get(f) and not _intersects(ec.get(f, []), set(cond[f])):
                    ok = False
                    break
            if ok and query_kw and not _keywords_hit(ec.get("keywords", []), query_kw):
                ok = False
            if not ok:
                continue
            spec = len(declared) + (1 if query_kw and _keywords_hit(ec.get("keywords", []), query_kw) else 0)
        specificity[e["id"]] = spec
        results.append(e)

    results.sort(key=lambda e: (-specificity[e["id"]], -e["weight"], e["path"]))
    if limit:
        results = results[:limit]
    return results


def print_results(results: List[Dict[str, Any]], detail: bool = False) -> None:
    if not results:
        print("无命中结果。")
        return
    for e in results:
        cond = e["conditions"]
        line = (f"[{e['weight']}] {e['book']} · {e['chapter']} — {e['title']} "
                f"({e['category']}/{e['subcategory']})  {e['path']}")
        print(line)
        if detail:
            for f in ["zhengxing", "zhifa", "bingzheng", "zhengzhuang", "fangming", "yaoming", "xuewei", "jingluo", "keywords"]:
                vals = cond.get(f, [])
                if vals:
                    print(f"    {f}: {'、'.join(vals)}")


def main() -> None:
    ap = argparse.ArgumentParser(description="TCM-Library 结构化检索")
    ap.add_argument("--zhengxing", action="append", default=[])
    ap.add_argument("--zhifa", action="append", default=[])
    ap.add_argument("--bingzheng", action="append", default=[])
    ap.add_argument("--zhengzhuang", action="append", default=[])
    ap.add_argument("--fangming", action="append", default=[])
    ap.add_argument("--yaoming", action="append", default=[])
    ap.add_argument("--xuewei", action="append", default=[])
    ap.add_argument("--jingluo", action="append", default=[])
    ap.add_argument("--keyword", action="append", default=[], help="开放主题词（可多次）")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--detail", action="store_true")
    ap.add_argument("--show-fields", action="store_true", help="显示受支持的结构化字段")
    args = ap.parse_args()

    if args.show_fields:
        m = load_manifest()
        print("结构化检索字段（组内 AND、维度间 OR）：")
        for f in m["match_fields"]:
            print(f"  --{f}")
        print("  开放主题词：--keyword")
        return

    cond = {
        "zhengxing": args.zhengxing,
        "zhifa": args.zhifa,
        "bingzheng": args.bingzheng,
        "zhengzhuang": args.zhengzhuang,
        "fangming": args.fangming,
        "yaoming": args.yaoming,
        "xuewei": args.xuewei,
        "jingluo": args.jingluo,
        "keywords": args.keyword,
    }
    manifest = load_manifest()
    results = query(manifest, cond, include_general=False, limit=args.limit)
    print(f"命中 {len(results)} 条：")
    print_results(results, detail=args.detail)


if __name__ == "__main__":
    main()
