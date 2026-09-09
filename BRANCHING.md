# BRANCHING · 分支管理规范

> 遵循优质开源项目（Git Flow 风格）分支模型。**目标：`main` 永远可发布，开发全在 `dev`。**

## 1. 分支模型

```
main ────────────●───────────●──────────────►  发布分支（只接受 Release/Hotfix 合并，打 tag）
  \            /             /
   └─ dev ────●────●────●───┘               集成开发分支（所有功能合入点）
             /    /    /
        feature/*  feature/*  feature/*     功能分支（从 dev 切出，PR 回 dev）
```

| 分支 | 角色 | 谁可写 | 合并来源 | 说明 |
| --- | --- | --- | --- | --- |
| `main` | 发布分支 | 维护者 | `release/*`、`hotfix/*` | 永远可发布；每次合并打 annotated tag（`v0.2.0` 等） |
| `dev` | 集成分支 | 维护者 | `feature/*` | 长期存在；CI 保持绿色；**禁止直接提交** |
| `feature/*` | 功能分支 | 贡献者 | — | 从最新 `dev` 切出，一个主题一个分支 |
| `release/*` | 发布冻结分支 | 维护者 | `dev` | 可选；只做版本号、文档、修 bug，合并回 `main` 与 `dev` |
| `hotfix/*` | 紧急修复 | 维护者 | `main` | 从 `main` 切出，修复后合并回 `main`（patch）与 `dev` |

## 2. 日常开发流程（普通贡献者）

```bash
# 1. 同步并切功能分支
git checkout dev
git pull origin dev
git checkout -b feature/<scope>      # 如 feature/add-suwen-81-chapters

# 2. 小步提交（见 AGENTS.md §1）
git add <paths>
git commit -m "feat(library): add 素问 篇1-20"
git push -u origin feature/<scope>

# 3. 开 PR：feature/<scope> → dev
gh pr create --base dev --head feature/<scope> --title "feat: ..." --body "来源 / 条目数 / 质量门输出"
```

- 分支命名：`feature/<scope>`、`hotfix/<scope>`、`docs/<topic>`、`test/<topic>`、`chore/<topic>`；ASCII 小写 + 连字符
- 一个分支只做一个主题；主题完成即合入 `dev`，不要长期悬挂
- 合入 `dev` 前先 rebase / merge 最新 `dev` 解决冲突

## 3. 发布流程（维护者）

```bash
# 从 dev 冻结
git checkout -b release/v1.0.0 dev
# 修版本号、更新文档、跑全部质量门
git commit -m "chore(release): prepare v1.0.0"
# 合入 main 并打 tag
git checkout main && git merge --no-ff release/v1.0.0
git tag -a v1.0.0 -m "TCM-Library v1.0.0"
git push origin main --tags
# 合回 dev
git checkout dev && git merge --no-ff release/v1.0.0
```

## 4. 紧急修复（维护者）

```bash
git checkout -b hotfix/fix-xxx main
# 修复 + 测试
git commit -m "fix: ..."
git checkout main && git merge --no-ff hotfix/fix-xxx
git tag -a v0.2.1 -m "hotfix v0.2.1"
git checkout dev && git merge --no-ff hotfix/fix-xxx
```

## 5. 硬性规则

1. **禁止**直接 commit / push 到 `main` 与 `dev`
2. **禁止**大 Commit / 大 PR：一个 PR 一个逻辑单元，PR 体量过大须拆分
3. `main` 每次合并必打 tag；`dev` 保持可构建、可测试
4. 提交默认 SSH 签名（本仓库已配置）；保持签名启用
5. 分支合并用 `--no-ff` 保留合并记录

## 6. 当前状态

- 基础初始化已提交至 `main`（v0.1 骨架）
- 后续开发一律在 `dev` 上进行：`git checkout dev` 后开始
