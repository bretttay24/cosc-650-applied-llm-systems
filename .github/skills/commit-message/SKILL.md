---
name: commit-message
description: Drafts an issue-linked Git commit message from staged changes. Use when the user asks to make, write, draft, or propose a commit message.
license: MIT
metadata:
  author: Brett Taylor
  version: "1.0"
---
# Commit Message
1. Inspect `git diff --cached --stat`, `git diff --cached --name-status`, the staged diff, and current branch.
2. If nothing is staged, say so; never stage files or run `git commit` without explicit approval.
3. Verify branch `<initials>_<issue-number>` and derive the issue number; ask rather than invent missing values.
4. Write one focused imperative subject with no period that completes "If applied, this commit will ___."
5. Start with `Add`, `Update`, `Fix`, `Remove`, `Document`, or `Rename`; describe the outcome, not the activity.
6. Cover only staged changes and avoid vague subjects such as `Update files`, `Make changes`, or `Fix issue`.

```powershell
git commit -m "<Imperative subject>" -m "Refs #<issue-number>"
```
Keep secrets out; reserve `Fixes` for resolving PRs or explicitly requested final commits.