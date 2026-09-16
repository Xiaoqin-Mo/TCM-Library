# plan-yishi.md · 医史医家（v0.3 剩余项）收录计划

> 立项日期：2026-09-16；基线：`origin/dev`（2402 条，validate 0 错 0 警、回归 18/18、契约 0 错）。
> 本文件为医史医家线的范围 / 批次 / 验收权威计划；每完成一批回填「实际进度」。

## 1. 目标与完成标准

- 新增 **医家条目 32 条**（type=`yijia`，`library/yishi/yijia/<医家拼音>/`）+
  **流派条目 10 条**（type=`chapter`，`library/yishi/liupai/<流派拼音>/`），合计 **42 条**，
  落点全库 **2444 条**。
- type 词表已含 `yijia`（`schema/controlled_vocabulary.json`，terms 内 n=0 种子定义），无需扩枚举。
- 每批合入前：`build_index / build_manifest / export_vocab` 重建 →
  `validate_library.py`（0 错 0 警）→ `recall_regression.py`（全绿；
  **manifest 总数硬编码断言需随批同步**：2402 → 2418 → 2434 → 2444）→
  `test_manifest_contract.py`（0 错）。
- 每个逻辑单元一个 `feature/<scope>` 分支 → 一个 PR（base=`dev`）；每批 ≤50 条一个
  `feat(library):` commit。严禁直接提交 `main` / `dev`。

## 2. 收录范围与批次切分

| 批次 | 逻辑单元（PR） | 目录 | 目标条数 | type |
| --- | --- | --- | --- | --- |
| B1 | 医家 1–16 | `library/yishi/yijia/` | 16 | yijia |
| B2 | 医家 17–32 | `library/yishi/yijia/` | 16 | yijia |
| B3 | 流派 10 | `library/yishi/liupai/` | 10 | chapter |

### 医家候选清单（32 位，按时代序）
扁鹊、淳于意、张仲景、华佗、王叔和、皇甫谧、葛洪、陶弘景、
巢元方、孙思邈、王焘、钱乙、庞安时、许叔微、刘完素、张从正、
张元素、李杲、王好古、朱震亨、薛己、张介宾、吴有性、喻嘉言、
傅山、陈士铎、叶天士、薛雪、徐大椿、黄元御、陈修园、王清任、
唐宗海、张锡纯、郑寿全、恽铁樵 —— 取前 32 位（扁鹊→薛雪）；
若个别素材核验不足可顺延替换，替换须在回填中注明。

### 流派清单（10 个）
伤寒学派、河间学派、易水学派、攻邪学派、丹溪学派、温补学派、
温病学派、中西汇通学派、经方学派、火神学派。

## 3. 条目格式硬约束

- 目录：`library/yishi/yijia/<医家拼音>/<医家拼音>_001.md`；
  `library/yishi/liupai/<流派拼音>/<流派拼音>_001.md`；目录名 = 条目拼音小写。
- Frontmatter 必填：`id`（与文件名同、全局唯一、`^[a-z0-9_]+$`）、`book`、`chapter`、
  `section_title`、`source_version`、`author`、`dynasty`、`type`、`conditions`（12 字段**全为数组**）、
  `weight`（0–10）、`tags`。
  - 医家条目：`book: "中医各家学说"`；`chapter: "医家"`；`section_title` = 医家名+核心贡献短题；
    `source_version` 注明「据《中医各家学说》及公开医史资料要点归纳，非原文转引」；
    `author` = 医家名；`dynasty` = 朝代；`type: yijia`；`weight: 8`。
  - 流派条目：`book: "中医各家学说"`；`chapter: "流派"`；`section_title` = 流派名+主张短题；
    `author` = 代表人物（如「刘完素等」）；`dynasty` = 主要活跃朝代；`type: chapter`；`weight: 8`。
- `conditions` 填法：按医家学术特色（如李杲 → zhengxing 脾胃气虚 / zhifa 补中益气 / yaoming
  黄芪·人参·白术…）；`keywords` 含医家名、别名、朝代、代表著作、所属流派；流派条目
  keywords 含流派名、代表人物、核心主张、代表著作。无相关维度置 `[]`。
- 正文必含三层标记：`**【原文】**`（医家代表原文——公有领域且经核验，或核心医论要点转述并
  标注；无可靠原文时写要点转述并注明）、`**【古注】**`（后世评述或留空标记）、
  `**【白话提要】**`（非空：生平+师承+学术贡献+代表著作+所属流派+影响）。
- 先例文件：`library/yishi/yian/lidongyuan/lidongyuan_001.md`（frontmatter 结构）；
  `library/zhongyao/jiebiao/baizhi/baizhi_001.md`（正文三层写法）。

## 4. 素材与内容纪律

- 医家生平、师承、学术主张、著作、流派归属：据公开资料（教材、百科、维基文库等公有领域源）
  忠实转述与要点归纳，并在条目标注资料出处；**不编造医家言论、不添加未经核实的临床结论**。
- 原文引用须公有领域（如《伤寒论》序、《脾胃论》名句）且可核验；拿不准的引用改为转述。

## 5. 每批收尾清单（集成步骤，由编排者执行）

1. `python3 scripts/build_index.py`
2. `python3 scripts/build_manifest.py`
3. `python3 scripts/export_vocab.py`
4. `python3 scripts/validate_library.py` → 0 错 0 警
5. 同步 `tests/recall_regression.py` 硬编码总数为新总数（2402 → 2418 → 2434 → 2444），
   新增条目若扩充既有精确集断言（如医家名/流派名 keywords），按仓库
   「旧基线子集 + 抽查新增」哲学更新（不得写死全集）；再跑全绿
6. `python3 tests/test_manifest_contract.py` → 0 错
7. 按 ≤50 条/commit 暂存提交；推送分支；`gh pr create --base dev`；验证后合并。
8. 合并后 `git pull --ff-only origin dev` 再开始下一批。

## 6. 实际进度（回填）

- [ ] B1 医家 1–16（PR 待建）
- [ ] B2 医家 17–32（PR 待建）
- [ ] B3 流派 10（PR 待建）
