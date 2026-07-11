---
name: brain
description: Answer any question from my Obsidian vault (the business brain). Searches vault notes, follows [[wiki-links]] up to 2 hops, and answers ONLY from my own notes, citing which notes it used. Use whenever I ask about my business, offer, clients, content, metrics, or say "/brain".
---

# /brain — query the vault

You are querying my personal knowledge vault: a folder of markdown notes
linked with `[[wiki-links]]`, located at `vault/` in this repo (or
`~/claude-os/vault` if not inside the repo).

## Process
1. Take my question and pick 3-6 search terms (include synonyms).
2. `Grep` the vault for those terms (case-insensitive). Also check filenames
   with `Glob`.
3. Read the best-matching notes in full.
4. Collect every `[[link]]` in those notes; read linked notes that look
   relevant (up to 2 hops from the originals — stop there).
5. Answer the question **using only what the notes say**. If the vault
   doesn't contain the answer, say exactly that and suggest which note I
   should create (offer to draft it).

## Output format
- The answer, in plain language.
- A "Sources" line listing the note paths you used.
- If notes contradict each other, flag it — newest note wins, but tell me.

## Rules
- Never invent facts about my business that aren't in a note.
- Don't dump raw note contents unless I ask; synthesize.
- If I ask you to remember something new, write it as a proper note
  (frontmatter with `tags` + `date`, at least one `[[link]]`) in the right
  folder and tell me where you put it.
