#!/usr/bin/env python3
"""test_manifest_contract.py — 契约冒烟测试（模拟外部 RAG 消费端）。

验证 manifest.json 作为数据契约的稳定性：
  1. schema_version 受支持
  2. 顶层结构与 entries 字段完整
  3. conditions 九个字段全为数组
  4. id 全局唯一
  5. path 指向的文件存在且含三层标记（原文/白话提要）

用法: python3 tests/test_manifest_contract.py
退出码: 0=通过, 1=失败
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "manifest.json")

SUPPORTED_SCHEMA = 2.1
ENTRY_REQUIRED = ["id", "book", "type", "tier", "category", "subcategory",
                  "path", "weight", "title", "chapter", "conditions"]
CONDITION_FIELDS = ["zhengxing", "zhifa", "bingzheng", "zhengzhuang",
                    "fangming", "yaoming", "xuewei", "jingluo",
                    "siqi", "wuwei", "guijing", "keywords"]


def main() -> None:
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        m = json.load(f)
    errors: list[str] = []

    # 1. 版本
    if m.get("schema_version") != SUPPORTED_SCHEMA:
        errors.append(f"schema_version={m.get('schema_version')} 不受支持（期望 {SUPPORTED_SCHEMA}）")

    # 2. 顶层结构
    for k in ["match_fields", "match_rule", "categories", "books", "total", "entries"]:
        if k not in m:
            errors.append(f"manifest 缺少顶层字段 {k}")

    entries = m.get("entries", [])
    if len(entries) != m.get("total"):
        errors.append(f"entries 数量 {len(entries)} 与 total {m.get('total')} 不符")

    # 3/4. entries 字段与 id 唯一
    seen: Counter = Counter()
    for e in entries:
        for k in ENTRY_REQUIRED:
            if k not in e:
                errors.append(f"entry {e.get('id')}: 缺少字段 {k}")
        seen[e.get("id")] += 1
        cond = e.get("conditions")
        if not isinstance(cond, dict):
            errors.append(f"entry {e.get('id')}: conditions 非对象")
            continue
        for f in CONDITION_FIELDS:
            if f not in cond:
                errors.append(f"entry {e.get('id')}: conditions 缺少 {f}")
            elif not isinstance(cond[f], list):
                errors.append(f"entry {e.get('id')}: conditions.{f} 非数组")
    for k, v in seen.items():
        if v > 1:
            errors.append(f"id 重复: {k} x{v}")

    # 5. 路径可达 + 三层标记
    layer_re = re.compile(r"【(原文|古注|白话提要)】")
    for e in entries:
        p = os.path.join(ROOT, e["path"])
        if not os.path.exists(p):
            errors.append(f"entry {e['id']}: 文件不存在 {e['path']}")
            continue
        with open(p, encoding="utf-8") as fh:
            body = fh.read()
        marks = set(layer_re.findall(body))
        if "原文" not in marks:
            errors.append(f"entry {e['id']}: 缺【原文】层")
        if "白话提要" not in marks:
            errors.append(f"entry {e['id']}: 缺【白话提要】层")

    print(f"契约冒烟测试：{len(entries)} 条条目，错误 {len(errors)}")
    for e in errors:
        print(f"  [ERROR] {e}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
