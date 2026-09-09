# RAG 消费端契约 · RAG Consumer Contract

> 本文件是**独立 RAG 仓库对接本库的权威契约**。TCM-Library 为纯文档仓库，
> RAG 管线不在此实现；消费端（向量检索 / 混合重排 / 前端后端）按下述契约读取数据。
> 契约机器校验见 `tests/test_manifest_contract.py`。

## 1. 仓库职责边界

| 仓库 | 职责 | 拥有者 |
| --- | --- | --- |
| `TCM-Library`（本仓库） | 条目内容 + `manifest.json` 数据契约 + 构建/校验工具 | 数据侧 |
| `tcm-rag`（独立仓库，待建） | 摄取 → 向量化 → 检索 → 重排 → 接口 | 消费侧 |
| `tcm-gui`（独立仓库，待建） | Web/桌面 GUI | 展示侧 |

数据变更通过 CI 重新构建 `manifest.json`；RAG 仓库订阅版本变化后重建索引。

## 2. 数据契约：manifest.json

由 `scripts/build_manifest.py` 确定性生成，位于仓库根目录。顶层结构：

```json
{
  "schema_version": 2,
  "name": "TCM-Library 中医知识百科全书检索库",
  "match_fields": ["zhengxing", "zhifa", "bingzheng", "zhengzhuang",
                   "fangming", "yaoming", "xuewei", "jingluo"],
  "match_rule": "…",
  "roots": { "<category>": { "<subcategory>": { "dir": "…", "count": 0 } } },
  "categories": [ { "id", "name", "name_zh", "subcategories": [...] } ],
  "books": [ { "dir", "tier", "tier_name", "category", "subcategory", "count" } ],
  "total": 0,
  "entries": [ { "id", "book", "type", "tier", "category", "subcategory",
                 "path", "weight", "title", "chapter", "conditions" } ]
}
```

### 2.1 关键字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `schema_version` | int | 契约版本（当前 2）。破坏性变更递增主版本；兼容性新增递增次版本 |
| `entries[].id` | string | **全局唯一、稳定的主键**，RAG 文档 ID 直接用 |
| `entries[].path` | string | 条目 `.md` 相对路径（相对仓库根） |
| `entries[].conditions` | object | 结构化检索条件（九个数组字段，见 §3） |
| `entries[].weight` | int | 排序权重（0–10），供重排特征 |
| `entries[].tier` | int | 书籍梯队（1 核心 / 2 重要 / 3 拓展），聚合自 weight |
| `categories[]` | array | 分类体系（id/name_zh/subcategories），供导航与过滤 |

### 2.2 版本策略

- `schema_version` 升主版本：消费端必须适配（字段删除/改名/语义变化）
- 升次版本：向后兼容（新增可选字段）
- 消费端读取时**校验版本**，不匹配则告警或走兼容分支

## 3. 条目正文结构

`path` 指向的 Markdown 文件结构固定：

```
---                     ← YAML Frontmatter（与 manifest.entries[].conditions 一致）
id / book / chapter / section_title / source_version / author / dynasty
type / conditions / weight / tags
---

### <section_title>

**【原文】**          ← 原文层：古籍原文照录 / 现代文献要点
**【古注】**          ← 古注层：可省略
**【白话提要】**      ← 白话层：白话转述，语义检索友好（必填）
```

**读取约定**：按层标记 `【原文】/【古注】/【白话提要】` 切分三块；层标记缺失视为该层为空。

## 4. 推荐接入流程

```
1. 摄取    读取 manifest.json → 对每个 entry 读取 path 指向的 .md
2. 切分    按层标记分为原文 / 古注 / 白话提要 三块文本
3. 建索引  结构化字段 → 精确过滤索引（Filter）
           白话提要 → 向量索引（语义检索主通道）
           原文层   → 可选：原文向量/关键词索引（引经据典场景）
4. 检索    结构化过滤（跨字段 AND、同字段 OR，语义同 retrieve.py）
           ∩ 向量语义召回（白话层 top-k）
           ∩ keywords 主题召回
5. 重排    混合分 = α·向量相似度 + β·weight 归一化 + γ·特异性（命中字段数）
           再按 (specificity, weight) 兜底稳定排序
6. 返回    返回条目 id / title / book / chapter + 三层正文切片 + 来源
```

## 5. 消费端最小实现（参考，非正式 RAG）

以下为读取契约的最小示例，纯标准库，可直接移植：

```python
import json, re, sys

def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def read_entry(entry, repo_root):
    """读取条目正文，按层标记切分为 (原文, 古注, 白话提要)。"""
    with open(f"{repo_root}/{entry['path']}", encoding="utf-8") as f:
        text = f.read()
    body = text.split("\n---", 1)[1] if text.startswith("---") else text
    layers = {"【原文】": "", "【古注】": "", "【白话提要】": ""}
    # 按标记顺序切分
    marks = re.findall(r"【(原文|古注|白话提要)】", body)
    parts = re.split(r"【(?:原文|古注|白话提要)】", body)[1:]
    for m, p in zip(marks, parts):
        layers[f"【{m}】"] = p.strip()
    return layers

if __name__ == "__main__":
    m = load_manifest(sys.argv[1] if len(sys.argv) > 1 else "manifest.json")
    assert m["schema_version"] == 2, f"unsupported schema {m['schema_version']}"
    for e in m["entries"][:3]:          # 演示：读前 3 条
        layers = read_entry(e, ".")
        print(e["id"], e["title"], "| 白话提要:", layers["【白话提要】"][:40])
```

## 6. 质量承诺（数据侧）

- `manifest.json` 确定性生成（无时间戳、路径排序），可重复构建
- `tests/test_manifest_contract.py`：模拟消费端读取，校验结构完整、路径可达、三层齐全
- `tests/recall_regression.py`：检索语义回归（消费端可对齐语义）
- 提交前强制 `validate_library.py` 0 错误 + manifest 交叉核对

## 7. 变更通知

- 契约破坏性变更：本仓库发 Release 说明（`release/*` → `main` tag），并在 `docs/` 标注迁移指引
- RAG 仓库建议订阅本仓库 release，用 CI 比对 `schema_version` 触发重建
