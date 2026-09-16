# plan-yangsheng.md · 养生康复（v0.3 剩余项）收录计划

> 立项日期：2026-09-16；基线：`origin/dev`（2444 条，validate 0 错 0 警、回归 18/18、契约 0 错）。
> 本文件为养生康复线的范围 / 批次 / 验收权威计划；每完成一批回填「实际进度」。

## 1. 目标与完成标准

- 新增 **养生条目 42 条**，覆盖三个子类：
  - **导引功法 16 条**（`library/yangsheng/daoyin/`，如八段锦、五禽戏、六字诀、易筋经、太极拳、马王堆导引术等）
  - **食疗养生 16 条**（`library/yangsheng/shiliao/`，常见药膳/粥羹/茶饮类，如山药粥、莲子羹、姜枣茶等）
  - **起居情志 10 条**（`library/yangsheng/qiju/`，四时起居、子午觉、情志调摄、劳逸适度等）
- 落点全库 **2486 条**。
- 每批合入前：`build_index / build_manifest / export_vocab` 重建 →
  `validate_library.py`（0 错 0 警）→ `recall_regression.py`（全绿；
  **manifest 总数硬编码断言需随批同步**：2444 → 2460 → 2476 → 2486）→
  `test_manifest_contract.py`（0 错）。
- 每个逻辑单元一个 `feature/<scope>` 分支 → 一个 PR（base=`dev`）；每批 ≤50 条一个
  `feat(library):` commit。严禁直接提交 `main` / `dev`。

## 2. 收录范围与批次切分

| 批次 | 逻辑单元（PR） | 目录 | 目标条数 | type |
| --- | --- | --- | --- | --- |
| S1 | 导引功法 16 | `library/yangsheng/daoyin/` | 16 | chapter |
| S2 | 食疗养生 16 | `library/yangsheng/shiliao/` | 16 | chapter |
| S3 | 起居情志 10 | `library/yangsheng/qiju/` | 10 | chapter |

### 条目清单（初拟，可依素材核验微调并在回填注明）

**导引 16**：八段锦、五禽戏、六字诀、易筋经、太极拳、马王堆导引术、
华佗五禽戏（与五禽戏合并）、导引按跷、叩齿咽津、撮谷道（提肛）、
揉腹法、摩面浴眼、鸣天鼓、踮足法、熊经鸟伸、吐纳调息。
**食疗 16**：山药粥、莲子羹、姜枣茶、百合银耳羹、薏苡仁粥、黑芝麻糊、
枸杞菊花茶、桂圆红枣茶、萝卜汤、冬瓜汤、山楂饮、陈皮茶、绿豆汤、
小米粥、茯苓饼、蜂蜜柠檬饮。
**起居情志 10**：四时起居、子午觉、春捂秋冻、避风寒、情志调摄、
恬淡虚无、劳逸适度、动静结合、睡眠卫生、七情致病与调摄。

## 3. 条目格式硬约束

- 目录：`library/yangsheng/<子类>/<条目拼音>/<条目拼音>_001.md`；目录名 = 条目拼音小写。
- Frontmatter 必填：`id`（与文件名同、全局唯一、`^[a-z0-9_]+$`）、`book`、`chapter`、
  `section_title`、`source_version`、`author`、`dynasty`、`type`、`conditions`（12 字段**全为数组**）、
  `weight`（0–10）、`tags`。
  - `book`：据来源填（如导引功法出处《易筋经》《养生延命录》、食疗起居出处《千金要方·食治》
    《遵生八笺》《素问·上古天真论》等）；跨源归纳的填 `book: "中医养生（古籍要义归纳）"`。
  - `source_version` 注明「据《X》等公有领域古籍原文/要点归纳」；`author` 填出处著者或「佚名」；
    `dynasty` 填朝代；`type: chapter`；`weight: 8`（古籍要义）。
- `conditions` 填法：按条目主题（如八段锦 → zhifa 调和气血/舒展筋骨、keywords 含功法名/出处/
  要领关键词；食疗 → yaoming 主料、siqi/wuwei 按食物属性填；起居 → zhengzhuang/zhifa 按
  调摄主题）；无相关维度置 `[]`。
- 正文必含三层标记：`**【原文】**`（古籍原文——公有领域且经核验，或要点转述并标注）、
  `**【古注】**`（后世注说或留空标记）、`**【白话提要】**`（非空：来源、要领、作用、适用与禁忌）。
- **内容边界（重要）**：养生条目属古籍养生文化转述与要点归纳，**不得写成医疗建议**；
  不承诺疗效、不编造临床结论；涉及疾病治疗内容的表述一律加注「养生保健参考，不替代诊疗」。
- 先例文件：`library/yishi/yijia/` 下任一医家条目（frontmatter 结构）、
  `library/zhongyao/jiebiao/baizhi/baizhi_001.md`（正文三层写法）。

## 4. 素材与内容纪律

- 传统功法、食疗、起居养生内容据公开资料（维基文库等公有领域古籍、权威教材要点）忠实转述
  与要点归纳，标注出处；**不编造出处、不加未经核实的临床结论**；拿不准的原文改为转述。
- 食疗条目给出常见原料与做法要点（文化/食谱性质），并注明「体质有异，食用前自行斟酌」。

## 5. 每批收尾清单（集成步骤，由编排者执行）

1. `python3 scripts/build_index.py`
2. `python3 scripts/build_manifest.py`
3. `python3 scripts/export_vocab.py`
4. `python3 scripts/validate_library.py` → 0 错 0 警
5. 同步 `tests/recall_regression.py` 硬编码总数为新总数（2444 → 2460 → 2476 → 2486），
   新增条目若扩充既有精确集断言，按仓库「旧基线子集 + 抽查新增」哲学更新（不得写死全集）；
   再跑全绿
6. `python3 tests/test_manifest_contract.py` → 0 错
7. 按 ≤50 条/commit 暂存提交；推送分支；`gh pr create --base dev`；验证后合并。
8. 合并后 `git pull --ff-only origin dev` 再开始下一批。

## 6. 实际进度（回填）

- [x] S1 导引功法 16 — PR [#42](https://github.com/Xiaoqin-Mo/TCM-Library/pull/42) 已合并，2444→2460
- [x] S2 食疗养生 16 — PR [#43](https://github.com/Xiaoqin-Mo/TCM-Library/pull/43) 已合并，2460→2476
- [x] S3 起居情志 10 — PR [#44](https://github.com/Xiaoqin-Mo/TCM-Library/pull/44) 已合并，2476→2486（完成）

> 微调说明：计划初稿 S1 列 16 项但「华佗五禽戏」注明并入「五禽戏」，实际为 15 项，
> 故补「站桩功」一条凑足 16。其余条目按计划收录。
> 内容边界已落实：所有条目为古籍养生文化转述，不承诺疗效；涉病表述均加注
> 「养生保健参考，不替代诊疗」，食疗条目另注「体质有异，食用前自行斟酌」。

