# CONTRIBUTING · 贡献指南

感谢参与 TCM-Library。本库的协作原则：**小步提交、小步 PR、严禁大 Commit**。
本文档回答「如何新增典籍、如何写条目、如何提交」。

## 1. 工作流程（MANDATORY）

1. 从最新 `dev` 切功能分支：`git checkout dev && git pull && git checkout -b feature/<scope>`
2. 小步提交（见 §4），频繁推送：`git push -u origin feature/<scope>`
3. 完成一个逻辑单元即开 PR 合入 `dev`（PR 描述写明：内容来源、条目数、质量门结果）
4. 严禁把多个不相关内容塞进一个 commit 或一个 PR

## 2. 新增一部典籍（古籍）

1. 获取公有领域原文（通行本 / 公开电子化文本），放入 `raw/<book>.txt`（统一 UTF-8，只清洗不改内容），**同一 commit 只含 raw 文件**：`feat(raw): add <book> source text`
2. 编写解析脚本 `scripts/parse_<book>.py`（纯标准库），将原文切为条目：
   - 经典按篇/卷/条切分 → `library/jingdian/<subcategory>/<book>/`
   - 方剂/药物/腧穴类知识 → 对应学科子类目录
3. 生成条目 `.md`（格式见 §3），**与 INDEX 一起提交**：`feat(library): add <book> (N entries)`
4. 重建产物：`python3 scripts/build_index.py && python3 scripts/build_manifest.py`，提交 `build: regenerate index and manifest`
5. 运行质量门与回归：`python3 scripts/validate_library.py && python3 tests/recall_regression.py`，全部通过后开 PR

## 3. 条目规范（硬性要求）

- Frontmatter 必填字段：`id / book / chapter / section_title / source_version / author / dynasty / type / conditions / weight / tags`（结构见 `schema/frontmatter.schema.json`）
- `conditions` 九个字段全填（不适用填 `[]`）：`zhengxing / zhifa / bingzheng / zhengzhuang / fangming / yaoming / xuewei / jingluo / keywords`
- 正文三层：【原文】必填；【古注】有则填、无则省略该层；【白话提要】必填且非空
- `id` 与文件名一致，全局唯一，仅小写字母/数字/下划线
- 结构化字段尽量取受控词表（`schema/controlled_vocabulary.json`），新词先跑 `python3 scripts/export_vocab.py` 同步
- 白话提要自己撰写，不得照搬原文；现代文献条目只做要点归纳并注明出处，不整段转载受版权保护内容

## 4. 提交规范（MANDATORY）

- **一个 commit = 一个逻辑单元**。建议粒度：
  - `feat(raw): add <book> source text` — 仅 raw 文件
  - `feat(scripts): add parser for <book>` — 仅解析脚本
  - `feat(library): add <book> (N entries)` — 条目 + 该书 INDEX
  - `feat(baihua): fill <book> batch <n>` — 白话批量回填（一次只一本书）
  - `fix(scripts):` / `refactor:` / `test:` / `docs:` / `build:` 各自独立
- **严禁**：`git add -A` 一次提交全部；数百文件一个 commit；把内容 + 脚本 + 文档混在一个 commit
- 按路径显式暂存：`git add <paths>`，提交前 `git status` + `git diff --cached --stat` 检查
- 提交信息用 Conventional Commits（英文动词 + scope + 主题），可加正文说明
- 每个提交保持**有效状态**：相关脚本可跑、质量门通过

## 5. 质量门与测试

```bash
python3 scripts/build_index.py       # 重建人读索引
python3 scripts/build_manifest.py    # 重建机读清单
python3 scripts/validate_library.py  # 质量门：必须 0 错误
python3 tests/recall_regression.py   # 召回回归：必须全绿
```

任何入库内容必须通过以上全部步骤；PR 描述须附质量门输出。

## 6. 内容版权与安全

- 古籍：仅收录公有领域文本（著作者逝世超过 50 年或通行整理本允许公开），保留版本标注
- 现代文献：只做要点归纳 + 注明出处，不整段转载
- 涉及用药、针刺等内容一律注明「仅供参考，遵医嘱」；本库不提供诊疗建议
