# mini

Send Claude Code or Codex tasks from the MacBook to the Mac mini, and keep the
mini's repos and agent config in step with the MacBook.

```bash
mini send "fix the flaky reports test"     # from inside a repo; same agent, model and effort
mini ls                                    # what's running / done
mini attach <id>                           # watch or steer (Ctrl-A then D to detach)
mini result <id>                           # the agent's closing summary
mini add-repo ~/Developer/some-repo        # put another repo on the mini, env files included
```

In Claude Code or Codex, just ask ("send this to the mini"). The skills in
`skills/` call this tool: `send-to-mini`, `mini-add-repo`, and
`mini-new-machine` for replacing either computer. `mini setup` (or `mini
link`) links them into `~/.claude/skills` and `~/.codex/skills`.

## How it works

- **Transport**: ssh over Tailscale to the host in `config/host`
  (`MINI_HOST` overrides it). Every `send` and `add-repo` first copies this
  folder to the mini, so both copies stay identical.
- **What's on the mini**: `config/repos.txt`. `add-repo` appends to it and
  `setup USER@HOST` rewrites `config/host`; both commit and push, so a fresh
  clone on any machine knows the mini and its repos.
- **Queue**: `send` writes `~/.mini/tasks/<id>/{meta,prompt.md}` on the mini and
  drops `<id>` into `~/.mini/queue`. The LaunchAgent `dev.mini.dispatch` starts
  each queued task in a `screen` session named `mini-<id>`. launchd runs it in
  the mini's desktop login session, because agents started from ssh can't read
  the login keychain Claude signs in with.
- **Each task** fetches origin and fast-forwards the repo to the branch the
  MacBook was on, or runs in a fresh worktree on branch `mini/<id>` when another
  task is using the checkout or it has local changes. It installs dependencies,
  then starts the agent: Claude in auto mode with Remote Control on (it shows up
  in the Claude app), or Codex in yolo mode.
- **Config**: `config/home-paths.txt` lists the files under `~` that `mini
  sync-config` mirrors; Claude memory and user MCP servers are merged in too.
  `config/skip-ignored.txt` lists the gitignored files `add-repo` never copies.

## Starting sessions from claude.ai

Besides `mini send`, the mini can host sessions you start from the Claude app
or claude.ai: on the mini, run `claude rc --spawn=worktree` inside a repo and
leave it running. Each session you spawn gets its own worktree, so several
can work on separate PRs at once.

Claude Code creates those worktrees through `mini _worktree-create`, the
`WorktreeCreate` hook in `~/.claude/settings.json` (which `mini sync-config`
carries to the mini). It puts the worktree in `~/.mini/worktrees/`, copies the
repo's ignored files (env files, local settings) the same way `add-repo` does,
installs dependencies, and prints the path. `mini clean` removes those worktrees
too once they hold no uncommitted work. Sessions in a repo's main checkout
(`--spawn=same-dir`) don't need any of this.

## Mac mini requirements

- Stay logged in to the desktop as `johnnyavila`, because tasks run in that
  session. Turn on automatic login as that user in case it reboots.
- Don't let it sleep: System Settings → Energy → turn on "Prevent automatic
  sleeping when the display is off" and "Wake for network access".
- Repos must live outside `~/Desktop`, `~/Documents` and `~/Downloads`. macOS
  blocks background jobs from those folders.

## Replacing a machine

The `mini-new-machine` skill walks through both cases. Ask Claude or Codex to
"set up a new mini" or "set up mini on this new MacBook". In short:

- **New Mac mini**: on the mini, set up Tailscale, Remote Login, sleep and
  auto-login settings, Homebrew with node and pnpm, and sign in to Claude and
  Codex. Then on the MacBook run
  `ssh-copy-id johnnyavila@<name>`, `mini setup johnnyavila@<name>` and
  `mini add-repo --all`.
- **New MacBook**: install Tailscale, gh, Claude and Codex, then clone this
  repo to `~/Developer/mini`, run `mini link`, and `ssh-copy-id` to the mini.
  Run `mini sync-config --from-mini` before anything else, so the new
  MacBook's blank settings don't overwrite the mini's.

## From a phone

- Claude tasks appear in the Claude app (Code) as "mini: <title>", so you can
  follow and reply there.
- To send a new task, use an ssh app over Tailscale, connect to `mac-mini` and
  run `mini send --agent claude --repo ~/Developer/<repo> "…"`. The same
  commands work on the mini itself.

## Troubleshooting a task that can't reach GitHub

Verified 2026-09-30 from inside a Codex task the runner launched: DNS and
HTTPS to github.com and api.github.com work, `gh` is signed in with push
rights, and the task pushed a branch and opened a PR with no approval prompt.
The runner starts Codex with `--dangerously-bypass-approvals-and-sandbox`, so
the session has no sandbox and no network restriction. `gh` keeps its token in
`~/.config/gh/hosts.yml` (signed in with `--insecure-storage`), so the login
keychain is never needed, and `gh auth setup-git` is the git credential helper.

- **`Could not resolve host` from `git push` or `gh` inside Codex** means that
  session is sandboxed with networking off. Check `env | grep CODEX_SANDBOX`:
  `CODEX_SANDBOX=seatbelt` plus `CODEX_SANDBOX_NETWORK_DISABLED=1` is a
  sandboxed session (a Codex session on the MacBook, not a mini task). Fix how
  that session was launched, not gh or git.
- **A network error from `gh auth status`** is not proof the token is bad; test
  DNS and HTTPS first.
- **A task that exits seconds after starting with no result**: read the error
  in `~/.codex/sessions/<date>/rollout-*.jsonl`. One exited because the model
  was passed as `astra` instead of `gpt-6-astra`.
- **A task that is queued but never starts**: on the mini,
  `launchctl print gui/$(id -u)/dev.mini.dispatch` and `~/.mini/dispatch.log`.
- **Every task lands in `~/.mini/worktrees/<id>`** even when the main checkout
  is idle: a finished task's `screen` session is still alive (the agent's UI
  stays up), so `_run` counts the checkout as in use. `mini stop <old id>`.
