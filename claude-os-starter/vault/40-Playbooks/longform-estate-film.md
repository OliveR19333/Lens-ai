---
tags: [playbook, longform, estate-film, resolve, premium]
date: 2026-07-11
---

# Playbook — Longform Estate Film (3–8 min, the flagship)

Vault mirror of Ryan's `Longform_Video_Workflow.md` (full text lives in
Drive — see [[drive-asset-map]]). This is the top-shelf product above
[[drone-hybrid-tour]]: hero estate films that anchor a listing's website.

## Spec
3–8 min · 60–80 BPM music · cuts on major phrase changes only · 4K master ·
landscape primary · Style 1 Luxury Listing grade, 10–12% grain.

## Story structure (lock BEFORE editing)
Establishing (aerials) → Approach → Living spaces → Private spaces →
Outdoor amenities (aspirational peak) → Lifestyle → Close. Durations sum to
the music track length.

## Pipeline
1. Ingest stabilized clips to `03_VIDEO/_RAW_FOOTAGE/`, one folder per
   camera (Mini5 / Avata / GoPro / iPhone)
2. Pick music FIRST (3:30+, cinematic, gradual build) → `05_detect_beats.py`
3. Calibrate one clip per shot family → Resolve still + DRX
4. Rough assembly: cuts on phrase markers (5–10s clips, 15s+ breathe moments)
5. `02b_apply_grade_via_drx.py` per family
6. Polish: continuity is THE tell — match warmth across interiors,
   saturation across aerials
7. Audio: music −18 to −20 LUFS, ambient layer −30 LUFS, final −14 LUFS
8. Three QC watches: color at 1×, rhythm at 2× muted, story at 1× with sound
9. `04_render_multi_format.py`: ProRes 4444 master + H.264 web

## Where Claude plugs in
- Rig / /tnc-video-factory: ingest, normalization, AI b-roll gap-fills,
  shorts cut-downs of the finished film
- DaVinci MCP: drive Resolve + the script suite conversationally
- Palmier: final cut review on the Mac
- Time budget is ~8 hrs manual — target: automate to ~2 hrs of Ryan-time

## Price tier
Sits above hybrid tour: $___ (fill after first sale; anchor high — this is
a Luxury Presence-grade deliverable).
