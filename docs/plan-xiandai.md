# plan-xiandai.md · 现代中医（v0.3 剩余项）收录计划

> 立项日期：2026-09-16；基线：`origin/dev`（2486 条，validate 0 错 0 警、回归 18/18、契约 0 错）。
> 本文件为现代中医线的范围 / 批次 / 验收权威计划；每完成一批回填「实际进度」。

## 1. 目标与完成标准

- 新增 **指南 / 共识 / 教材规范要点条目 36 条**（type=`zhinan`，`library/xiandai/zhinan/`），
  落点全库 **2522 条**。
- type 词表已含 `zhinan`（n=111，诊断/内科线已用），无需扩枚举。
- 每批合入前：`build_index / build_manifest / export_vocab` 重建 →
  `validate_library.py`（0 错 0 警）→ `recall_regression.py`（全绿；
  **manifest 总数硬编码断言需随批同步**：2486 → 2504 → 2522）→
  `test_manifest_contract.py`（0 错）。
- 每个逻辑单元一个 `feature/<scope>` 分支 → 一个 PR（base=`dev`）；每批 ≤50 条一个
  `feat(library):` commit。严禁直接提交 `main` / `dev`。

## 2. 收录范围与批次切分

| 批次 | 逻辑单元（PR） | 目录 | 目标条数 | type |
| --- | --- | --- | --- | --- |
| X1 | 常见病证诊疗指南要点 18 | `library/xiandai/zhinan/` | 18 | zhinan |
| X2 | 治未病 / 体质 / 适宜技术规范 18 | `library/xiandai/zhinan/` | 18 | zhinan |

### X1 病证候选（18）：感冒、咳嗽、哮病、喘证、心悸、胸痹心痛、不寐、头痛、眩晕、
### 胃痛、泄泻、便秘、消渴、水肿、淋证、痹证、中风、虚劳（据现行中医临床路径与
### 诊疗指南要点归纳）。
### X2 主题候选（18）：中医体质九分法、治未病四大状态、四季养生指导原则、情志调摄规范、
### 拔罐、刮痧、艾灸、穴位贴敷、耳穴压豆、推拿、药膳食疗规范、运动导引规范、冬病夏治、
### 膏方调理、亚健康状态辨识、慢病中医管理、康复期调护、儿童中医调养（据现行规范/共识要点）。

## 3. 条目格式硬约束

- 目录：`library/xiandai/zhinan/<条目拼音>/<条目拼音>_001.md`；目录名 = 条目拼音小写。
- Frontmatter 必填：`id`（与文件名同、全局唯一、`^[a-z0-9_]+$`）、`book`、`chapter`、
  `section_title`、`source_version`、`author`、`dynasty`、`type: zhinan`、`conditions`（12 字段
  **全为数组**）、`weight`（0–10）、`tags`。
  - `book: "中医临床诊疗指南/专家共识（要点归纳）"`；`chapter: "现代中医"`；
    `section_title` = 病证/主题名+核心要点短题；`source_version` 注明具体依据
    （如「据《中医内科常见病诊疗指南》（中华中医药学会，2008）要点归纳」）；
    `author: "中华中医药学会等（要点归纳）"`；`dynasty: "当代"`；`weight: 8`。
- `conditions` 填法：按病证/主题核心维度（如感冒 → zhengxing 风寒束表·风热犯表 / zhifa 辛温解表·
  辛凉解表 / zhengzhuang 恶寒发热·鼻塞流涕…）；`keywords` 含病证名、指南名、核心治法、
  适宜技术名。无相关维度置 `[]`。
- 正文必含三层标记：`**【原文】**`（指南/共识核心要点忠实转述，注明依据文件）、
  `**【古注】**`（留空标记即可，现代条目无古注）、`**【白话提要】**`（非空：核心诊断/辨证/
  治法/调护要点）。
- 先例文件：`library/linchuang/neike/` 下 zhinan 条目、`library/yishi/yijia/` 下条目（frontmatter 结构）。

## 4. 素材与内容纪律

- 依据现行公开指南 / 共识 / 教材规范（中华中医药学会指南、行业标准、规划教材等）做
  **要点归纳并标注出处**；禁止整段转载受版权保护文本。
- **不承诺疗效、不做个体化医疗建议**；条目标注「要点归纳，供参考；具体诊疗请遵医嘱」。
- 无可靠公开依据的内容不写入；拿不准的表述删去或标注待核。

## 5. 每批收尾清单（集成步骤，由编排者执行）

1. `python3 scripts/build_index.py`
2. `python3 scripts/build_manifest.py`
3. `python3 scripts/export_vocab.py`
4. `python3 scripts/validate_library.py` → 0 错 0 警
5. 同步 `tests/recall_regression.py` 硬编码总数为新总数（2486 → 2504 → 2522），
   新增条目若扩充既有精确集断言，按仓库「旧基线子集 + 抽查新增」哲学更新；再跑全绿
6. `python3 tests/test_manifest_contract.py` → 0 错
7. 按 ≤50 条/commit 暂存提交；推送分支；`gh pr create --base dev`；验证后合并。
8. 合并后 `git pull --ff-only origin dev` 再开始下一批。

## 6. 实际进度（回填）

- [ ] X1 常见病证诊疗指南要点 18（PR 待建）
- [ ] X2 治未病/体质/适宜技术规范 18（PR 待建）
