#!/usr/bin/env python3
"""TCM-Library 共享工具库：分类常量 / Frontmatter 解析 / 文件发现。

零依赖（纯标准库）。Frontmatter 解析器仅覆盖本项目使用的 YAML 子集：
顶层标量、顶层数组（行内或缩进块）、一层嵌套字典（conditions / 通用）。
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# 分类体系（与 docs/classification.md 保持同步；改动先改 docs 再改这里）
# ---------------------------------------------------------------------------

# (category_id, category_zh, [(subcategory_id, subcategory_zh), ...])
CATEGORIES: List[Tuple[str, str, List[Tuple[str, str]]]] = [
    ("jichu", "中医基础理论", [
        ("yinyangwuxing", "阴阳五行"),
        ("zangxiang", "藏象"),
        ("jingluo", "经络"),
        ("qixuejinye", "气血津液"),
        ("bingyinbingji", "病因病机"),
        ("zhifa", "治则治法"),
    ]),
    ("zhenduan", "中医诊断", [
        ("siyang", "四诊"),
        ("bianzheng", "辨证"),
    ]),
    ("zhongyao", "中药学", [
        ("bencao", "本草著作"),
        ("yaoxing", "药性理论"),
        ("yaowu", "单味药"),
        ("paozhi", "炮制"),
        ("peiwu", "配伍与禁忌"),
    ]),
    ("fangji", "方剂学", [
        ("jingfang", "经方"),
        ("shifang", "时方"),
        ("chengfang", "成方制剂"),
        ("jieyao", "方解"),
    ]),
    ("zhenjiu", "针灸推拿", [
        ("jingluo", "经络"),
        ("shuxue", "腧穴"),
        ("cijiu", "刺法灸法"),
        ("tuina", "推拿"),
    ]),
    ("linchuang", "中医临床", [
        ("neike", "内科"),
        ("waike", "外科"),
        ("fuke", "妇科"),
        ("erke", "儿科"),
        ("gushang", "骨伤科"),
        ("wuguan", "五官科"),
        ("pifu", "皮肤科"),
        ("wenbing", "温病"),
    ]),
    ("yangsheng", "养生康复", [
        ("daoyin", "导引气功"),
        ("shiliao", "食疗药膳"),
        ("qiju", "起居调摄"),
        ("kangfu", "康复"),
    ]),
    ("yishi", "医史医家", [
        ("yijia", "医家"),
        ("yian", "医案"),
        ("xuepai", "学术流派"),
        ("shishu", "医史"),
    ]),
    ("jingdian", "经典医籍", [
        ("neijing", "黄帝内经"),
        ("shanghan", "伤寒论"),
        ("jingui", "金匮要略"),
        ("wenbing", "温病经典"),
        ("bencao", "本草经典"),
        ("nanjing", "难经"),
    ]),
    ("xiandai", "现代中医", [
        ("zhidao", "临床指南"),
        ("gongshi", "专家共识"),
        ("yanjiu", "现代研究"),
        ("jiaocai", "教材与规范"),
    ]),
]

CATEGORY_MAP: Dict[str, Dict[str, Any]] = {}
for cid, czh, subs in CATEGORIES:
    CATEGORY_MAP[cid] = {"name_zh": czh, "subs": {sid: szh for sid, szh in subs}}

# 结构化检索维度（manifest.match_fields；keywords 单独作为开放主题召回）
MATCH_FIELDS: List[str] = [
    "zhengxing", "zhifa", "bingzheng", "zhengzhuang",
    "fangming", "yaoming", "xuewei", "jingluo",
]
KEYWORDS_FIELD: str = "keywords"

CONDITION_FIELDS: List[str] = MATCH_FIELDS + [KEYWORDS_FIELD]

# 正文三层标记
LAYER_MARKS = ("【原文】", "【古注】", "【白话提要】")

# 不参与索引的文件（INDEX.md / README.md / _book.yaml / 模板）
SKIP_FILENAMES = ("INDEX.md", "README.md", "_book.yaml")


# ---------------------------------------------------------------------------
# Frontmatter 解析（纯标准库，YAML 子集）
# ---------------------------------------------------------------------------

def parse_scalar_token(raw: str) -> Any:
    """解析单个标量 token：引号字符串 / 整数 / 布尔 / null。"""
    raw = raw.strip()
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1].replace('\\"', '"').replace("\\n", "\n")
    if raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
        return raw[1:-1]
    if raw in ("null", "Null", "NULL", "~", ""):
        return None
    if raw in ("true", "True", "TRUE"):
        return True
    if raw in ("false", "False", "FALSE"):
        return False
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    return raw


def _parse_inline_list(raw: str) -> List[Any]:
    """解析行内数组：["a", "b", 3]"""
    raw = raw.strip()
    if not (raw.startswith("[") and raw.endswith("]")):
        raise ValueError(f"invalid inline list: {raw!r}")
    inner = raw[1:-1].strip()
    if not inner:
        return []
    # 简单分割：不处理含逗号的引号串（本库词条不含）
    return [parse_scalar_token(tok) for tok in inner.split(",")]


def _parse_block(block: str) -> Dict[str, Any]:
    """解析 frontmatter 块（--- 之间的内容），返回 dict。"""
    result: Dict[str, Any] = {}
    lines = block.split("\n")
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent != 0:
            raise ValueError(f"unexpected indented line at top level: {line!r}")
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if not rest:
            # 值在后续缩进行
            j = i + 1
            sub_lines: List[str] = []
            while j < n:
                nxt = lines[j]
                if not nxt.strip():
                    j += 1
                    continue
                nxt_indent = len(nxt) - len(nxt.lstrip(" "))
                if nxt_indent <= indent:
                    break
                sub_lines.append(nxt)
                j += 1
            if not sub_lines:
                result[key] = None
                i = j
                continue
            # 块内条目形如 "- a" / "- a: x" 或 "sub: v"
            block_items: List[Any] = []
            sub_dict: Dict[str, Any] = {}
            for sl in sub_lines:
                stripped = sl.lstrip()
                if stripped.startswith("- "):
                    item = stripped[2:].strip()
                    if ":" in item and not item.startswith(('"', "'")):
                        k2, _, v2 = item.partition(":")
                        sub_dict[k2.strip()] = parse_scalar_token(v2)
                    else:
                        block_items.append(parse_scalar_token(item))
                elif ":" in stripped:
                    k2, _, v2 = stripped.partition(":")
                    v2 = v2.strip()
                    if v2.startswith("["):
                        sub_dict[k2.strip()] = _parse_inline_list(v2)
                    else:
                        sub_dict[k2.strip()] = parse_scalar_token(v2)
                else:
                    block_items.append(parse_scalar_token(stripped))
            if block_items:
                result[key] = block_items
            elif sub_dict:
                result[key] = sub_dict
            else:
                result[key] = None
            i = j
            continue
        if rest.startswith("["):
            result[key] = _parse_inline_list(rest)
        else:
            result[key] = parse_scalar_token(rest)
        i += 1
    return result


def parse_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """将条目 .md 文本拆为 (frontmatter dict, 正文部分)。无 frontmatter 时返回 ({}, text)。"""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return {}, text
    fm_block = parts[0][3:].strip("\n")
    body = parts[1]
    if body.startswith("-"):
        body = body[1:]
    if body.startswith("\n"):
        body = body[1:]
    return _parse_block(fm_block), body


# ---------------------------------------------------------------------------
# 文件发现
# ---------------------------------------------------------------------------

def iter_entry_files(library_root: str):
    """遍历 library/ 下所有条目 .md（排除 INDEX.md / _*.md）。返回绝对路径列表。"""
    for root, _dirs, files in os.walk(library_root):
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            if fn in SKIP_FILENAMES or fn.startswith("_"):
                continue
            yield os.path.join(root, fn)


def rel_path(path: str, base: str) -> str:
    return os.path.relpath(path, base)


def id_from_path(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def read_entry(path: str) -> Tuple[Dict[str, Any], str]:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return parse_frontmatter(text)


def main() -> None:
    print("TCM-Library shared lib OK")
    print(f"categories: {[c[0] for c in CATEGORIES]}")


if __name__ == "__main__":
    main()
