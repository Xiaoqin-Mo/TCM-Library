# plan-zhenduan.md · 诊断学扩充（四诊细化 / 病因辨证 / 六经与温病分证 / 舌脉深化）收录计划

> 立项日期：2026-09-21；基线：`origin/dev`（3049 条，validate 0 错 0 警、回归 18/18、契约 0 错）。
> 本文件为诊断学线的范围 / 批次 / 验收权威计划；每完成一批回填「实际进度」。

## 1. 目标与完成标准

- 新增 **诊断条目约 60 条**（type=`zhinan`，`library/zhenduan/siyang/` 与 `library/zhenduan/bianzheng/`），
  落点全库 **≥3109 条**。
- 背景：`zhenduan` 现有 52 条（siyang 24 + bianzheng 28），已有四诊总论、八纲/脏腑/气血津液/
  六经/卫气营血/三焦辨证框架；本线做**细化与分证拆分**，不重复已有总论。
- 每批合入前：`build_index / build_manifest / export_vocab` 重建 →
  `validate_library.py`（0 错 0 警）→ `recall_regression.py`（全绿；**manifest 总数硬编码断言随批同步**）
  → `test_manifest_contract.py`（0 错）。
- 每个逻辑单元一个 `feature/<scope>` 分支 → 一个 PR（base=`dev`）；每批 ≤25 条一个
  `feat(library):` commit。严禁直接提交 `main` / `dev`。

## 2. 收录范围（分 3 批，共 60 条）

| 批次 | 子类（条数） | 内容 |
| --- | --- | --- |
| D1 | siyang 四诊细化（20） | 望排出物（痰涕唾涎/呕吐物/二便）、小儿指纹、望目、望耳、望鼻、望唇齿龈、望咽喉、听声音总论、听语言声、听呼吸声、听呕吐咳嗽声、嗅气味、问饮食口味、问睡眠、问二便、问经带、问小儿、按肌肤、按手足、按脘腹、按腧穴（精选 20） |
| D2 | bianzheng 辨证细化（25） | 病因辨证总论、风淫/寒淫/暑淫/湿淫/燥淫/火淫（6）、七情内伤、痰饮辨证、瘀血辨证、劳伤辨证；六经分证（太阳经证/阳明经证/少阳经证/太阴证/少阴证/厥阴证 6）；卫气营血分证（卫分证/气分证/营分证/血分证 4）；经络辨证总论 |
| D3 | siyang 舌脉深化（15） | 舌色（淡白舌/红舌/绛舌/紫舌青舌 4）、舌形（胖大舌瘦薄舌/裂纹舌/齿痕舌/芒刺舌 4）、苔质（厚薄/润燥/腐腻/剥落 4）、相兼脉（浮紧脉/沉迟脉/弦数脉 3） |

**去重硬约束**：已有 `shese/shetai/shexing/taise/taizhi/deshen/cunkou/mai_fuchen/mai_ruoruo/mai_xianjin/mai_xushi/
anwen/wenhan/wenhanre/wennv/wenshuimian/wentong/wenyinshi/liuwei/luomai` 等四诊条目、
`liujing/weiqi_yingxue/sanjiao/yinyang/biaoli/hanre/xushi` 等辨证总论条目**不得重复**；
新条目必须为其下**分证/细化**（如「太阳经证」是 `liujing_001` 六经总论的分证条目，不另写总论）。

## 3. 条目格式硬约束

- 目录：`library/zhenduan/siyang/<主题拼音>/<主题拼音>_001.md` 或
  `library/zhenduan/bianzheng/<主题拼音>/<主题拼音>_001.md`。
- Frontmatter 必填：`id`（与文件名同、全局唯一、先查占用冲突顺延 `_002`）、
  `book: "《中医诊断学》规划教材（要点归纳）"`、`chapter`（如 "四诊" / "辨证"）、
  `section_title` = 主题+要点、`source_version`（注明依据教材）、`author`（如 "教材编者（要点归纳）"）、
  `dynasty: "当代"`、`type: zhinan`、`conditions`（12 字段**全为数组**）、`weight: 8`、`tags`
  （含 "中医诊断"）。
- `conditions` 填法：`zhengzhuang` 主症/舌脉表现；`bingzheng` 对应证型；`zhengxing` 证型；
  `zhifa` 治法；`keywords` 含主题名；无相关维度置 `[]`。
- 正文三层标记：`**【原文】**` = 定义+要点（教材要点归纳+出处）；`**【古注】**` = 经典条文（《素问》
  《灵枢》公有领域原文可引）；`**【白话提要】**` = 非空：辨证要点/鉴别要点/临床意义（**不做诊断结论**，
  标注「教材要点归纳，供参考；具体诊疗请遵医嘱」）。

## 4. 素材与内容纪律

- 依据《中医诊断学》规划教材做**要点归纳并标注出处**；经典条文用《素问》《灵枢》公有领域原文。
- **不承诺疗效、不做个体化诊断**；只描述教材所述辨证要点，不引导用户自我诊断。
- 无可靠教材依据的内容不收录。

## 5. 每批收尾清单（集成步骤，由编排者执行）

1. `python3 scripts/build_index.py`
2. `python3 scripts/build_manifest.py`
3. `python3 scripts/export_vocab.py`
4. `python3 scripts/validate_library.py` → 0 错 0 警
5. 同步 `tests/recall_regression.py` 硬编码总数为新总数（3049 → 3069 → 3094 → 3109）；
   新增条目若扩充既有精确集断言，按仓库「旧基线子集 + 抽查新增」哲学更新；再跑全绿
6. `python3 tests/test_manifest_contract.py` → 0 错
7. 按 ≤25 条/commit 显式按路径 `git add library/zhenduan/...`（严禁 `git add -A`）提交；
   推送分支；`gh pr create --base dev`；验证后合并（`gh pr merge --merge`）。
8. 合并后 `git checkout dev; git pull --ff-only origin dev` 再开始下一批。

## 6. 实际进度（回填）

- [x] D1 四诊细化（17 净增，PR #89，3066）
- [x] D2 辨证细化（19 净增，PR #90，3085）
- [x] D3 舌脉深化（16 净增，PR #91，3101）
