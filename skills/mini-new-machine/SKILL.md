---
name: mini-new-machine
description: Set up a replacement or additional machine for the mini task runner — a new Mac mini to send tasks to, or a new MacBook to send them from. Use when the user says the mini broke, they bought a new mini or MacBook, they want to switch minis, or they ask how to set up mini on another machine.
---

# Set up a new Mac mini or a new MacBook

Everything machine-independent lives in the `mini` repo
(github.com/johnny-2123/mini, cloned to `~/Developer/mini`):
`config/host` names the mini, and `config/repos.txt` lists the repos kept on
it. Ask the user which case this is, then follow that section. Use the same
macOS username (`johnnyavila`) on every machine: repo paths and Claude memory
are keyed by absolute path.

## A. New Mac mini (sending from the existing MacBook)

**The user does these on the new mini** (walk them through; they need its
screen):

1. Sign in to macOS as `johnnyavila` (an admin account).
2. Install Tailscale, sign in with avila.johnny11@gmail.com, and set it to
   open at login.
3. System Settings → General → Sharing → turn on **Remote Login**.
4. System Settings → Energy → turn on **Prevent automatic sleeping when the
   display is off** and **Wake for network access**.
5. System Settings → Users & Groups → **Automatically log in as** Johnny
   Avila. Tasks run in that desktop session.
6. Install Homebrew (https://brew.sh), then `brew install node pnpm`.
7. Install Claude Code and Codex, then run `claude` once and `codex` once in
   a terminal on the mini and sign in to each.

**Then on the MacBook** (you can run these; `!` lines need the user because
they prompt for the mini's password):

1. `tailscale status` to find the new mini's name.
2. `! ssh-copy-id johnnyavila@<name>` (answer `yes`, then the mini's password).
3. `mini setup johnnyavila@<name>` saves the new host to `config/host`
   (committed and pushed), installs gh, the task launcher and agent config.
   If it reports missing tools, have the user install them and re-run it.
4. `mini add-repo --all` recreates every repo in `config/repos.txt` with its
   env files and dependencies.
5. Send a read-only test through each agent and check `mini result`, e.g.
   `mini send --agent claude --repo <repo> "Make no changes; write the summary with the current branch and last commit."`
   (and the same with `--agent codex`).

The first Claude task may stop at a one-time Claude question (display mode,
tips). Tell the user to `mini attach <id>`, answer it once, and `/exit`.

## B. New MacBook (the mini stays)

**The user does these on the new MacBook:**

1. Sign in to macOS as `johnnyavila`.
2. Install Tailscale and sign in with avila.johnny11@gmail.com.
3. Install Homebrew, then `brew install gh node pnpm`, and install Claude Code
   and Codex.
4. `gh auth login` as johnny-2123.

**Then (in Claude or Codex on the new MacBook):**

1. `git clone https://github.com/johnny-2123/mini.git ~/Developer/mini`
2. `~/Developer/mini/bin/mini link` puts `mini` on the PATH and links the
   skills into `~/.claude/skills` and `~/.codex/skills`.
3. If `~/.ssh/id_ed25519` doesn't exist: `ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519`.
   Then `! ssh-copy-id johnnyavila@$(cat ~/Developer/mini/config/host | cut -d@ -f2)`.
4. `mini sync-config --from-mini` copies the Claude and Codex settings,
   skills, plugins, memory and MCP servers from the mini to this MacBook.
   Do this **before** anything that syncs toward the mini (`setup`,
   `add-repo`, `sync-config`), or the new MacBook's blank settings would
   overwrite the mini's.
5. Clone the repos you work in to the same paths listed in
   `config/repos.txt` (`mini send` runs from a local checkout). Env files
   aren't in git. Copy them from the mini with
   `rsync -a johnnyavila@<mini>:<repo>/.env* <repo>/` or from wherever you keep them.
6. `mini ls` and a read-only test `mini send` confirm it works.

## Both

- `mini setup` is safe to re-run at any time.
- A mini's leftover tasks and worktrees are in `~/.mini` on that mini. They
  aren't needed on a new one.
