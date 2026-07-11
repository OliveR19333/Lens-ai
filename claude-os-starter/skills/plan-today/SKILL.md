---
name: plan-today
description: Morning command — read my vault (goals, inbox, latest metrics, client notes) and produce today's battle plan with at most 3 concrete actions. Use when I say "/plan-today", "plan my day", or ask what to work on.
---

# /plan-today — the morning command

Build me a short, honest plan for today from my vault (`vault/` in this repo,
or `~/claude-os/vault`).

## Process
1. Read `vault/10-TNC/` (offer + BHAG) — this defines what matters.
2. Read the newest note in `vault/50-Metrics/` — this is the current state.
3. Scan `vault/00-Inbox/` — anything captured but not processed.
4. Scan `vault/30-Clients/` for open commitments or waiting-on items.
5. Think: what single action today moves the BHAG most? What's leaking
   (unanswered client, stale inbox, metric dropping)?

## Output format (keep the whole thing under ~20 lines)
**Today's focus:** one sentence.

**Top 3 actions** — numbered, each starting with a verb, each doable today.
For each: why it matters in one clause.

**Inbox triage** — list inbox notes that need filing/linking (just names).

**Flag** — one risk or dropped ball, if any. Skip the section if none.

## Rules
- Max 3 actions. If the vault suggests ten, pick the three highest-leverage.
- Ground every action in something you actually read in a note.
- If key notes are empty (no offer, no metrics), make action #1 "fill in
  <note>" and offer to draft it with me right now.
- End by offering to log the plan to `vault/00-Inbox/plan-YYYY-MM-DD.md`.
