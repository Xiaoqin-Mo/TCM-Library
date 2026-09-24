# AGENTS.md — 协作者与 AI Agent 规范

供人类协作者与 AI Agent 在本仓库工作时遵守。本库为结构化中医知识检索库：
每个条目是 Markdown + YAML Frontmatter，检索为**元数据驱动**（`conditions` 结构化字段），
非全文模糊搜索。匹配语义：组内 AND、维度间 OR、`keywords` 包含召回；
结果按命中特异性 → `weight` → `path` 排序（见 `docs/retrieval-design.md`）。

---

## 1. 提交纪律（MANDATORY）

**小步、频繁、单一目的提交**；严禁把无关工作打包进一个 commit 或一次性暂存数百文件。

- **一个 commit = 一个逻辑单元**，推荐粒度：
  - 某书 `raw/*.txt` 原文 → `feat(raw): add <book> source text`
  - 该书解析脚本 → `feat(scripts): add parser for <book>`
  - 该书条目 `*.md` + 子 `INDEX.md` → `feat(library): add <book> (N entries)`
  - 白话批量：一个 JSON 批次 + 仅该批填写的 md → `feat(baihua): fill <book> batch <n>`
  - 脚本修复/重构 → `fix(scripts):` / `refactor:`
  - README/INDEX/docs 改动 → `docs:`
  - 构建产物（manifest.json / INDEX）→ `build: regenerate …`
- 显式按路径暂存（`git add <paths>`），提交前检查 `git status` 与 `git diff --cached --stat`；避免 `git add -A` 处理大混合改动。
- 使用 Conventional Commits，英文动词 + scope：`feat|fix|docs|style|refactor|test|chore|build(scope): subject`。
- 每个提交必须让仓库处于**有效状态**：相关解析器可跑、`validate_library.py` 0 错误、回归测试全绿。

## 2. 分支与 PR（MANDATORY）

三层分支模型（完整策略见 `BRANCHING.md`）：

- `main` — 发布分支：仅接受来自 `dev` 的 Release PR；每次合并打 annotated tag；禁止直接提交
- `dev` — 长期集成分支：所有 `feature/*` 合入此处；CI 保持绿色；禁止直接提交
- `feature/<scope>` — 功能分支：从最新 `dev` 切出，小步提交、频繁推送，PR 回 `dev`
- `hotfix/*` — 从 `main` 切出，修复后合并回 `main`（patch tag）与 `dev`
- `release/*` — 发布冻结分支（可选）：从 `dev` 切出，合并回 `main`（tag）与 `dev`

远程操作：分支创建、PR、release 用 GitHub CLI（`gh`）。禁止直接 commit 到 `main` / `dev`。

### 审核门（Review gate，MANDATORY）

- **PR 创建后不自动合并**（Agent 不得自行执行 `gh pr merge`），一律由审核人逐条 Review 后手动合并；Agent 只负责开 PR、报告并等待。
- **内容线 PR 只含内容**：feature 分支只提交内容文件（如 `library/<分类>/*.md` 新条目）；构建产物——`manifest.json`、各级 `INDEX.md`、`controlled_vocabulary.json`、`tests/recall_regression.py` 的条目数期望——**一律不进内容 PR**。
- 内容 PR 被审核合并后，Agent 另开构建 PR：在最新 dev 上统一重建上述产物并更新回归期望，作为独立机器生成提交（标题标 `build: regenerate`），同样待审核合并。
- **串行开 PR**：一条内容线一个 PR，前一个审核合并后再开下一条；构建产物后置后即便多条 OPEN 也不冲突，但串行可保持 dev 基线新鲜。

## 3. 内容不变量（修改/新增内容时不可破坏）

1. Frontmatter 必填字段齐全；`id` 与文件名一致、全局唯一
2. `conditions` 九个字段全为数组；type 在受控枚举内
3. 正文含【原文】与【白话提要】层（【古注】可省略）；白话提要非空
4. 分类路径与 `docs/classification.md` / `scripts/tcm_lib.py` 的 `CATEGORIES` 一致
5. `manifest.json` 与 `library/` 实际一致（`validate_library.py` 交叉核对）

## 4. 构建命令速查

```bash
python3 scripts/build_index.py       # 人读索引（各级 INDEX.md）
python3 scripts/build_manifest.py    # 机读清单（manifest.json）
python3 scripts/validate_library.py  # 质量门（0 错误才可提交）
python3 scripts/export_vocab.py      # 受控词表统计更新
python3 scripts/retrieve.py --show-fields   # 检索维度速查
python3 tests/recall_regression.py   # 召回回归
```

## 5. 环境与坑

- 要求 Python 3.10+；**零第三方依赖**（纯标准库），不引入 PyYAML 等
- Frontmatter 解析为自研 YAML 子集（`scripts/tcm_lib.py`）：仅支持标量 / 行内数组 / 一层嵌套 dict；新增复杂 YAML 结构须先扩展解析器
- 分类体系改动的**唯一入口**：`docs/classification.md` + `scripts/tcm_lib.py` 的 `CATEGORIES` 常量，两者必须同步修改
- 提交签名：本仓库已配置 SSH 签名（经 1Password）；`git commit` 默认签名，验证密钥在 `.gpg/allowed_signers`
- 不要提交 `__pycache__/`、`.DS_Store` 等（.gitignore 已覆盖）

## 6. 协作礼仪

- 新增条目前先查重（`python3 scripts/retrieve.py --keyword <词>`）
- PR 描述必须附：内容来源、条目数、质量门输出
- 内容只做忠实转述与要点归纳，不编造出处、不添加未经核实的临床结论
