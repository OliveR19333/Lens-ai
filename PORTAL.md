# TNC Interactive Proposal Portal

A two-sided proposal system: you build a proposal with toggleable line items
(each with an optional BEFORE/AFTER image), the client opens a private link,
flips options on and off, watches the total update live — and sees exactly
what they lose when they cut something. Their final selection comes back to you.

## Run it

```bash
ADMIN_KEY=pick-a-strong-key npm start
```

- **Admin dashboard:** `http://localhost:3000/admin` (enter your ADMIN_KEY)
- **Client link:** generated per proposal, looks like `/p/ac351204e7c0…`

On Railway, set `ADMIN_KEY` in the service variables. Note: proposals are
stored in `data/proposals.json` on disk — add a Railway volume (or we wire a
DB) before relying on it in production, since a redeploy wipes the filesystem.

## The workflow (with the AI images)

1. Get the client's photos (their listing, yard, project).
2. Ask Claude to generate the AFTER variants via the Higgsfield MCP
   (Nano Banana 2 — unlimited on your plan): "same yard with new turf and
   paver patio", "living room virtually staged", etc.
3. In `/admin`, create the proposal: one line item per service, price, the
   "what they lose" line, and upload the BEFORE (their real photo) and AFTER
   (the AI render) for each item.
4. Copy the client link, send it.
5. Client toggles options — the image flips between with/without, the total
   updates live — and submits. You see their selection + note in `/admin`.

## Design decisions

- **Images are pre-generated, never live.** Clients toggling between two
  hosted images is instant and free; letting visitors trigger AI generation
  would burn credits, be slow, and be abusable.
- **Required items** can't be toggled off (your base package).
- **Client links are unguessable tokens** — no client login needed. Don't
  post the links publicly.
- Everything is plain Express + two HTML pages — no build step, no framework.
