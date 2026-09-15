# Plan · v0.2 P1 收尾：经方 30+ 与《神农本草经》药物条目

> 状态：进行中。本文件记录范围、批次划分、验收标准与实际进度回填。
> 基线：`origin/dev` = 2215 条，质量门全绿（validate 0 错 0 警 / recall_regression 18/18 / manifest 契约 0 错）。

## 1. 范围

### 1.1 经方条目（`library/fangji/jingfang/`，type=fangming）

在已有 `guizhitang_001` 基础上补齐 31 首（合计 32 首）。每首一个目录 `<pinyin-slug>/<pinyin-slug>_001.md`，`conditions.fangming` 必填，`yaoming` 列组成药，`book` 标注出处（《伤寒论》/《金匮要略》），`chapter` 标具体篇名。

清单（slug 即目录与文件名前缀）：

| # | 方名 | slug | 出处 |
| --- | --- | --- | --- |
| 1 | 麻黄汤 | mahuangtang | 伤寒论·太阳病 |
| 2 | 桂枝加葛根汤 | guizhijiagegengtang | 伤寒论·太阳病 |
| 3 | 葛根汤 | gegentang | 伤寒论·太阳病 |
| 4 | 大青龙汤 | daqinglongtang | 伤寒论·太阳病 |
| 5 | 小青龙汤 | xiaoqinglongtang | 伤寒论·太阳病 |
| 6 | 五苓散 | wulingsan | 伤寒论·太阳病 |
| 7 | 白虎汤 | baihutang | 伤寒论·阳明病 |
| 8 | 大承气汤 | dachengqitang | 伤寒论·阳明病 |
| 9 | 小承气汤 | xiaochengqitang | 伤寒论·阳明病 |
| 10 | 调胃承气汤 | tiaoweichengqitang | 伤寒论·阳明病 |
| 11 | 桃核承气汤 | taohechengqitang | 伤寒论·太阳病 |
| 12 | 小柴胡汤 | xiaochaihutang | 伤寒论·少阳病 |
| 13 | 大柴胡汤 | dachaihutang | 伤寒论·少阳病 |
| 14 | 四逆汤 | sinatang | 伤寒论·少阴病 |
| 15 | 真武汤 | zhenwutang | 伤寒论·少阴病 |
| 16 | 理中丸 | lizhongwan | 伤寒论·太阴病 / 金匮 |
| 17 | 吴茱萸汤 | wuzhuyutang | 伤寒论·厥阴病 |
| 18 | 半夏泻心汤 | banxiaxiexintang | 伤寒论·太阳病 |
| 19 | 大陷胸汤 | daxianxiongtang | 伤寒论·太阳病 |
| 20 | 小建中汤 | xiaojianzhongtang | 伤寒论·太阳病 |
| 21 | 炙甘草汤 | zhigancaotang | 伤寒论·太阳病 |
| 22 | 黄连阿胶汤 | huanglianejiaotang | 伤寒论·少阴病 |
| 23 | 乌梅丸 | wumeiwan | 伤寒论·厥阴病 |
| 24 | 麻黄附子细辛汤 | mahuangfuzixixintang | 伤寒论·少阴病 |
| 25 | 当归四逆汤 | danguisinitang | 伤寒论·厥阴病 |
| 26 | 白头翁汤 | baitouwengtang | 伤寒论·厥阴病 |
| 27 | 猪苓汤 | zhulingtang | 伤寒论·阳明病 |
| 28 | 茵陈蒿汤 | yinchenhaotang | 伤寒论·阳明病 |
| 29 | 栀子豉汤 | zhizichitang | 伤寒论·太阳病 |
| 30 | 苓桂术甘汤 | lingguizhugantang | 伤寒论·太阳病 |
| 31 | 甘草泻心汤 | gancaoxiexintang | 伤寒论·太阳病 |
| 32 | 旋覆代赭汤 | xuanfudaizhetang | 伤寒论·太阳病 |

### 1.2 《神农本草经》药物条目（`library/jingdian/bencao/shennong/`，type=yaowu）

新建 `library/jingdian/bencao/shennong/`（`jingdian/bencao` 为既存子类「本草经典」，无需改 CATEGORIES）。
`book="神农本草经"`，`conditions.yaoming` 必填，`siqi/wuwei/guijing` 按本经与通行药性填。
每味药一个文件 `<pinyin-slug>_001.md`（不按三品分子目录，以 `chapter` 字段标「上经/中经/下经」）。
目标 150 味：上经 50 + 中经 50 + 下经 50。

**与 `library/zhongyao/` 的关系**：本草经条目在 `jingdian/bencao/shennong/`，`book="神农本草经"`；药典条目 `book="中国药典（2025年版）一部"`，两条线不可混淆。

## 2. 批次与 PR 划分

| PR | 分支 | 内容 | commit 粒度 |
| --- | --- | --- | --- |
| PR-A | feature/docs-v02-p1-plan | 本计划文档 | 1 个 docs commit |
| PR-B | feature/v02-p1-jingfang | 经方 31 首（+ 已有桂枝汤） | 按方类小步：解表 / 泻下 / 和解 / 温里 / 寒热错杂 分批 commit |
| PR-C | feature/v02-p1-shennong-upper | 上经 50 味 | ≤50 条/commit |
| PR-D | feature/v02-p1-shennong-middle | 中经 50 味 | ≤50 条/commit |
| PR-E | feature/v02-p1-shennong-lower | 下经 50 味 | ≤50 条/commit |

所有 feature 分支从最新 `origin/dev` 切出，PR 回 `dev`；禁止直接提交 `main`/`dev`。

## 3. 每批验收（质量门，0 错 0 警）

```
python3 scripts/build_index.py
python3 scripts/build_manifest.py
python3 scripts/export_vocab.py
python3 scripts/validate_library.py        # 0 错误 0 警告
python3 tests/recall_regression.py         # 18/18（manifest 总数随之增长）
python3 tests/test_manifest_contract.py
```

## 4. 内容纪律

- 忠实转述与要点归纳，不编造出处、不加未经核实的临床结论。
- 经方组成/主治/方解取《伤寒论》《金匮要略》通行知识；原文条用通行宋本白文。
- 神农本草经原文取顾观光/孙星衍辑本通行文；古注可引公有领域注或从略（保留空标记）。
- 内容只做忠实转述与要点归纳。

## 5. 实际进度回填

- [ ] PR-A 计划文档
- [ ] PR-B 经方 31 首
- [ ] PR-C 上经 50 味
- [ ] PR-D 中经 50 味
- [ ] PR-E 下经 50 味
