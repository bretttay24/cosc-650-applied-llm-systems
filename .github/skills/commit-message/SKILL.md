---
name: commit-message
description: Drafts a focused Git commit message from staged changes, with an optional issue reference when the user provides one. Use when the user asks to make, write, draft, or propose a commit message.
license: MIT
metadata:
  author: Brett Taylor
  version: "1.1"
---
# Commit Message
1. Inspect `git diff --cached --stat`, `git diff --cached --name-status`, the staged diff, and current branch.
2. If nothing is staged, say so; never stage files or run `git commit` without explicit approval.
3. Write one focused imperative subject with no period that completes "If applied, this commit will ___."
4. Start with `Add`, `Update`, `Fix`, `Remove`, `Document`, or `Rename`; describe the outcome, not the activity.
5. Cover only staged changes and avoid vague subjects such as `Update files`, `Make changes`, or `Fix issue`.
6. Add an issue reference only when the user provides an issue number or explicitly requests an issue-linked commit. Never derive or invent an issue number from the branch name.

```powershell
git commit -m "<Imperative subject>"
```

When an issue reference is requested:

```powershell
git commit -m "<Imperative subject>" -m "Refs #<issue-number>"
```

Keep secrets out; do not use `Fixes` unless the user explicitly requests a closing reference.