# Your Claude OS — Start Here

This folder is a complete starter kit for your "brain + war room" setup:
an Obsidian vault Claude can read, plus your first two Claude Code skills.
You do 4 manual steps. Everything else is automated by `setup.sh`.

---

## What you're building (plain English)

- **The brain** = a folder of markdown notes (your vault). Obsidian is just a
  nice app for viewing and editing that folder. The "graph" is created by
  linking notes to each other with `[[double brackets]]`.
- **The skills** = saved instructions for Claude Code. Typing `/brain` or
  `/plan-today` in Claude Code runs them. They read your vault, so the more
  notes you write, the smarter they get.
- **No database. No servers.** It's files on your computer, backed up to a
  private GitHub repo.

---

## One-time setup (about 15 minutes)

### Step 1 — Install the two apps (you)
- **Claude Code**: https://claude.ai/code (if you don't already have it)
- **Obsidian** (free): https://obsidian.md

### Step 2 — Run the setup script (automated)
Open a terminal, then:

```bash
cd ~/Downloads/claude-os-starter    # or wherever this folder is
./setup.sh
```

The script:
1. Copies the vault + CLAUDE.md to `~/claude-os`
2. Installs the `brain` and `plan-today` skills into `~/.claude/skills/`
3. Turns `~/claude-os` into a git repo so nothing is ever lost

### Step 3 — Point Obsidian at the vault (you)
Open Obsidian → "Open folder as vault" → choose `~/claude-os/vault`.
Click the graph icon (top-left sidebar) to see your brain. It'll be small.
That's fine — it grows every time you link two notes.

### Step 4 — Test it (you, 1 minute)
```bash
cd ~/claude-os
claude
```
Then type: `/brain what is my offer?`
Claude will search your vault, follow the links, and answer from YOUR notes.

---

## How to use it day-to-day (the actual product)

| When | What you do | What happens |
|------|-------------|--------------|
| Any time an idea hits | Drop a note in `vault/00-Inbox/` (Obsidian or phone) | Captured. Link it later. |
| Every morning | In Claude Code: `/plan-today` | Claude reads your goals, inbox, and metrics and gives you today's plan |
| Any question about your business | `/brain <question>` | Answer sourced from your own notes |
| Friday | Fill in a new note in `vault/50-Metrics/` | Your weekly numbers become part of the brain |

**The one habit that matters:** when you write a note, link it to at least one
other note with `[[note name]]`. Links are what make it a graph instead of a
junk drawer.

---

## Fill these in first (15 minutes of honest writing)

1. `vault/10-TNC/tnc-offer.md` — what you sell, to whom, for how much
2. `vault/20-Content/content-ideas.md` — your next 5 content ideas
3. `vault/50-Metrics/` — copy the template, put in this week's real numbers

A brain with no notes is furniture. These three notes make every skill work.

---

## What comes next (we do these together, in order)

1. **Phase 2** — RE Walkthrough Pro pipeline (Apify + Higgsfield keys, ~20 min)
2. **Phase 3** — Convert Lens-ai into your war-room dashboard (vitals, command
   deck, BHAG bar), hosted on Railway
3. **More command-deck skills** — `/am-report`, `/trend-scan`, `/wk-review`

When you're ready for any phase, just tell Claude and mention this file.
