# raw/ — 原始文本库

存放未作内容改动的原始文本（统一 UTF-8 编码），是条目生成的**唯一素材来源**。

## 规范

- 命名：`<书拼音>.txt`（如 `shanghanlun.txt`、`bencaogangmu.txt`）。
- 只做**格式清洗**（编码、分段、去页眉页脚），**不改动原文内容**。
- 每部典籍的原始来源、版本、URL 记录在对应解析脚本头部或 `docs/sources.md`。
- 文本较大的典籍可切分为 `raw/<book>/` 多文件（如 `part1.txt`、`part2.txt`）。

## 工作流

```
raw/<book>.txt
  → scripts/parse_<book>.py（解析为条目）
    → library/<category>/<subcategory>/<book>/*.md
      → build_index / build_manifest / validate_library
```

> 注意：文本来源须为公有领域（古籍通行本、公开电子化文本），并保留来源标注。
