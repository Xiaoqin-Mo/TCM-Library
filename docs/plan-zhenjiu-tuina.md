# plan-zhenjiu-tuina.md · 针灸刺法灸法 + 推拿线收录计划

> 立项日期：2026-09-24；基线：`origin/dev`（3101 条，validate 0 错 0 警、回归 18/18、契约 0 错）。
> 本文件为针灸线（cijiu 刺法灸法扩充、tuina 推拿新建）的范围 / 批次 / 验收权威计划；
> 每完成一批回填「实际进度」。养生康复线另见 `docs/plan-yangsheng.md`。

## 1. 目标与完成标准

- **cijiu 刺法灸法扩充**：现有 24 条仅为《针灸大成》歌赋（type=`koujue`），本线补
  **刺法灸法学规划教材要点**约 30 条（`library/zhenjiu/cijiu/`）。
- **tuina 推拿新建**：子类当前为空（目录不存在），新建**推拿学规划教材要点**约 30 条
  （`library/zhenjiu/tuina/`，type=`zhinan`）。
- 落点全库 **≥3161 条**（两项合计约 60 条，实数回填）。
- 每批合入前（构建 PR 执行，内容 PR 以 `validate_library.py --skip-manifest` 0 错为准）：
  `build_index / build_manifest / export_vocab` 重建 → `validate_library.py`（0 错 0 警）→
  `recall_regression.py`（全绿；**manifest 总数硬编码断言随批同步**）→ `test_manifest_contract.py`（0 错）。
- 审核门：内容 PR **只含内容文件**（library/ 新条目），构建产物后置由构建 PR 统一重建；
  所有 PR 不自动合并，等审核人逐条 Review（见 `AGENTS.md`）。

## 2. 收录范围与批次切分

| 批次 | 逻辑单元（PR） | 目录 | 目标条数 | type |
| --- | --- | --- | --- | --- |
| Z1 | 刺法灸法扩充 | `library/zhenjiu/cijiu/<条目拼音>/` | ~30 | zhinan |
| Z2 | 推拿新建 | `library/zhenjiu/tuina/<条目拼音>/` | ~30 | zhinan |

### 条目清单（初拟，依素材核验微调并在回填注明；执行前逐条 `retrieve.py --keyword` 查重）

**Z1 刺法灸法（教材要点，~30）**：毫针刺法总论（持针/进针/角度深度）、进针手法（指切/夹持/舒张/提捏）、
行针手法（提插/捻转）、得气与候气、捻转补泻、提插补泻、疾徐补泻、开阖补泻、迎随补泻、呼吸补泻、
平补平泻、针刺禁忌（部位/体质/孕妇）、晕针与滞针处理、电针、三棱针刺络放血、皮肤针（梅花针）、
皮内针（埋针）、火针、温针灸、艾炷灸（直接灸）、艾条灸（悬起/实按）、隔物灸（隔姜蒜盐）、
温灸器灸、拔罐法（闪罐/留罐/走罐/刺络拔罐）、刮痧法、耳针、头针、穴位注射（水针）、穴位埋线、
保健灸与灸法禁忌。

**Z2 推拿（教材要点，~30）**：推拿学概述（适应证/禁忌/介质）、一指禅推法、㨰法、揉法（指/掌/鱼际）、
摩法、擦法、推法、拿法、按法、点法、拨法、捏法、搓法、抖法、拍法击法、摇法、扳法、拔伸法、
踩跷法、小儿推拿概述（特点/常用介质）、推三关、退六腑、清天河水、揉板门、运内八卦、捏脊、
摩腹、小儿头面特定穴（攒竹/坎宫/天柱骨）、颈肩腰腿痛推拿、内科推拿（头痛/失眠）、保健推拿（头面/全身）、
推拿意外与禁忌处理。

> 条目数与内容以《刺法灸法学》《推拿学》规划教材（全国中医药行业高等教育）要点归纳为准；
> 针灸大成已有 24 首歌赋不重复收录。

## 3. 条目格式硬约束

- 目录：`library/zhenjiu/cijiu/<条目拼音>/<条目拼音>_001.md` 与
  `library/zhenjiu/tuina/<条目拼音>/<条目拼音>_001.md`；目录名 = 条目拼音小写；
  id 与文件名一致、全局唯一（`^[a-z0-9_]+$`）。
- Frontmatter 必填：`id`、`book`、`chapter`、`section_title`、`source_version`、`author`、
  `dynasty`、`type`、`conditions`（12 字段**全为数组**）、`weight`、`tags`。
  - `book`：教材条目填 `book: "刺法灸法学"` / `"推拿学"`（规划教材要点归纳）；
    `source_version` 注明「据全国中医药行业高等教育规划教材要点归纳」；`author` 填
    "教材编写组（要点归纳）"；`dynasty: "现代"`；`type: zhinan`；`weight: 8`。
  - 歌赋类如新收古诀（如《金针赋》已收录则不重复）用 `type: koujue`，weight 10。
- `conditions` 填法：`zhifa` 手法/治法术语；`bingzheng` 适应证（如颈肩腰腿痛、小儿泄泻）；
  `zhengzhuang` 主症要点；`xuewei` 涉及腧穴（选穴条目填，如头针、耳针、小儿推拿特定穴）；
  `jingluo` 经络归属；`keywords` 含技法名、适用病证、教材关键词；无相关维度置 `[]`。
- 正文三层标记：`**【原文】**` = 技法定义/操作要点（要点归纳）；`**【古注】**` = 可留空标记
  （现代教材无古注）或一句源流；`**【白话提要】**` = 非空：操作要领、适用与禁忌、
  **注明「专业操作，请由专业人员实施；本条目为知识参考，不构成操作指导」**。

## 4. 素材与内容纪律

- 内容据规划教材要点忠实归纳；不编造出处、不添加未经核实的临床结论。
- 所有刺法灸法/推拿条目属**知识参考**，含手法操作者一律加注专业操作警示；
  小儿推拿条目单独注明「请在专业人员指导下操作」。
- 每条先 `python3 scripts/retrieve.py --keyword <词>` 查重，与已有 shuxue/cijiu 歌赋不重复。

## 5. 每批收尾清单

1. 内容 PR：只提交 `library/` 新条目；`validate_library.py --skip-manifest` 0 错；开 PR（base=dev，待审核）
2. 审核合并后，构建 PR：`build_index / build_manifest / export_vocab` 重建 → 全量 `validate_library.py`
   0 错 0 警 → 同步 `tests/recall_regression.py` 总数断言 → 回归全绿 → `test_manifest_contract.py` 0 错 →
   `build: regenerate` PR（待审核）
3. 合并后 `git pull --ff-only origin dev` 再开始下一批。

## 6. 实际进度（回填）

- [ ] Z1 刺法灸法扩充（~30）
- [ ] Z2 推拿新建（~30）
