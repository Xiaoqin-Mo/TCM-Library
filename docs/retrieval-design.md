# 检索设计 · Retrieval Design

> 检索是**元数据驱动**（重索引、轻搜索），与参考库 Aether-Cycle 一致：
> 结构化字段精确匹配召回，`keywords` 主题包含召回，不做全文模糊搜索。
> 本设计面向两个消费方：内置 CLI 检索器与后续 RAG 管线。

## 1. 数据契约

`manifest.json`（`scripts/build_manifest.py` 确定性生成）是唯一机读入口：

```json
{
  "schema_version": 2,
  "match_fields": ["zhengxing", "zhifa", "bingzheng", "zhengzhuang",
                   "fangming", "yaoming", "xuewei", "jingluo"],
  "match_rule": "…",
  "roots": { "category": { "subcategory": { "dir", "count" } } },
  "categories": [ { "id", "name_zh", "subcategories": [...] } ],
  "books": [ { "dir", "tier", "tier_name", "category", "subcategory", "count" } ],
  "total": 0,
  "entries": [ { "id", "book", "type", "tier", "category", "subcategory",
                 "path", "weight", "title", "chapter", "conditions" } ]
}
```

- 引擎 / RAG 管线一次性加载 `manifest.json`；正文按需从 `path` 读取。
- 确定性生成（无时间戳、路径排序），CI 中可校验 `manifest.json` 与 `library/` 一致。

## 2. 结构化匹配语义

```
对每条 entry：
  声明字段 = conditions 中非空且查询同字段非空的结构化字段
  若查询为空 → 返回全部（include_general=false 时静默）
  命中条件 = 每个查询非空字段与 entry 同字段有交集（组内 AND）
             AND（查询含 keywords 时 entry.keywords 有包含命中）
  特异性 = 命中的声明字段数（keywords 命中 +1）
排序 = (-特异性, -weight, path)
```

- **组内 AND**：`zhengxing=["风寒束表","太阳病"]` 需同时命中（复合证型查询）。
- **维度间 OR**：`zhifa=["解表散寒"]` 与 `yaoming=["桂枝"]` 任一命中即召回。
- **keywords**：包含式（双向包含），用于主题召回；不参与结构化特异性主排序。

## 3. 排序与权重

| 优先级 | 依据 | 说明 |
| --- | --- | --- |
| 1 | 命中特异性 | 命中声明字段数越多越靠前（精确度优先） |
| 2 | weight | 同精确度时，经典/核心内容靠前（见 frontmatter-spec §4） |
| 3 | path | 稳定排序兜底（确定性） |

## 4. 使用方式

CLI：
```bash
python3 scripts/retrieve.py --zhengxing 风寒束表 --zhifa 解表散寒
python3 scripts/retrieve.py --keyword 消渴 --detail
python3 scripts/retrieve.py --show-fields
```

导入：
```python
from scripts.retrieve import load_manifest, query
m = load_manifest()
r = query(m, {"zhifa": ["解表散寒"], "keywords": ["感冒"]}, limit=10)
```

## 5. RAG 接入指引（后续 Fork）

1. 消费 `manifest.json` 的 `entries`（含结构化 `conditions`）与 `categories`/`books` 层级。
2. 正文读取：`path` 指向的 `.md`，按层标记 `【原文】/【古注】/【白话提要】` 切分：
   - 原文层 → 原文检索索引；
   - 白话提要层 → 语义向量索引（中文语义检索友好）；
   - 结构化字段 → 精确过滤 + 重排特征（Filter / Rerank）。
3. 推荐召回管线：结构化过滤（组内 AND / 维度间 OR）→ 向量语义召回（白话层）→ 混合重排（specificity + weight + 向量分）。
4. 保持 `id` 全局唯一稳定，作为 RAG 文档主键。

## 6. 质量保证

- `scripts/validate_library.py`：frontmatter 必填/枚举/结构、id 唯一、分类路径、三层标记、manifest 交叉核对。
- `tests/recall_regression.py`：召回回归测试（确定性 query 断言）。
- 提交前必须：`validate_library.py` 通过 + 回归测试通过 + `manifest.json` 已重建。
