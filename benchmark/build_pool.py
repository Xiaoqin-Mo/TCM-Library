#!/usr/bin/env python3
"""build_pool.py — 查询集 × 多路检索 pooling，生成标注候选池。

流程：对每条查询，各检索器取 top-K → 按 doc id 合并去重 → 附带
book/chapter/section_title 与原文/白话片段（截断）→ 输出 pool JSON，
并按批切分为标注 CSV（列对齐 annotation/template.csv）。

用法：
    python benchmark/build_pool.py --depth 20
    python benchmark/build_pool.py --target 350     # 每批候选目标量（约 2h 标注量）
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "benchmark"))

from retrievers import build_retrievers, load_corpus  # noqa: E402

QUERIES = os.path.join(ROOT, "benchmark", "queries", "query_set_v1.json")
DATA = os.path.join(ROOT, "benchmark", "data")
POOL_OUT = os.path.join(DATA, "pool_v1.json")
CSV_DIR = os.path.join(ROOT, "benchmark", "gold")
SNIPPET = 160  # 原文/白话片段截断长度


def excerpt(text: str, n: int = SNIPPET) -> str:
    t = (text or "").replace("\n", " ").strip()
    return t if len(t) <= n else t[:n] + "…"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--depth", type=int, default=20, help="每检索器 top-K")
    ap.add_argument("--target", type=int, default=350, help="每批候选目标量")
    args = ap.parse_args()

    corpus = load_corpus()
    by_id = {e["id"]: e for e in corpus}
    queries = json.load(open(QUERIES, encoding="utf-8"))
    retrievers = build_retrievers(corpus, cache_dir=DATA)
    print(f"语料 {len(corpus)} · 查询 {len(queries)} · 检索器 {[r.name for r in retrievers]}")

    pool = []
    for q in queries:
        cand = {}
        # 检索词 = 查询本身 + 语域配对术语（术语对扩展，保证桥两侧候选入池）
        terms = [q["query"]]
        for t in (q.get("classical_term"), q.get("modern_term")):
            if t and t != q["query"] and t not in terms:
                terms.append(t)
        for term in terms:
            for r in retrievers:
                for doc_id, score in r.search(term, k=args.depth):
                    d = cand.setdefault(doc_id, {"ranks": {}, "max_score": -1e9})
                    d["ranks"][r.name] = round(score, 4)
                    d["max_score"] = max(d["max_score"], score)
        cands = []
        for doc_id in sorted(cand, key=lambda i: -cand[i]["max_score"]):
            e = by_id[doc_id]
            cands.append({
                "candidate_id": doc_id,
                "book": e.get("book"),
                "chapter": e.get("chapter"),
                "section_title": e.get("section_title"),
                "original": excerpt(e.get("original", "")),
                "baihua": excerpt(e.get("baihua", "")),
                "ranks": cand[doc_id]["ranks"],
            })
        pool.append({"qid": q["qid"], "query": q["query"], "form": q["form"],
                     "modern_term": q.get("modern_term", ""),
                     "classical_term": q.get("classical_term", ""),
                     "source": q.get("source", ""), "target_books": q.get("target_books", []),
                     "notes": q.get("notes", ""), "pool_terms": terms, "candidates": cands})
        print(f"{q['qid']} [{q['form']:>8}] {q['query'][:22]:<24} 候选 {len(cands)}")

    os.makedirs(DATA, exist_ok=True)
    with open(POOL_OUT, "w", encoding="utf-8") as f:
        json.dump(pool, f, ensure_ascii=False, indent=1)

    total = sum(len(p["candidates"]) for p in pool)
    print(f"\npool → {POOL_OUT}（{len(pool)} 查询，候选 {total}，平均 {total / len(pool):.0f}/查询）")

    # 按候选目标量切分标注 CSV（列对齐 annotation/template.csv）
    os.makedirs(CSV_DIR, exist_ok=True)
    cols = ["query_id", "query", "query_form", "candidate_id", "book", "chapter",
            "section_title", "原文片段", "白话片段", "relevance", "notes"]
    batches, cur, acc = [], [], 0
    for p in pool:
        cur.append(p)
        acc += len(p["candidates"])
        if acc >= args.target:
            batches.append(cur)
            cur, acc = [], 0
    if cur:
        batches.append(cur)
    for b, chunk in enumerate(batches, 1):
        path = os.path.join(CSV_DIR, f"annotation_batch{b}.csv")
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            for p in chunk:
                for c in p["candidates"]:
                    w.writerow([p["qid"], p["query"], p["form"], c["candidate_id"],
                                c["book"], c["chapter"], c["section_title"],
                                c["original"], c["baihua"], "", ""])
        n = sum(len(p["candidates"]) for p in chunk)
        print(f"batch{b}: {len(chunk)} 查询 · {n} 候选 → {path}")


if __name__ == "__main__":
    main()
