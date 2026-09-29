---
name: mini-task-prompt
description: Turn rough notes into one paste-ready prompt for the Claude Code mobile app, so a Remote Control session on the Mac mini does the work unattended. Use when the user shares notes, a Linear story, or a rough ask and wants a prompt to copy into Claude Code on their phone, "a prompt for the mini", or "write this up for the mini".
---

# Notes → a prompt for the Mac mini

The Mac mini runs `claude rc --spawn=worktree` in a repo. A prompt pasted into
the Claude Code mobile app (or claude.ai/code) starts a fresh session there,
in its own git worktree, with nobody watching. Your job is to turn the user's
notes into the one prompt that session needs.

The user reads nothing but the prompt, so the reply is **one fenced code block
and nothing else**: no preamble, no commentary after it. If a note is too
thin to act on, ask one question first instead of guessing.

## 1. Read the notes

Pull out:

- **The story**: an id like `SAL-3184`, with or without "ref".
- **The goal**: what should be different when the work is done.
- **The places**: `@path` references and named pages, screens or files.
  Write them as plain paths (`ios/SalesablyRecorder`), never with `@`: the
  mobile app does not expand it.
- **Decisions already made** and constraints (default off, don't touch X,
  match the other platform).

## 2. Resolve the Linear story

Every commit message and PR description must link the story with a Linear
magic word (`ref`, `refs`, `part of`, `toward`, ...) and a markdown link, on
its own line:

```
ref [SAL-3184: Guide, option to only guide but not record](https://linear.app/salesably/issue/SAL-3184/guide-option-to-only-guide-but-not-record)
```

- **Linear is connected here**: look the story up. Copy the id, the exact
  title and the URL from it, never from memory, and write the finished line
  into the prompt. Read the description too: fold any requirement it adds
  (a default, a customer's concern, an acceptance note) into the task.
- **Linear is not connected**: put the id in the prompt and tell the session
  to look the story up with its own `linear` tools before its first commit
  and to build the line from what it finds.

Never use closing words (`fixes`, `closes`, `resolves`): they move the story.

## 3. Write the prompt

Fill this skeleton. Keep the user's own wording for the task where it is
clear; add only what the session needs and the notes left implicit.

````
```
Unattended task on the Mac mini. Nobody is watching: don't stop to ask
questions, make the reasonable call and say so in the PR. You are in your own
git worktree of <repo>; follow the repo's CLAUDE.md and AGENTS.md.

## Story
<the finished ref line, or: "SAL-NNNN — look it up with the linear tools
before the first commit and build the ref line from the story's id, exact
title and URL.">

## Task
<goal in one or two sentences>

<details from the notes, plus anything the story's description adds>

Where: <plain paths / screens>

## Rules
- Branch off dev, commit and push, and open a PR to dev in this same
  session. A pushed branch with no PR is lost work.
- Put the ref line above, on its own line, in every commit message and in
  the PR description. Do not use fixes/closes/resolves.
- <constraints from the notes>

## Done means
- <what to verify: the tests the change touches, a build per platform,
  a screen to check>
- Reply with the branch, the PR link, and anything left for me to check.
```
````

Rules of thumb for the body:

- One platform per bullet when the work spans iOS, Android and web, so the
  session can't finish one and forget the other.
- Name the behaviour, not the implementation, unless the notes decide the
  implementation.
- Don't repeat the repo's standing rules (design tokens, test layout);
  CLAUDE.md is in the worktree. Say only what this task adds.

## Example

Notes:

> Ref SAL-3184: Guide, option to only guide but not record
> @ios/SalesablyRecorder @android/SalesablyRecorder
> In the live guided mode it only lets you run it while recording the
> conversation. Also want option to run it and not record the conversation.

Reply (the story's description said the customer is worried about
conversation security and wants the option default off):

````
```
Unattended task on the Mac mini. Nobody is watching: don't stop to ask
questions, make the reasonable call and say so in the PR. You are in your own
git worktree of salesably-app; follow the repo's CLAUDE.md and AGENTS.md.

## Story
ref [SAL-3184: Guide, option to only guide but not record](https://linear.app/salesably/issue/SAL-3184/guide-option-to-only-guide-but-not-record)

## Task
Let a rep run Guide (live coaching) without recording the conversation.

Today the live guided mode only runs while the conversation is being
recorded. Add an option to run Guide and not record. It is off by default
(recording stays the default); the customer asking for this is concerned
about the security of recorded conversations, so when it is on, no audio or
transcript of the call is stored.

Where: ios/SalesablyRecorder, android/SalesablyRecorder, and whatever the
Guide backend under app/api/live-coach needs so a guide-only session saves
no recording.

## Rules
- Branch off dev, commit and push, and open a PR to dev in this same
  session. A pushed branch with no PR is lost work.
- Put the ref line above, on its own line, in every commit message and in
  the PR description. Do not use fixes/closes/resolves.
- Same behaviour and wording on both apps.

## Done means
- iOS builds for the simulator and Android unit tests pass, per the repo's
  own instructions.
- Unit tests for anything touched under lib/guide or app/api/live-coach pass.
- Reply with the branch, the PR link, and anything left for me to check.
```
````
