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

In Claude Code or Codex, just ask ("send this to the mini"); the
`send-to-mini` and `mini-add-repo` skills in `skills/` call this tool. `mini
setup` links them into `~/.claude/skills` and `~/.codex/skills`.

## How it works

- **Transport**: ssh over Tailscale to `johnnyavila@mac-mini` (`MINI_HOST`).
  Every `send` and `add-repo` first copies this folder to the mini, so both
  copies stay identical.
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

## Mac mini requirements

- Stay logged in to the desktop (tasks run in that session). Turn on automatic
  login if it may reboot.
- Don't let it sleep: System Settings → Energy → turn on "Prevent automatic
  sleeping when the display is off" and "Wake for network access".
- Repos must live outside `~/Desktop`, `~/Documents` and `~/Downloads`. macOS
  blocks background jobs from those folders.

## From a phone

- Claude tasks appear in the Claude app (Code) as "mini: <title>", so you can
  follow and reply there.
- To send a new task, use an ssh app over Tailscale, connect to `mac-mini` and
  run `mini send --agent claude --repo ~/Developer/<repo> "…"`. The same
  commands work on the mini itself.
