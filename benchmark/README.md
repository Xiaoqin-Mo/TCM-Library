# benchmark/ · TCM 检索基准（plan-fbr Phase 0–4）

> 计划：`docs/plan-fbr.md` · 协调：Issue #94 · 语料：TCM-Library

## 状态（Phase 0）

- **冻结版本**：`dev @ 7c81131ca80936cd17cd6c72c76baebd6dd67e17`（3101 条，validate 0 错 0 警、回归 18/18、契约 0 错）。
  基准发布绑定本版本；后续语料变更需显式升版并记录。
- **语料导出**：`python benchmark/build_corpus.py` → `benchmark/data/corpus.jsonl`
  （每条：元数据 + conditions + 原文/古注/白话三层正文）。
- **基线**：`python benchmark/run_baselines.py --smoke`
  - BM25（字符 bigram，不分词）· 原文层 / 白话层
  - BM25（jieba 分词）· 原文层 / 白话层
  - 向量（bge-small-zh-v1.5，白话语义层）——需 `pip install -r benchmark/requirements.txt`
- **评测 harness**：`benchmark/metrics.py`（Recall@k / nDCG@k / MRR，支持分级金标准）。

## 目录

```
benchmark/
├── README.md           # 本文件（状态与运行方式）
├── requirements.txt    # jieba；sentence-transformers（向量基线）
├── build_corpus.py     # 从 manifest + library 导出三层语料
├── metrics.py          # Recall@k / nDCG@k / MRR
├── retrievers.py       # BM25（char/jieba）× 原文/白话层；向量检索
├── run_baselines.py    # 冒烟查询跑基线 → 指标 + top-k 抽样
├── queries/            # 正式查询集（Phase 1 起）
├── gold/               # 相关性金标准（Phase 1 起）
└── data/               # 生成数据（gitignore）
```

## 冒烟说明

`--smoke` 使用内置临时相关集（取自回归测试已知命中），仅用于验证管线，
**不是正式金标准**；正式评测在 Phase 1 金标准冻结后执行（查询在 `queries/`、金标准在 `gold/`）。
