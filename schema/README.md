# schema/ — 数据规范

本目录存放全库的数据契约，是检索与 RAG 消费的权威定义。

| 文件 | 作用 |
| --- | --- |
| `frontmatter.schema.json` | 每个条目 `.md` 的 YAML Frontmatter 结构（JSON Schema），定义必填字段与类型 |
| `manifest.schema.json` | 机读总清单 `manifest.json` 的结构（引擎与 RAG 管线的输入契约） |
| `controlled_vocabulary.json` | 受控检索词表（type 强枚举；zhengxing/zhifa/jingluo 建议词表） |

## 数据流

```
raw/ (原始文本)
  → scripts/parse_*.py (解析为条目)
    → library/.../*.md (Markdown + YAML Frontmatter，正文三层：原文/古注/白话提要)
      → scripts/build_index.py → 各级 INDEX.md (人读导航)
      → scripts/build_manifest.py → manifest.json (机读总清单)
      → scripts/validate_library.py → 质量门校验
        → scripts/retrieve.py / 外部 RAG 管线 (消费)
```

任何字段的新增或取值扩展，先更新本目录下对应 schema，再入库。
