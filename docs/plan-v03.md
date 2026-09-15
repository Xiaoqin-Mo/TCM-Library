# plan-v03.md · v0.3「针灸与临床」收录计划

> 立项日期：2026-09-15；基线：`origin/dev`（1630 条，质量门 0 错 0 警、回归 18/18、契约 0 错）。
> 本文件为 v0.3 的范围 / 批次 / 验收权威计划；每完成一批回填「实际进度」。

## 1. 目标与完成标准

- 新增 **≥500 条**，覆盖 `zhenjiu / zhenduan / linchuang / jingdian / yishi` 等 ≥8 个顶层分类。
- 每批合入前：`python3 scripts/validate_library.py`（0 错 0 警）、
  `python3 tests/recall_regression.py`（全绿；**注意其硬编码总数需随每批同步**）、
  `python3 tests/test_manifest_contract.py`（0 错），并重建 `build_index / build_manifest / export_vocab`。
- 每个逻辑单元一个 `feature/<scope>` 分支 → 一个 PR（base=`dev`）；每批 ≤50 条一个 `feat(library):` commit。
- 严禁直接提交 `main` / `dev`；严禁删除或改写 dev 已合入内容。

## 2. 收录范围与批次切分

| 批次 | 逻辑单元（PR） | 目录 | 目标条数 | type |
| --- | --- | --- | --- | --- |
| B1 | 十四经经穴 361 穴 | `library/zhenjiu/shuxue/<穴名拼音>/` | 361（已有足三里种子 1 条，另建 360） | shuxue |
| B2 | 《针灸大成》精选（名篇歌赋 / 要章） | `library/zhenjiu/jingdian/zhenjiudacheng/` | 30–50 | chapter / koujue |
| B3 | 《中医诊断学》要点 | `library/zhenduan/siyang/`、`library/zhenduan/bianzheng/` | 40–60 | zhinan / chapter |
| B4 | 《中医内科学》常见病证 50+ | `library/linchuang/neike/<系>/` | 50+ | zhinan / bingzheng |
| B5 | 温病学（温病条辨条文 + 温热论） | `library/jingdian/wenbing/<book>/` + `library/linchuang/wenbing/` | 40–60 | chapter |
| B6 | 医案 50+ | `library/yishi/yian/<医家>/` | 50+ | yian |

合计新增约 570–620 条，落点全库约 2200+ 条。

## 3. 条目格式硬约束（与既有先例一致）

- 目录：`library/<category>/<subcategory>/<条目目录>/<拼音>_NNN.md`，条目目录名 = 条目拼音小写。
- Frontmatter 必填：`id`（与文件名同、全局唯一、`^[a-z0-9_]+$`）、`book`、`chapter`、`section_title`、
  `source_version`、`author`、`dynasty`、`type`（受控枚举）、`conditions`（12 字段**全为数组**，缺省 `[]`）、
  `weight`（0–10 整数）、`tags`。
- `conditions` 十二字段：`zhengxing / zhifa / bingzheng / zhengzhuang / fangming / yaoming /
  xuewei / jingluo / siqi / wuwei / guijing / keywords`。
- 正文必含三层标记：`**【原文】**`、`**【古注】**`（无古注也保留空标记）、`**【白话提要】**`（非空）。
- 先例文件：`library/zhenjiu/shuxue/zusanli/zusanli_001.md`（shuxue）、
  `library/zhongyao/jiebiao/baizhi/baizhi_001.md`（yaowu）。
- weight 惯例：核心典籍 10；教材 / 国家标准经穴 8；炮制品 / 精选注解 6。
- 版权：古籍用公有领域白文；教材只做要点归纳并标注出处，禁止整段转载。

## 4. 每批收尾清单（集成步骤，由编排者执行）

1. `python3 scripts/build_index.py`
2. `python3 scripts/build_manifest.py`
3. `python3 scripts/export_vocab.py`
4. `python3 scripts/validate_library.py` → 0 错 0 警
5. 同步 `tests/recall_regression.py` 中硬编码总数为新总数，再 `python3 tests/recall_regression.py` 全绿
6. `python3 tests/test_manifest_contract.py` → 0 错
7. 按 ≤50 条/commit 暂存提交；推送分支；`gh pr create --base dev`；绿后合并。

## 5. 实际进度（回填）

- [ ] B1 经穴 361
- [ ] B2 针灸大成精选
- [ ] B3 诊断学要点
- [ ] B4 内科 50+
- [ ] B5 温病学
- [ ] B6 医案 50+

| 批次 | PR | 新增条数 | 状态 |
| --- | --- | --- | --- |
| — | — | — | 计划中 |
