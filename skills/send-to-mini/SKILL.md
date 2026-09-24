---
name: send-to-mini
description: Send a coding task to the Mac mini so it runs there instead of on this MacBook, in the same agent (Claude or Codex) with the same model and effort. Use when the user says "send this to the mini", "have the mini do X", "run this on the Mac mini", "offload this", or asks to check on, watch or stop a task running on the mini.
---

# Send a task to the Mac mini

`mini` (source: `~/Developer/mini`) hands a task to the Mac mini. The mini
pulls the repo's latest code, installs dependencies, and starts the **same
agent you are** — Claude Code or Codex — with the model and effort you pass,
in its own session. The task runs without anyone there to approve anything:
Claude in auto mode, Codex in yolo mode.

## 1. Write the task as a standalone brief

The agent on the mini sees none of this conversation. Write the prompt so it
stands alone: the goal, the files or pages involved, decisions already made,
constraints the user gave, and what "done" looks like. Carry over anything the
user said about branches, PRs or testing. Don't paste this conversation.

## 2. Send it

Run this from the repo the task is for, or pass `--repo PATH`:

```bash
mini send --agent <claude|codex> --model <your model> [--effort <effort>] [--title "short name"] - <<'TASK'
<the brief>
TASK
```

- `--agent`: `claude` if you are Claude Code, `codex` if you are Codex.
- `--model`: your exact model ID as your system prompt states it (for
  example `claude-opus-5-5[1m]`, or the Codex model name). Leave it out only
  if you don't know it; `mini` then reads the tool's configured default.
- `--effort`: pass it when you know the session's effort level. Otherwise
  leave it out: `mini` reads the effort the tool is configured with
  (`effortLevel` in `~/.claude/settings.json`, `model_reasoning_effort` in
  `~/.codex/config.toml`), which is what `/effort` and `/model` set.
- The mini follows the branch this checkout is on when origin has it,
  otherwise the mini's current branch. Use `--branch` to choose another.
- Codex: the command uses the network (ssh), so run it with escalated
  permissions rather than inside the sandbox.

If it says the repo isn't on the mini yet, offer to run the `mini-add-repo`
skill first.

## 3. Tell the user

Tell the user the task id and these commands:

- `mini ls` — tasks and whether they're running, done or stopped
- `mini attach <id>` — watch or steer it (Ctrl-A then D to detach)
- `mini result <id>` — the summary the agent writes when it finishes
- `mini log <id>` — the pull/install output, if it failed before starting
- `mini stop <id>` — end it

Claude tasks also show up in the Claude app (Code) as "mini: <title>", so the
user can follow and reply from their phone.

When two tasks target the same repo, the second runs in its own git worktree
on a `mini/<id>` branch, so they never overwrite each other. `mini clean`
removes finished worktrees that have no uncommitted work.
