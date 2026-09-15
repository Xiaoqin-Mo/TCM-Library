# MILESTONES · 里程碑规划

> 版本节奏：基础骨架已就绪；内容分批收录，每批通过质量门后合入 `dev`，
> 累积到发布节点从 `dev` 合入 `main` 并打 tag。
>
> 状态更新于 2026-09-15：全库 **1630 条**（素问 81 + 灵枢 81 + 伤寒论 660（含序 2）+ 金匮要略 25 + 难经 81 + 药典药材 637 + 药典外品种 64 + 针灸 1）。

## v0.1 — 骨架就绪（已完成）

- [x] 分类体系（10 大类 47 子类）与目录骨架
- [x] Frontmatter / Manifest / 受控词表规范（schema/）
- [x] 构建脚本：INDEX 生成、manifest 生成、质量门校验、检索器
- [x] 种子条目：覆盖 chapter / tiaomu / fangji / yaowu / shuxue 五类 + yian / zhinan 模板
- [x] 文档：README / CONTRIBUTING / MILESTONES / AGENTS / BRANCHING / 设计文档
- [x] 回归测试固化（tests/recall_regression.py，18 项断言全绿）

**完成标准**：质量门 0 错误；`dev` 分支建立；检索器全维度可用。

## v0.2 — 首批经典 + 药材名录（已完成核心目标，1630 条）

**优先级 P0（核心经典，weight 10）**
- [x] 《黄帝内经·素问》81 篇全文（`jingdian/neijing/suwen/`）
- [x] 《黄帝内经·灵枢》81 篇全文（`jingdian/neijing/lingshu/`）
- [x] 《伤寒论》条文全文（`jingdian/shanghan/`，657 条 + 序 2 条，素材为宋本白文标点本）

**药材名录（L0 药典药材，详见 docs/plan-herbal-catalog.md）**
- [x] 基础设施：siqi/wuwei/guijing 字段（schema 2.1）、21 功效子类、词表、模板、测试
- [x] 药典目录清点 + 名单入库（官方 2025 版一部品名目次，637 条）
- [x] 药典药材完整条目（全部功效类；26 味炮制品/加工品单独建条，weight=6，标注与生品差异）

**优先级 P1（本草 / 方剂）**
- [ ] 《神农本草经》药物条目（`jingdian/bencao/shennong/` + `zhongyao/` 关联）— 待启动
- [x] 《金匮要略》25 篇（`jingdian/jingui/`）
- [x] 《难经》81 难（`jingdian/nanjing/`）
- [ ] 经方条目（桂枝汤、麻黄汤、小柴胡汤等 30+，`fangji/jingfang/`）— 部分（桂枝汤 1 条），待扩充

**优先级 P2（教材体系）**
- [ ] 《中医基础理论》要点条目（`jichu/`）— 待启动
- [x] 《中药学》（清华社）药典外品种 64 条（`zhongyao/`，对应 L1 教材差集首期）
- [ ] 《方剂学》常用方剂 100+（`fangji/`）— 待启动

**完成标准（v0.2）**：质量门 0 错误；检索回归通过；条目总量 1630。

## v0.3 — 针灸与临床（目标：≥500 条）

- [ ] 十四经经穴 361 穴（`zhenjiu/shuxue/`）
- [ ] 《针灸大成》精选（`zhenjiu/`）
- [ ] 《中医诊断学》要点条目（`zhenduan/`）
- [ ] 《中医内科学》常见病证 50+（`linchuang/neike/`）
- [ ] 温病学：温病条辨、温热论（`jingdian/wenbing/` + `linchuang/wenbing/`）
- [ ] 医案 50+（`yishi/yian/`）

**完成标准**：≥500 条；覆盖 ≥8 个顶层分类；检索压力测试（万条级毫秒返回）。

## v1.0 — 检索库发布（目标：≥1000 条）

> 条目总量已达成（1630），其余发布项进行中。

- [ ] 现代中医：指南 / 共识 / 教材规范条目（`xiandai/`）
- [ ] 养生康复：导引、食疗、起居条目（`yangsheng/`）
- [ ] 医史医家：医家 30+、流派 10+（`yishi/`）
- [ ] 白话提要覆盖全库（新增条目已全覆盖，存量抽查中）
- [ ] CLI 检索器完整（分页 / 多条件 / 排序展示）
- [ ] 发布流程：`release/*` 分支 → `main` tag v1.0.0

**完成标准**：≥1000 条；质量门与回归全绿；`manifest.json` 与库一致。

## v1.x — RAG 增强（后续 Fork 接入）

- [ ] 提供 RAG 接入参考（见 docs/retrieval-design.md §5）
- [ ] 白话提要层向量索引示例
- [ ] 结构化字段作为 Filter / Rerank 特征
- [ ] 按需提供多语言 / 拼音检索

> 里程碑为方向性规划，实际优先级随社区需求调整；每个里程碑完成时更新本文件勾选状态。
