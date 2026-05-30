# Install

Chinese documentation: [zh-CN/install.md](./zh-CN/install.md)

Install into Codex's skill directory:

```text
$CODEX_HOME/skills
```

If `CODEX_HOME` is unset, use:

```text
~/.codex/skills
```

## Dependency Sets

`skills.json` defines the install sets.

Local skills:

- required: `dev-flow`, `audit-project-scale`, `setup-rust-workstreams`, `open-workstream`,
  `run-architecture-lane`, `coordinate-workstream`, `run-workstream-task`, `review-workstream`,
  `verify-rust-workstream`, `resume-workstream`, `close-workstream`
- recommended: `codex-session-recovery`, `changelog`, `fearless-refactor`
- misc: `humanizer`

Upstream `mattpocock/skills`:

- required: `grill-with-docs`, `tdd`, `diagnose`, `handoff`
- recommended: `zoom-out`, `improve-codebase-architecture`, `prototype`
- optional: `to-prd`, `to-issues`, `triage`, `setup-matt-pocock-skills`, `write-a-skill`,
  `caveman`, `grill-me`

Do not install every upstream skill by default. Keep the working set small.

## Default Install

Installs local required skills and upstream required skills:

```powershell
.\scripts\install-dev-skills.ps1
```

Python equivalent:

```powershell
python .\scripts\install_dev_skills.py
```

## Include Recommended Skills

This installs local recommended skills and upstream recommended skills.

```powershell
.\scripts\install-dev-skills.ps1 -IncludeRecommended
python .\scripts\install_dev_skills.py --include-recommended
```

## Include Optional Upstream Skills

```powershell
.\scripts\install-dev-skills.ps1 -IncludeRecommended -IncludeOptional
python .\scripts\install_dev_skills.py --include-recommended --include-optional
```

## Include Misc Local Skills

Misc skills are useful with Codex but are not part of the default Rust engineering workflow.

```powershell
.\scripts\install-dev-skills.ps1 -IncludeMisc
python .\scripts\install_dev_skills.py --include-misc
```

## Use A Local mattpocock/skills Checkout

The installer automatically uses a sibling `../skills` checkout when present.

You can also pass a path:

```powershell
.\scripts\install-dev-skills.ps1 -MattPocockSkillsPath F:\SourceCodes\Github\skills
python .\scripts\install_dev_skills.py --mattpocock-skills-path F:\SourceCodes\Github\skills
```

If no local checkout is found, the script clones `https://github.com/mattpocock/skills` into a
temporary directory, copies the selected skills, then removes the temporary clone.

## Updating Existing Skills

By default, existing destination skill directories are skipped. Use `-Force` to replace selected
skill folders:

```powershell
.\scripts\install-dev-skills.ps1 -IncludeRecommended -Force
python .\scripts\install_dev_skills.py --include-recommended --force
```

Restart Codex after installing or updating skills.

## Validate Local Skills

Run this before publishing changes to local skills:

```powershell
python .\scripts\validate_skills.py
```
