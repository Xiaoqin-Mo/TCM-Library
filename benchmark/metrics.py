#!/usr/bin/env python3
"""metrics.py — 检索评测指标（Recall@k / nDCG@k / MRR）。

支持分级金标准：gold = {doc_id: grade(0-3)}；若为集合则按二值（相关=1）处理。
纯标准库实现。
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Set, Union


def _grades(gold: Union[Dict[str, int], Set[str], Iterable[str]]) -> Dict[str, int]:
    if isinstance(gold, dict):
        return gold
    return {g: 1 for g in gold}


def recall_at_k(ranked: List[str], gold, k: int) -> float:
    g = _grades(gold)
    rel = {d for d, v in g.items() if v >= 1}
    if not rel:
        return 0.0
    hit = sum(1 for d in ranked[:k] if d in rel)
    return hit / len(rel)


def _dcg(ranked: List[str], gold, k: int) -> float:
    g = _grades(gold)
    dcg = 0.0
    for i, d in enumerate(ranked[:k]):
        v = g.get(d, 0)
        if v > 0:
            dcg += (2 ** v - 1) / math.log2(i + 2)
    return dcg


def ndcg_at_k(ranked: List[str], gold, k: int) -> float:
    g = _grades(gold)
    ideal = sorted(g.values(), reverse=True)[:k]
    idcg = sum((2 ** v - 1) / math.log2(i + 2) for i, v in enumerate(ideal) if v > 0)
    if idcg == 0:
        return 0.0
    return _dcg(ranked, g, k) / idcg


def mrr(ranked: List[str], gold) -> float:
    g = _grades(gold)
    rel = {d for d, v in g.items() if v >= 1}
    for i, d in enumerate(ranked):
        if d in rel:
            return 1.0 / (i + 1)
    return 0.0


def summarize(ranked: List[str], gold, ks=(10, 50)) -> Dict[str, float]:
    out = {}
    for k in ks:
        out[f"R@{k}"] = round(recall_at_k(ranked, gold, k), 4)
        out[f"nDCG@{k}"] = round(ndcg_at_k(ranked, gold, k), 4)
    out["MRR"] = round(mrr(ranked, gold), 4)
    return out
