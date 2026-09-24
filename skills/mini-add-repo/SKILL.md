---
name: mini-add-repo
description: Set up a repo on the Mac mini so tasks can be sent to it — a fresh clone at the same path, plus the env files and local config git ignores, agent config and installed dependencies. Use when the user asks to copy, add, set up or refresh a repo on the mini, or when `mini send` says a repo isn't on the mini yet.
---

# Put a repo on the Mac mini

Run from the MacBook:

```bash
mini add-repo <path to the repo on this MacBook>      # or no path for the current repo
mini add-repo <path> --env-only                       # re-copy env files only; keep the mini's clone
```

What it does:

1. **Recreates the repo** at the same absolute path on the mini, cloned from
   the same `origin` and checked out on the same branch. If a copy already
   exists there, it moves to the mini's Trash first, so nothing is deleted
   outright.
2. **Copies what git ignores but the repo needs**: `.env*`, local settings
   such as `.claude/settings.local.json`, keys and so on. It never copies
   build output or dependencies (`~/Developer/mini/config/skip-ignored.txt`)
   or anything over 50 MB, and it lists every file it copied or skipped.
3. **Syncs agent config**: Claude and Codex settings, skills, plugins, Claude
   memory, user MCP servers and git identity
   (`~/Developer/mini/config/home-paths.txt`), and marks the repo trusted so a
   task never stops at a trust prompt.
4. **Installs dependencies** with the repo's own package manager.

Before you run it:

- A full `add-repo` replaces the mini's copy. If the user may have work on
  the mini they haven't pushed, use `--env-only` or ask first.
- The command uses the network (ssh). In Codex, run it with escalated
  permissions.

Afterwards, tell the user what was copied and anything that was skipped for
size. If the repo needs more than what's listed, such as a machine-wide tool
config under `~`, add the path to `config/home-paths.txt` and run
`mini sync-config`.

Other commands: `mini repos` lists the repos on the mini, and `mini setup`
redoes the one-time setup (safe to re-run).
