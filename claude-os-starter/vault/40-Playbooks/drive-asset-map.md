---
tags: [assets, drive, luts, resolve, inventory]
date: 2026-07-11
---

# Asset map — what already exists in Google Drive

Inventory of the editing assets Ryan built before the Claude OS era.
Nothing here needs rebuilding — it needs wiring in. Used by
[[drone-hybrid-tour]], [[longform-estate-film]], and /tnc-video-factory.

## The Resolve automation suite (the crown jewel)
Numbered Python scripts driving DaVinci Resolve, in Drive folder
`Project_Template` (scripts subfolder):
- `02_apply_grade_to_all.py` / `02b_apply_grade_via_drx.py` — ripple a
  calibrated grade (DRX stills) across shot families
- `04_render_multi_format.py` — one-click ProRes master + H.264 web + social
- `05_detect_beats.py` → beats.json / `06_place_beat_markers.py` — music-beat
  markers on the Resolve timeline for cut timing
Pairs with the DaVinci MCP: Claude drives Resolve, scripts do the heavy lifts.

## Workflow docs
- `Longform_Video_Workflow.md` — full 3–8 min estate-film pipeline: story
  structure table, grade families (aerial smooth / FPV dynamic / lifestyle
  interior / detail b-roll), audio LUFS targets, QC passes, 8-hour time
  budget. Mirrored into this vault as [[longform-estate-film]].

## Libraries
- `LUT/` folder — large .cube conversion library (Blackmagic, ARRI, HLG,
  Rec709 families) + `lut-notes/`
- `Project_Template/03_VIDEO/` — the per-project folder skeleton
- `Topaz Video Projects/` — Topaz Video AI upscale/stabilize projects
- `Tnc Marketing Stablaized video/` — stabilized TNC marketing footage
- Raw DJI D-log footage folders (`DJI_*_D.MP4`)

## Known gaps (fill before first hero delivery)
1. **`10_MUSIC/longform_estate/` is empty** — flagged "top priority gap" in
   the workflow doc. Fix: Artlist/Epidemic downloads or ElevenLabs
   compose_music into that folder.
2. **No DJI D-Log M → Rec709 LUT in the library** — the .cube pack is camera
   conversions, not DJI. Download DJI's official LUT (free, dji.com) into
   `LUT/` and `~/work/luts/` on the rig.

## Getting assets onto the rig
On the rig, `rclone` syncs Drive → disk (one-time `rclone config` for the
Google Drive remote, then):
```bash
rclone copy gdrive:LUT ~/work/luts --include "*.cube"
rclone copy gdrive:Project_Template ~/work/project-template
```
Raw footage stays in Drive/SSD; pull per-project, not wholesale.
