# Claude OS — Operating Context

This directory is my personal operating system: a linked markdown vault
(`vault/`) that is my business brain. You (Claude) are the operator.

## Who I am
<!-- FILL IN: name, what TNC is, your niche, your current stage -->
- Owner: Ryan
- Business: TNC — AI content / real-estate media (edit me in one sentence)
- Big goal (BHAG): <!-- e.g. first 10 paying clients / road to 1,000,000 -->

## The vault is the source of truth
- `vault/00-Inbox/` — raw captures, unsorted. Triage these when planning.
- `vault/10-TNC/` — offer, pricing, positioning, ICP. Trust these notes over memory.
- `vault/20-Content/` — content ideas, hooks, scripts, posting log.
- `vault/30-Clients/` — one note per client or lead.
- `vault/40-Playbooks/` — repeatable processes (e.g. the walkthrough pipeline).
- `vault/50-Metrics/` — weekly numbers snapshots, newest = current state.

## How to work in here
1. **Answer from the vault first.** Grep/read notes before generalizing.
2. **Follow `[[wiki-links]]`** up to 2 hops when a note references another.
3. **Frontmatter tags** (`tags:` in YAML) mark topics — use them to search.
4. When you create or update a note, add at least one `[[link]]` to a related
   note and sensible frontmatter (`tags`, `date`).
5. Keep answers practical and short. I am new to this — explain what you did
   and how I use the result, not just what the code does.

## Standing preferences
- Never delete notes; move superseded ones to `vault/00-Inbox/archive-` prefix.
- Weekly metrics note format: see `vault/50-Metrics/` template.
- When asked to plan, end with at most 3 concrete actions for today.
