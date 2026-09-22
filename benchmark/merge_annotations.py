#!/usr/bin/env python3
"""merge_annotations.py — 合并 gold/ 下标注 CSV，输出金标准 JSON 并计算 IAA。

流程：
  1. 读取 gold/annotation_batch*.csv（UTF-8-sig）
  2. 按 (query_id, candidate_id) 聚合 relevance
  3. 若双人标注（同一 query+candidate 出现两次），计算 Cohen's κ
  4. 输出 benchmark/data/gold_standard.json：{qid: {doc_id: relevance}}

用法：
    python benchmark/merge_annotations.py
    python benchmark/merge_annotations.py --iaa-only   # 仅打印 IAA，不写文件
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOB = os.path.join(ROOT, "benchmark", "gold", "annotation_batch*.csv")
OUT = os.path.join(ROOT, "benchmark", "data", "gold_standard.json")

RELEVANCE_SCALE = [0, 1, 2, 3]


def load_rows():
    rows = []
    for path in sorted(glob.glob(GLOB)):
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                rel = (r.get("relevance") or "").strip()
                if not rel:
                    continue
                try:
                    rel_int = int(rel)
                except ValueError:
                    print(f"[warn] {os.path.basename(path)} 无效 relevance={rel!r} (qid={r.get('query_id')}, doc={r.get('candidate_id')})")
                    continue
                if rel_int not in RELEVANCE_SCALE:
                    print(f"[warn] {os.path.basename(path)} relevance={rel_int} 不在 0-3 (qid={r.get('query_id')})")
                    continue
                rows.append({
                    "qid": r["query_id"],
                    "doc": r["candidate_id"],
                    "rel": rel_int,
                    "batch": os.path.basename(path),
                })
    return rows


def cohens_kappa(labels_a, labels_b):
    """Cohen's κ，分级标注（0-3）。"""
    n = len(labels_a)
    if n == 0:
        return None
    agree = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    po = agree / n
    cats = set(labels_a) | set(labels_b)
    pa = pb = 0.0
    for c in cats:
        pa += (sum(1 for x in labels_a if x == c) / n) * (sum(1 for x in labels_b if x == c) / n)
    pe = pa if pa else 1.0
    if pe == 1.0:
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iaa-only", action="store_true")
    args = ap.parse_args()

    rows = load_rows()
    if not rows:
        print("[!] 无已标注行（relevance 列全空）。标注者填写后再跑。")
        sys.exit(0)

    # 聚合：(qid, doc) -> [rel1, rel2, ...]（可能有两人标注）
    by_pair = defaultdict(list)
    for r in rows:
        by_pair[(r["qid"], r["doc"])].append(r["rel"])

    # IAA：找双人标注的 pair
    double = {k: v for k, v in by_pair.items() if len(v) >= 2}
    if double:
        a = [v[0] for v in double.values()]
        b = [v[1] for v in double.values()]
        k = cohens_kappa(a, b)
        print(f"双人标注 pair 数: {len(double)}")
        print(f"Cohen's κ = {k:.3f}" if k is not None else "κ 无法计算")
        if k is not None and k < 0.6:
            print("[warn] κ < 0.6，需扩大仲裁范围（见标注指南）")
    else:
        print("[info] 无双人标注 pair（单人标注未抽样重叠），跳过 IAA")

    if args.iaa_only:
        return

    # 金标准：有标注的 pair，双人标注取平均（四舍五入）
    gold = defaultdict(dict)
    for (qid, doc), rels in by_pair.items():
        avg = round(sum(rels) / len(rels))
        gold[qid][doc] = avg

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(gold, f, ensure_ascii=False, indent=2)
    n_docs = sum(len(v) for v in gold.values())
    print(f"金标准写入: {OUT}")
    print(f"  查询数: {len(gold)}，(query,doc) 标注数: {n_docs}")


if __name__ == "__main__":
    main()
