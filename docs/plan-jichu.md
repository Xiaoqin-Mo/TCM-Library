# plan-jichu.md · 中医基础理论（jichu）收录计划

> 立项日期：2026-09-17；基线：`origin/dev`（2834 条，validate 0 错 0 警、回归 18/18、契约 0 错）。
> 本文件为中医基础理论线的范围 / 批次 / 验收权威计划；每完成一批回填「实际进度」。

## 1. 目标与完成标准

- 新增 **中医基础理论条目约 104 条**（type=`chapter`，`library/jichu/<子类>/`），落点全库 **≥2938 条**。
- 背景：`jichu`（中医基础理论）分类已注册 6 个子类（yinyangwuxing 阴阳五行 / zangxiang 藏象 /
  jingluo 经络 / qixuejinye 气血津液 / bingyinbingji 病因病机 / zhifa 治则治法），**当前 0 条目**，
  本线为该分类奠基。
- 每批合入前：`build_index / build_manifest / export_vocab` 重建 →
  `validate_library.py`（0 错 0 警）→ `recall_regression.py`（全绿；**manifest 总数硬编码断言随批同步**）
  → `test_manifest_contract.py`（0 错）。
- 每个逻辑单元一个 `feature/<scope>` 分支 → 一个 PR（base=`dev`）；每批 ≤25 条一个
  `feat(library):` commit。严禁直接提交 `main` / `dev`。

## 2. 收录范围（分 6 批，共 104 条）

| 批次 | 子类（条数） | 代表条目 |
| --- | --- | --- |
| J1 | yinyangwuxing 阴阳五行（18） | 阴阳学说、阴阳对立制约、阴阳互根互用、阴阳消长、阴阳转化、阴阳平衡失调、阴阳互藏、阴阳交感、五行学说、五行相生、五行相克、五行制化、五行相乘相侮、五行母子相及、五行与五脏配属、五色五味五脏对应、阴阳学说在中医学的应用、五行学说在中医学的应用 |
| J2 | zangxiang 藏象（24） | 藏象学说、五脏、六腑、奇恒之腑、心（主血脉主神明）、肺（主气司呼吸）、脾（主运化）、肝（主疏泄）、肾（主藏精）、心包、胆、胃、小肠、大肠、膀胱、三焦、女子胞、五脏与志液窍华、六腑以通为用、奇恒之腑特点、心肾水火既济、脏腑表里关系、命门学说、三焦气化 |
| J3 | jingluo 经络（12） | 经络学说、十二经脉、奇经八脉、十二经别、十五络脉、十二经筋、十二皮部、经络生理功能、经络临床应用、标本根结、气街四海、经脉循行规律 |
| J4 | qixuejinye 气血津液（15） | 气、元气、宗气、营气、卫气、中气、气机、气化、血、血的生成、血的运行、津液、津液代谢、气血关系、精 |
| J5 | bingyinbingji 病因病机（20） | 六淫、风邪、寒邪、暑邪、湿邪、燥邪、火邪、疠气、七情内伤、饮食失宜、劳逸失度、痰饮、瘀血、结石、正气邪气、正邪相争、阴阳失调、气血失常、津液失常、内生五邪 |
| J6 | zhifa 治则治法（15） | 治未病、治病求本、扶正祛邪、标本缓急、正治反治、调整阴阳、调理气血、三因制宜、因时制宜、因地制宜、因人制宜、八法、以平为期、同病异治异病同治、辨证论治 |

## 3. 条目格式硬约束

- 目录：`library/jichu/<子类拼音>/<条目拼音>_001.md`（如 `library/jichu/zangxiang/xin_001.md`）；
  目录名 = 条目主题小写拼音，同主题多篇顺延 `_002`。
- Frontmatter 必填：`id`（与文件名同、全局唯一）、`book`（如 "《中医基础理论》规划教材（要点归纳）"，
  引经典时 `book` 可标经典名如 "《黄帝内经》"）、`chapter`（如 "藏象"）、`section_title`（主题+核心义）、
  `source_version`（注明依据，如「据《中医基础理论》教材与《素问》原文要点归纳」）、
  `author`（如 "教材编者/经典（要点归纳）"）、`dynasty`（"当代"或经典朝代）、`type: chapter`、
  `conditions`（12 字段**全为数组**）、`weight: 8`、`tags`（含 "中医基础"）。
- `conditions` 填法：按主题维度（如 心 → zangxiang 相关不适用，用 `zhengxing` 置证型概念如
  "心气虚"、"keywords" 含主题词/核心概念；经络条目 `jingluo` 填经络名；气血津液条目 `keywords`
  含 "气"/"血" 等）。无相关维度置 `[]`，不得编造语义。
- 正文三层标记：`**【原文】**` = 概念定义与核心内容（教材/经典要点忠实转述+出处）；
  `**【古注】**` = 经典原文引用（《素问》《灵枢》等公有领域条文）或「本条古注从略」；
  `**【白话提要】**` = 非空：现代通俗释义 + 临床/学习意义（不编造未经核实的临床结论）。
- 先例：`library/yishi/xuepai/`（type=chapter 条目）、`library/zhenduan/bianzheng/` 条目
  （frontmatter 结构、三层标记）。

## 4. 素材与内容纪律

- 依据《中医基础理论》规划教材与《黄帝内经》等公有领域经典做**要点归纳并标注出处**；
  禁止整段转载受版权保护教材文本；经典原文引公有领域通行本。
- 基础理论属学术知识转述，不承诺疗效、不给出个体化诊疗建议；表述用学术口径。
- 无可靠依据的概念不收录。

## 5. 每批收尾清单（集成步骤，由编排者执行）

1. `python3 scripts/build_index.py`
2. `python3 scripts/build_manifest.py`
3. `python3 scripts/export_vocab.py`
4. `python3 scripts/validate_library.py` → 0 错 0 警
5. 同步 `tests/recall_regression.py` 硬编码总数为新总数（2834 → 逐批累加 2852→2876→2888→2903→2923→2938）；
   新增条目若扩充既有精确集断言，按仓库「旧基线子集 + 抽查新增」哲学更新；再跑全绿
6. `python3 tests/test_manifest_contract.py` → 0 错
7. 按 ≤25 条/commit 显式按路径 `git add library/jichu/...`（严禁 `git add -A`）提交；
   推送分支；`gh pr create --base dev`；验证后合并（`gh pr merge --merge`）。
8. 合并后 `git checkout dev; git pull --ff-only origin dev` 再开始下一批。

## 6. 实际进度（回填）

- [ ] J1 阴阳五行（18，PR 待建）
- [ ] J2 藏象（24，PR 待建）
- [ ] J3 经络（12，PR 待建）
- [ ] J4 气血津液（15，PR 待建）
- [ ] J5 病因病机（20，PR 待建）
- [ ] J6 治则治法（15，PR 待建）
