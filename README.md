# TCM-Library · 中医知识百科全书检索库

> 面向「中医古籍 + 现代中医知识」的结构化检索库：**即查即用・引经据典・白话可读**。
>
> 定位为「**带检索功能的图书馆**」——重索引、轻搜索，元数据驱动而非全文模糊搜索。
> 每条知识以 Markdown + YAML Frontmatter 标引，`conditions` 承载中医结构化检索维度
> （证型 / 治法 / 病症 / 症状 / 方名 / 药名 / 腧穴 / 经络），毫秒级返回
> **原文 / 古注 / 白话提要** 三层内容；`manifest.json` 为机读总清单，
> 可直接供 RAG 管线消费。

> 内容仅供学习研究参考，不构成诊疗建议。用药、针刺等请遵医嘱。

---

## 一、特性

- **双轨收录**：中医古籍（经典原文按篇/卷/条切分）+ 现代中医知识（指南 / 共识 / 研究 / 教材）
- **全面分类**：10 个顶层大类、47 个子类，覆盖基础理论 → 诊断 → 中药 → 方剂 → 针灸 → 临床 → 养生 → 医史 → 经典 → 现代
- **结构化检索**：8 个中医检索维度 + 开放主题词；组内 AND、维度间 OR，命中特异性优先排序
- **RAG 就绪**：确定性生成的 `manifest.json`（含结构化 `conditions`）与三层正文，可直接接入向量检索与混合重排
- **白话提要**：每条附白话转述层，语义检索友好
- **质量门**：`validate_library.py` 校验条目完整性、id 唯一性、分类路径、正文三层；构建确定性可复现
- **零依赖**：解析 / 索引 / 校验 / 检索全部纯 Python 标准库

## 二、目录结构

```
TCM-Library/
├── README.md                 # 本文件
├── CONTRIBUTING.md           # 贡献指南（新增典籍 / 条目规范 / 提交流程）
├── MILESTONES.md             # 里程碑规划
├── AGENTS.md                 # 协作者规范（AI Agent / 人类协作者）
├── BRANCHING.md              # 分支管理规范（main / dev / feature）
├── LICENSE                   # MIT
├── manifest.json             # 机读总清单（build_manifest 确定性生成）
├── schema/                   # 数据契约：frontmatter / manifest / 受控词表
├── docs/                     # 设计文档：分类体系 / 字段规范 / 检索设计
├── library/                  # 条目内容（10 大分类）
│   ├── jichu/                #   中医基础理论
│   ├── zhenduan/             #   中医诊断
│   ├── zhongyao/             #   中药学
│   ├── fangji/               #   方剂学
│   ├── zhenjiu/              #   针灸推拿
│   ├── linchuang/            #   中医临床
│   ├── yangsheng/            #   养生康复
│   ├── yishi/                #   医史医家
│   ├── jingdian/             #   经典医籍
│   └── xiandai/              #   现代中医
├── raw/                      # 原始文本库（统一 UTF-8，不做内容改动）
├── scripts/                  # 构建 / 校验 / 检索脚本（纯标准库）
│   ├── tcm_lib.py            #   共享库（分类常量 / frontmatter 解析）
│   ├── build_index.py        #   生成各级 INDEX.md（人读导航）
│   ├── build_manifest.py     #   生成 manifest.json（机读总清单）
│   ├── validate_library.py   #   交付前质量门
│   ├── retrieve.py           #   结构化检索器（CLI + 可导入）
│   └── export_vocab.py       #   受控词表统计更新
└── tests/                    # 回归测试
    └── recall_regression.py  #   召回回归测试
```

## 三、快速开始

```bash
# 1. 构建人读索引与机读清单
python3 scripts/build_index.py
python3 scripts/build_manifest.py

# 2. 质量门校验（提交前必须通过）
python3 scripts/validate_library.py

# 3. 检索
python3 scripts/retrieve.py --zhengxing 太阳中风        # 按证型
python3 scripts/retrieve.py --yaoming 桂枝              # 按药名
python3 scripts/retrieve.py --zhifa 解表散寒 --detail   # 治法 + 明细
python3 scripts/retrieve.py --keyword 消渴               # 开放主题词
python3 scripts/retrieve.py --show-fields               # 查看全部维度

# 4. 回归测试
python3 tests/recall_regression.py
```

环境要求：Python 3.10+，**零第三方依赖**。

## 四、分类总览

| category | 中文 | 子类 |
| --- | --- | --- |
| `jichu` | 中医基础理论 | 阴阳五行 / 藏象 / 经络 / 气血津液 / 病因病机 / 治则治法 |
| `zhenduan` | 中医诊断 | 四诊 / 辨证 |
| `zhongyao` | 中药学 | 本草著作 / 药性理论 / 单味药 / 炮制 / 配伍与禁忌 |
| `fangji` | 方剂学 | 经方 / 时方 / 成方制剂 / 方解 |
| `zhenjiu` | 针灸推拿 | 经络 / 腧穴 / 刺法灸法 / 推拿 |
| `linchuang` | 中医临床 | 内科 / 外科 / 妇科 / 儿科 / 骨伤 / 五官 / 皮肤 / 温病 |
| `yangsheng` | 养生康复 | 导引气功 / 食疗药膳 / 起居调摄 / 康复 |
| `yishi` | 医史医家 | 医家 / 医案 / 学术流派 / 医史 |
| `jingdian` | 经典医籍 | 内经 / 伤寒 / 金匮 / 温病经典 / 本草经典 / 难经 |
| `xiandai` | 现代中医 | 临床指南 / 专家共识 / 现代研究 / 教材与规范 |

详见 [docs/classification.md](docs/classification.md)。

## 五、条目格式（速览）

```markdown
---
id: "guizhitang_001"      # 全局唯一，与文件名一致
book: "伤寒论"
chapter: "辨太阳病脉证并治"
section_title: "桂枝汤方"
source_version: "通行本"
author: "张仲景"
dynasty: "汉"
type: "fangji"
conditions:
  zhengxing: ["太阳中风"]     # 证型
  zhifa: ["解肌发表"]         # 治法
  bingzheng: ["感冒"]         # 病症
  zhengzhuang: ["发热", "恶寒"] # 症状
  fangming: ["桂枝汤"]        # 方名
  yaoming: ["桂枝", "芍药"]   # 药名
  xuewei: []                 # 腧穴
  jingluo: []                # 经络
  keywords: ["调和营卫"]      # 开放主题词
weight: 8
tags: ["方剂", "经方"]
---

### 桂枝汤方

**【原文】** ……（原文照录）

**【古注】** ……（古注/校释，可省略）

**【白话提要】** ……（白话转述，必填）
```

完整规范见 [docs/frontmatter-spec.md](docs/frontmatter-spec.md) 与 [schema/](schema/)。

## 六、开发与协作

- **分支模型**：`main`（发布）← `dev`（集成）← `feature/*`（开发），详见 [BRANCHING.md](BRANCHING.md)
- **提交规范**：Conventional Commits，小步频繁提交，禁止大 Commit，详见 [CONTRIBUTING.md](CONTRIBUTING.md)
- **里程碑**：见 [MILESTONES.md](MILESTONES.md)
- **AI/人类协作者规范**：见 [AGENTS.md](AGENTS.md)

## 七、License

MIT License。古籍原文为公有领域文本；现代文献条目仅作要点归纳并标注出处。
