#!/usr/bin/env python3
"""export_vocab.py — 从库中统计并更新受控词表（controlled_vocabulary.json）。

对 conditions.zhengxing / zhifa / jingluo 与 type 做词频统计，回写受控词表，
使词表与实际库内容保持同步（open=true 的字段自动合并新词）。

用法: python3 scripts/export_vocab.py [--check]   # --check 只统计不写回
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tcm_lib import (  # noqa: E402
    iter_entry_files,
    parse_frontmatter,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_DIR = os.path.join(ROOT, "library")
VOCAB_PATH = os.path.join(ROOT, "schema", "controlled_vocabulary.json")

COUNT_FIELDS = ["zhengxing", "zhifa", "jingluo", "siqi", "wuwei", "guijing"]


def collect() -> dict:
    counters = {f: Counter() for f in COUNT_FIELDS}
    type_counter: Counter = Counter()
    n = 0
    for fp in iter_entry_files(LIBRARY_DIR):
        fm, _ = parse_frontmatter(open(fp, encoding="utf-8").read())
        if not fm:
            continue
        n += 1
        t = fm.get("type")
        if t:
            type_counter[t] += 1
        cond = fm.get("conditions") or {}
        for f in COUNT_FIELDS:
            for v in cond.get(f, []):
                counters[f][v] += 1
    return {"type": type_counter, "counters": counters, "n": n}


def merge_terms(existing: list, counts: Counter) -> list:
    by_v = {t["v"]: t for t in existing}
    merged = []
    for v in counts:
        if v in by_v:
            by_v[v]["n"] = counts[v]
        else:
            by_v[v] = {"v": v, "n": counts[v]}
    for v, t in sorted(by_v.items(), key=lambda kv: (-kv[1].get("n", 0), kv[0])):
        t["n"] = counts.get(v, t.get("n", 0))
        merged.append(t)
    return merged


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只统计不写回")
    args = ap.parse_args()

    data = collect()
    with open(VOCAB_PATH, encoding="utf-8") as f:
        vocab = json.load(f)

    vocab["scanned_entries"] = data["n"]
    fields = vocab["fields"]

    type_terms = merge_terms(fields["type"]["terms"], data["type"])
    fields["type"]["terms"] = type_terms
    fields["type"]["distinct"] = len(type_terms)
    for f in COUNT_FIELDS:
        terms = merge_terms(fields[f]["terms"], data["counters"][f])
        fields[f]["terms"] = terms
        fields[f]["distinct"] = len(terms)

    print(f"统计 {data['n']} 条：type {len(type_terms)} 种；"
          + "；".join(f"{f} {len(fields[f]['terms'])} 词" for f in COUNT_FIELDS))
    if not args.check:
        with open(VOCAB_PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(vocab, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"已写回 {VOCAB_PATH}")
    else:
        print("--check：未写回")


if __name__ == "__main__":
    main()
