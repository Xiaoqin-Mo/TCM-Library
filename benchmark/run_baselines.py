#!/usr/bin/env python3
"""run_baselines.py — 冒烟查询跑基线，验证评测流水线。

用法：
    python benchmark/run_baselines.py --smoke
    python benchmark/run_baselines.py --gold benchmark/gold/<file>.json   # Phase 1 正式评测

--smoke 使用内置临时相关集（取自回归测试已知命中），仅验证管线，非正式金标准。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "benchmark"))

from metrics import summarize  # noqa: E402
from retrievers import build_retrievers, load_corpus  # noqa: E402

# 冒烟查询：临时相关集仅用于验证管线（取自既有回归已知命中，非正式金标准）
SMOKE_QUERIES = [
    {"qid": "s01", "query": "感冒发热恶风汗出，宜用何方？", "form": "现代术语",
     "gold": ["guizhitang_001", "shanghan_013", "guizhijiagegengtang_001"]},
    {"qid": "s02", "query": "太阳中风", "form": "文言术语",
     "gold": ["guizhitang_001", "shanghan_013", "guizhijiagegengtang_001"]},
    {"qid": "s03", "query": "解表散寒", "form": "文言术语",
     "gold": ["baizhi_001", "qianghuo_001", "shengjiang_001", "xixin_001", "zisuye_001",
              "xiaoqinglongtang_001"]},
    {"qid": "s04", "query": "桂枝", "form": "文言术语",
     "gold": ["guizhi_001", "guizhitang_001"]},
    {"qid": "s05", "query": "足三里", "form": "文言术语",
     "gold": ["zusanli_001"]},
    {"qid": "s06", "query": "白芷", "form": "现代术语",
     "gold": ["baizhi_001"]},
    {"qid": "s07", "query": "外感风寒，有哪些解表药可用？", "form": "现代术语",
     "gold": ["baizhi_001", "qianghuo_001", "shengjiang_001", "xixin_001", "zisuye_001"]},
]


def load_gold(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", default=None, help="正式金标准 JSON（Phase 1）")
    ap.add_argument("--smoke", action="store_true", help="冒烟模式（内置临时相关集）")
    ap.add_argument("--k", type=int, default=10)
    args = ap.parse_args()

    corpus = load_corpus()
    print(f"语料 {len(corpus)} 条")

    if args.gold:
        queries = load_gold(args.gold)["queries"]
    elif args.smoke:
        queries = SMOKE_QUERIES
    else:
        raise SystemExit("请指定 --smoke 或 --gold")

    retrievers = build_retrievers(corpus)
    print(f"检索器：{[r.name for r in retrievers]}\n")

    rows = []
    for q in queries:
        gold = {d: 1 for d in q["gold"]}
        line = [q["qid"], q["query"], q["form"]]
        for r in retrievers:
            ranked = [i for i, _ in r.search(q["query"], k=args.k)]
            m = summarize(ranked, gold, ks=(10, 50))
            line.append(m)
        rows.append({"qid": q["qid"], "query": q["query"], "form": q["form"],
                     "results": {r.name: [i for i, _ in r.search(q["query"], k=args.k)]
                                 for r in retrievers}})

    # 汇总表（按检索器列）
    header = ["qid", "form", "query"] + [r.name for r in retrievers]
    print(" | ".join(header[:3]) + "   " + "   ".join(header[3:]))
    for row in rows:
        cells = [row["qid"], row["form"], row["query"][:16]]
        for r in retrievers:
            m = row["results"][r.name] and summarize(
                [i for i, _ in r.search(row["query"], k=args.k)],
                {d: 1 for d in next(q["gold"] for q in queries if q["qid"] == row["qid"])},
                ks=(10, 50))
            cells.append(f"R@{args.k}={m.get(f'R@{args.k}')} n={m.get('nDCG@10')}")
        print(" | ".join(cells))

    # 平均指标
    print("\n=== 平均（冒烟临时集，仅供管线验证）===")
    avg = {r.name: {} for r in retrievers}
    for q in queries:
        gold = {d: 1 for d in q["gold"]}
        for r in retrievers:
            ranked = [i for i, _ in r.search(q["query"], k=50)]
            m = summarize(ranked, gold, ks=(10, 50))
            for key in ("R@10", "nDCG@10", "MRR"):
                avg[r.name].setdefault(key, []).append(m[key])
    for name, acc in avg.items():
        print(name, {k: round(sum(v) / len(v), 4) for k, v in acc.items()})

    os.makedirs(os.path.join(ROOT, "benchmark", "data"), exist_ok=True)
    with open(os.path.join(ROOT, "benchmark", "data", "smoke_results.json"), "w",
              encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print("\n冒烟 top-k 明细 → benchmark/data/smoke_results.json")


if __name__ == "__main__":
    main()
