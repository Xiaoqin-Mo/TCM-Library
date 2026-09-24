#!/usr/bin/env python3
"""validate_library.py — 交付前质量门。

逐项校验：
  1. Frontmatter 存在且含全部必填字段
  2. id 与文件名一致、全局唯一、格式合法（^[a-z0-9_]+$）
  3. type 属于受控枚举
  4. conditions 字段齐全且类型为数组
  5. category / subcategory 路径与分类体系一致
  6. weight ∈ [0,10]
  7. 正文含三层标记（原文/古注/白话提要），白话提要非空
  8. manifest.json 与条目实际一致（若存在则交叉核对）

用法: python3 scripts/validate_library.py [--skip-manifest]
     --skip-manifest  跳过第 8 项 manifest 交叉核对（内容线 PR 使用：
                      构建产物后置，条目格式校验通过即可；manifest 一致性由构建 PR 全量验证）
退出码: 0=通过, 1=有错误, 2=有警告
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from typing import Any, Dict, List, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tcm_lib import (  # noqa: E402
    CATEGORY_MAP,
    CONDITION_FIELDS,
    LAYER_MARKS,
    SKIP_FILENAMES,
    id_from_path,
    iter_entry_files,
    parse_frontmatter,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBRARY_DIR = os.path.join(ROOT, "library")
MANIFEST_PATH = os.path.join(ROOT, "manifest.json")
ID_RE = re.compile(r"^[a-z0-9_]+$")

# 各 type 建议的必填 conditions 维度（zhengxing 等建议；keywords 必填）
TYPE_REQUIRED_COND = {
    "fangji": ["fangming"],
    "yaowu": ["yaoming"],
    "shuxue": ["xuewei"],
    "tiaomu": [],
    "chapter": [],
    "yian": ["bingzheng"],
    "yijia": [],
    "koujue": [],
    "zhinan": ["bingzheng"],
    "reference": [],
}


def load_type_vocab() -> set:
    p = os.path.join(ROOT, "schema", "controlled_vocabulary.json")
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    return {t["v"] for t in data["fields"]["type"]["terms"]}


def check_entry(path: str, fm: Dict[str, Any], body: str, errors: List[str], warns: List[str]) -> None:
    rel = os.path.relpath(path, ROOT)
    # 1. 必填字段
    required = ["id", "book", "chapter", "section_title", "source_version",
                "author", "dynasty", "type", "conditions", "weight", "tags"]
    for k in required:
        if k not in fm:
            errors.append(f"[{rel}] 缺少必填字段 {k}")

    if "id" in fm:
        # 2. id 与文件名一致
        stem = id_from_path(path)
        if fm["id"] != stem:
            errors.append(f"[{rel}] id '{fm['id']}' 与文件名 '{stem}' 不一致")
        if not ID_RE.match(fm["id"]):
            errors.append(f"[{rel}] id 格式非法（仅允许小写字母/数字/下划线）: {fm['id']}")

    # 3. type 枚举
    if "type" in fm:
        if fm["type"] not in TYPE_VOCAB:
            errors.append(f"[{rel}] type '{fm['type']}' 不在受控枚举中")

    # 4. conditions 结构
    cond = fm.get("conditions")
    if not isinstance(cond, dict):
        if "conditions" in fm:
            errors.append(f"[{rel}] conditions 必须是对象")
    else:
        for field in CONDITION_FIELDS:
            if field not in cond:
                errors.append(f"[{rel}] conditions 缺少字段 {field}")
            elif not isinstance(cond[field], list):
                errors.append(f"[{rel}] conditions.{field} 必须是数组")
        extra = set(cond) - set(CONDITION_FIELDS)
        if extra:
            errors.append(f"[{rel}] conditions 含未知字段: {sorted(extra)}")
        # type 建议必填维度
        t = fm.get("type")
        if t and t in TYPE_REQUIRED_COND:
            for f in TYPE_REQUIRED_COND[t]:
                if not cond.get(f):
                    warns.append(f"[{rel}] type={t} 建议填写 conditions.{f}")

    # 5. 分类路径
    parts = os.path.relpath(os.path.dirname(path), LIBRARY_DIR).split(os.sep)
    cat = parts[0]
    if cat not in CATEGORY_MAP:
        errors.append(f"[{rel}] 目录 category '{cat}' 不在分类体系中")
    else:
        if len(parts) > 1:
            sub = parts[1]
            if sub not in CATEGORY_MAP[cat]["subs"]:
                errors.append(f"[{rel}] 目录 subcategory '{sub}' 不在 {cat} 的子类中")

    # 6. weight
    w = fm.get("weight")
    if isinstance(w, int) and not (0 <= w <= 10):
        errors.append(f"[{rel}] weight {w} 超出 [0,10]")

    # 7. 正文三层
    missing_marks = [m for m in LAYER_MARKS if m not in body]
    if missing_marks:
        errors.append(f"[{rel}] 正文缺少层标记: {missing_marks}")
    if "【白话提要】" in body and not body.split("【白话提要】", 1)[1].strip():
        errors.append(f"[{rel}] 白话提要层为空")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="TCM 库质量门")
    ap.add_argument("--skip-manifest", action="store_true",
                    help="跳过 manifest 交叉核对（内容线 PR 使用）")
    args = ap.parse_args()

    global TYPE_VOCAB
    TYPE_VOCAB = load_type_vocab()
    errors: List[str] = []
    warns: List[str] = []
    seen_ids: Counter = Counter()
    entries_in_lib: List[Tuple[str, str]] = []  # (id, relpath)

    for fp in iter_entry_files(LIBRARY_DIR):
        fm, body = parse_frontmatter(open(fp, encoding="utf-8").read())
        if not fm:
            errors.append(f"[{os.path.relpath(fp, ROOT)}] 缺少 YAML Frontmatter")
            continue
        if "id" in fm:
            seen_ids[fm["id"]] += 1
            entries_in_lib.append((fm["id"], os.path.relpath(fp, ROOT)))
        check_entry(fp, fm, body, errors, warns)

    dup = {k: v for k, v in seen_ids.items() if v > 1}
    if dup:
        errors.append(f"重复 id: {dup}")

    # 8. manifest 交叉核对（--skip-manifest 时跳过）
    if not args.skip_manifest and os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            manifest = json.load(f)
        manifest_ids = {e["id"] for e in manifest["entries"]}
        lib_ids = {i for i, _ in entries_in_lib}
        if manifest_ids != lib_ids:
            errors.append(f"manifest 与 library 不一致：仅 manifest 有 {sorted(manifest_ids - lib_ids)[:5]}；"
                          f"仅 library 有 {sorted(lib_ids - manifest_ids)[:5]}")
        if manifest["total"] != len(lib_ids):
            errors.append(f"manifest.total={manifest['total']} 与实测 {len(lib_ids)} 不符")

    print(f"校验完成：{len(entries_in_lib)} 条条目，错误 {len(errors)}，警告 {len(warns)}")
    for e in errors:
        print(f"  [ERROR] {e}")
    for w in warns:
        print(f"  [WARN]  {w}")
    sys.exit(0 if not errors else (1 if errors else 2))


if __name__ == "__main__":
    main()
