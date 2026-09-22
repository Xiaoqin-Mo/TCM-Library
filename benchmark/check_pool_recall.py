#!/usr/bin/env python3
"""check_pool_recall.py — pooling 质量门：已知相关条目是否在候选池中。

对照回归测试已知命中（作为弱金标准），检查 query_set_v1 中对应查询的
候选池是否覆盖。漏掉金标准说明 pooling 深度/检索器不足。
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

POOL = os.path.join(ROOT, "benchmark", "data", "pool_v1.json")

# (qid, 已知相关 id 集合) —— 弱金标准，仅用回归测试已验证的 id
KNOWN = [
    ("q019", {"guizhijiagegengtang_001", "guizhitang_001", "zhangzhongjing_002"}),
    ("q038", {"guizhitang_001", "guizhijiagegengtang_001"}),
    ("q054", {"zusanli_001"}),
    ("q001", {"ganmao_002", "guizhitang_001"}),
]


def main() -> None:
    pool = json.load(open(POOL, encoding="utf-8"))
    by_qid = {p["qid"]: p for p in pool}
    ok = True
    for prefix, expected in KNOWN:
        q = by_qid.get(prefix)
        if q is None:
            print(f"MISS 查询 {prefix} 不存在"); ok = False; continue
        have = {c["candidate_id"] for c in q["candidates"]}
        miss = sorted(expected - have)
        status = "PASS" if not miss else "FAIL"
        if miss:
            ok = False
        print(f"{status} {prefix} [{q['query'][:14]}] 池 {len(have)}：漏 {miss if miss else '无'}")
    print("\npool 质量门", "通过" if ok else "未通过（上方 FAIL 项需加大深度或补检索器）")


if __name__ == "__main__":
    main()
