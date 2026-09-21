#!/usr/bin/env python3
"""retrievers.py — 基线检索器。

- BM25：字符 bigram（不分词）与 jieba 分词两种 tokenizer；
  语料层可选 original（原文）/ baihua（白话）作为索引字段。
- 向量：sentence-transformers（bge-small-zh-v1.5），索引白话层；
  未安装时标记不可用，不影响 BM25 基线。

接口约定（供 run_baselines.py 与 Phase 1 harness 使用）：
    retriever.search(query: str, k: int) -> List[(id, score)]
"""

from __future__ import annotations

import math
import os
import re
from typing import Callable, Dict, List, Tuple

import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

try:
    import jieba
except ImportError:
    jieba = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

CORPUS_DEFAULT = os.path.join(ROOT, "benchmark", "data", "corpus.jsonl")

_PUNCT_RE = re.compile(r"[\s，。、；：？！“”‘’（）《》〈〉【】·…—\-—,.;:?!()\[\]{}\"'<>/\\|~`@#$%^&*_+=]+")


def load_corpus(path: str = CORPUS_DEFAULT) -> List[dict]:
    import json

    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def tokenize_char_bigram(text: str) -> List[str]:
    t = _PUNCT_RE.sub("", text or "")
    return [t[i : i + 2] for i in range(max(0, len(t) - 1))]


def tokenize_jieba(text: str) -> List[str]:
    if jieba is None:
        raise RuntimeError("jieba 未安装")
    t = _PUNCT_RE.sub("", text or "")
    return [w for w in jieba.lcut(t) if w]


class BM25:
    """经典 BM25（k1=1.5, b=0.75）。"""

    def __init__(self, docs: List[Tuple[str, List[str]]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_ids: List[str] = [d[0] for d in docs]
        self.doc_len = [len(d[1]) for d in docs]
        self.avgdl = sum(self.doc_len) / len(docs) if docs else 0.0
        df: Dict[str, int] = {}
        self.postings: Dict[str, List[Tuple[int, int]]] = {}
        for i, (_, toks) in enumerate(docs):
            seen = set()
            for t in toks:
                if t in seen:
                    continue
                seen.add(t)
                df[t] = df.get(t, 0) + 1
                self.postings.setdefault(t, []).append((i, 1))
        n = len(docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def search(self, query_tokens: List[str], k: int = 10) -> List[Tuple[str, float]]:
        scores = [0.0] * len(self.doc_ids)
        qtf: Dict[str, int] = {}
        for t in query_tokens:
            qtf[t] = qtf.get(t, 0) + 1
        for t, qf in qtf.items():
            idf = self.idf.get(t)
            if idf is None:
                continue
            for i, _ in self.postings.get(t, []):
                tf = 1
                dl = self.doc_len[i]
                scores[i] += idf * (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
        order = sorted(range(len(scores)), key=lambda i: (-scores[i], self.doc_ids[i]))
        return [(self.doc_ids[i], scores[i]) for i in order if scores[i] > 0][:k]


class BM25Retriever:
    def __init__(self, corpus: List[dict], field: str = "original", tokenizer: str = "char"):
        tok: Callable[[str], List[str]] = tokenize_char_bigram if tokenizer == "char" else tokenize_jieba
        docs = [(e["id"], tok(e.get(field, ""))) for e in corpus]
        self.model = BM25(docs)
        self.field = field
        self.tokenizer = tokenizer
        self.name = f"bm25-{tokenizer}({field})"

    def search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        tok = tokenize_char_bigram if self.tokenizer == "char" else tokenize_jieba
        return self.model.search(tok(query), k=k)


class VectorRetriever:
    def __init__(self, corpus: List[dict], field: str = "baihua", model_name: str = "BAAI/bge-small-zh-v1.5"):
        if SentenceTransformer is None:
            raise RuntimeError("sentence-transformers 未安装")
        self.model = SentenceTransformer(model_name)
        self.field = field
        self.name = f"vector({field})"
        self.ids = [e["id"] for e in corpus]
        self.emb = self.model.encode([e.get(field, "") for e in corpus],
                                     normalize_embeddings=True, show_progress_bar=False)

    def search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        import numpy as np

        q = self.model.encode([query], normalize_embeddings=True)[0]
        scores = self.emb @ q
        order = np.argsort(-scores)[:k]
        return [(self.ids[i], float(scores[i])) for i in order]


def build_retrievers(corpus: List[dict], with_vector: bool = True) -> List:
    r = [
        BM25Retriever(corpus, "original", "char"),
        BM25Retriever(corpus, "baihua", "char"),
    ]
    if jieba is not None:
        r.append(BM25Retriever(corpus, "original", "jieba"))
        r.append(BM25Retriever(corpus, "baihua", "jieba"))
    if with_vector:
        try:
            r.append(VectorRetriever(corpus))
        except RuntimeError as e:
            print(f"[skip] 向量基线：{e}")
    return r
