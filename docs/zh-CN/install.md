# 安装

English: [../install.md](../install.md)

安装到 Codex 的 skill 目录：

```text
$CODEX_HOME/skills
```

如果没有设置 `CODEX_HOME`，默认使用：

```text
~/.codex/skills
```

## 依赖集合

`skills.json` 定义安装集合。

本地 skills：

- required：`dev-flow`、`audit-project-scale`、`setup-rust-workstreams`、`open-workstream`、
  `run-architecture-lane`、`coordinate-workstream`、`run-workstream-task`、`review-workstream`、
  `verify-rust-workstream`、`resume-workstream`、`close-workstream`
- recommended：`codex-session-recovery`、`changelog`、`fearless-refactor`
- misc：`humanizer`

上游 `mattpocock/skills`：

- required：`grill-with-docs`、`tdd`、`diagnose`、`handoff`
- recommended：`zoom-out`、`improve-codebase-architecture`、`prototype`
- optional：`to-prd`、`to-issues`、`triage`、`setup-matt-pocock-skills`、
  `write-a-skill`、`caveman`、`grill-me`

默认不要安装所有上游 skill。保持工作集小，模型选择更稳定。

## 默认安装

安装本地 required skills 和上游 required skills：

```powershell
.\scripts\install-dev-skills.ps1
```

Python 等价命令：

```powershell
python .\scripts\install_dev_skills.py
```

## 安装推荐 Skills

这会同时安装本地推荐 skills 和上游推荐 skills。

```powershell
.\scripts\install-dev-skills.ps1 -IncludeRecommended
python .\scripts\install_dev_skills.py --include-recommended
```

## 安装可选上游 Skills

```powershell
.\scripts\install-dev-skills.ps1 -IncludeRecommended -IncludeOptional
python .\scripts\install_dev_skills.py --include-recommended --include-optional
```

## 安装 Misc 本地 Skills

Misc skills 对 Codex 有帮助，但不属于默认 Rust 工程工作流。

```powershell
.\scripts\install-dev-skills.ps1 -IncludeMisc
python .\scripts\install_dev_skills.py --include-misc
```

## 使用本地 mattpocock/skills

安装脚本会自动使用同级 `../skills` checkout。

也可以显式传路径：

```powershell
.\scripts\install-dev-skills.ps1 -MattPocockSkillsPath F:\SourceCodes\Github\skills
python .\scripts\install_dev_skills.py --mattpocock-skills-path F:\SourceCodes\Github\skills
```

如果没有本地 checkout，脚本会临时 clone `https://github.com/mattpocock/skills`，复制选中的 skills 后删除临时目录。

## 更新已有 Skills

默认跳过已有目录。使用 `-Force` / `--force` 替换选中的 skill：

```powershell
.\scripts\install-dev-skills.ps1 -IncludeRecommended -Force
python .\scripts\install_dev_skills.py --include-recommended --force
```

安装或更新后重启 Codex。

## 验证本地 Skills

发布本地 skill 变更前运行：

```powershell
python .\scripts\validate_skills.py
```
