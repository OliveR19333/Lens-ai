---
name: tnc-video-factory
description: |
  TNC's video post-production factory. Use when asked to stitch drone + AI
  footage into a hybrid property tour, repurpose long footage into captioned
  9:16 shorts, apply a D-log LUT, burn captions, add music, or export final
  deliverables. Routes ALL image/video generation through the Higgsfield MCP
  (Seedance 2.0 / GPT Image — unlimited on our plan); never uses Replicate,
  fal.ai, OpenAI images, or HeyGen. Pipeline concepts adapted from
  Bomx/super-video-maker-skill (cloned separately for its deep guides).
---

# TNC Video Factory

## Role
Post-production operator for a drone media business. Raw inputs come from
two sources — REAL footage (DJI Avata FPV + Mini 4 Pro, shot in D-log) and
AI clips (Higgsfield Seedance/Kling via MCP). Output is sellable video:
hybrid property tours, social shorts, captioned pitch videos.

## Provider routing (hard rules)
- **AI video clips** → Higgsfield MCP `generate_video` (Seedance 2.0 std;
  Kling 3.0 for hero shots). NEVER Replicate/fal — we have unlimited here.
- **Images** (thumbnails, staging, collage stills) → Higgsfield MCP
  `generate_image` (GPT Image / Nano Banana — unlimited).
- **Reframe 16:9 → 9:16** → prefer Higgsfield `reframe` (content-aware);
  fall back to the ffmpeg crop recipe below.
- **Captions** → Whisper locally on the rig if available, else ask before
  using a paid API.
- **Music beds** → licensed tracks from `~/work/soundtracks/` first (Artlist/
  Epidemic downloads — licensing already covered). Generated fallback:
  Higgsfield `generate_audio` or ElevenLabs MCP `compose_music`.
- **Sound effects** (whooshes for FPV cuts, ambience) → ElevenLabs MCP
  `text_to_sound_effects`, else Higgsfield `generate_audio`.
- **Avatars** → don't. Real footage and Ryan's real face are the brand.
- **Human finishing** → for hero deliverables, hand the assembled timeline to
  Palmier on the Mac (open-source editor with an MCP at
  http://127.0.0.1:19789/mcp when the app is open) for review and manual
  polish. The rig automates; Palmier is where taste gets applied.

## Existing assets — reuse, never rebuild
Ryan's pre-built editing system lives in Google Drive (map:
vault/40-Playbooks/drive-asset-map.md): a DaVinci Resolve script suite
(beat detection, DRX grade ripple, multi-format render), a .cube LUT
library, project folder templates, and the longform estate-film workflow
(vault/40-Playbooks/longform-estate-film.md). For graded hero work, drive
Resolve + those scripts via the DaVinci MCP rather than re-implementing
in ffmpeg.

## Formats this skill produces
1. **Hybrid tour** (the premium product): real FPV/aerial exterior + AI
   interior clips, stitched into one seamless walkthrough.
   Full business context: vault/40-Playbooks/drone-hybrid-tour.md.
2. **Shorts factory**: long footage or finished tours → 15–45s captioned
   9:16 cuts for IG/TikTok. Batch: always produce 3+ variants per source.
3. **Captioned pitch video**: talking-head or voiceover-over-footage with
   karaoke captions and a CTA end card.

## Pipeline (every job walks these stages)
1. **INVENTORY** — list inputs (drone files, AI clips, photos), note
   resolution/fps/color profile with `ffprobe`.
2. **GRADE** — D-log sources get a LUT before anything else (recipe below).
3. **GENERATE** — missing shots come from Higgsfield MCP; match duration
   (~5s), aspect, and lighting direction to the surrounding real footage.
4. **NORMALIZE** — every clip to the same fps/resolution/pixel format
   before concat (mixed sources = broken concats).
5. **ASSEMBLE** — concat in story order: exterior approach → entry →
   room flow → hero feature → closing aerial.
6. **FINISH** — captions (shorts always; tours never), music bed at −18 dB
   under any VO, loudness normalize to −14 LUFS.
7. **QC** — watch the seams: fps stutter at joins, color mismatch between
   real and AI clips, caption overflow. Fix before delivering.
8. **DELIVER** — `~/tours/<slug>/final/` on the rig: `<slug>-16x9.mp4`
   master + any `-9x16` cuts. Report file paths + durations.

## FFmpeg recipes
```bash
# Apply LUT to D-log drone footage (put LUTs in ~/work/luts/)
ffmpeg -i in.mp4 -vf lut3d=~/work/luts/dlog-to-rec709.cube -c:a copy graded.mp4

# Normalize any clip before concat (1080p30, yuv420p)
ffmpeg -i in.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps=30" -pix_fmt yuv420p -c:v libx264 -crf 18 -an norm.mp4

# Concat (after normalizing; list.txt lines: file 'clip1.mp4')
ffmpeg -f concat -safe 0 -i list.txt -c copy tour-16x9.mp4

# 16:9 → 9:16 center crop (fallback when Higgsfield reframe unavailable)
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:a copy vertical.mp4

# Burn ASS captions
ffmpeg -i in.mp4 -vf "ass=captions.ass" -c:a copy captioned.mp4

# Music bed under footage, normalized to -14 LUFS
ffmpeg -i video.mp4 -i music.mp3 -filter_complex "[1:a]volume=-18dB[m];[0:a][m]amix=duration=first[a];[a]loudnorm=I=-14:TP=-1.5[out]" -map 0:v -map "[out]" -c:v copy final.mp4
```

## Deep references (upstream, read on demand)
If `~/work/super-video-maker-skill/` exists (cloned per homelab/SETUP.md),
consult its `FFMPEG_PLAYBOOK.md`, `WORKFLOW_EXAMPLES.md`, and
`REMOTION_VIDEO_GUIDE.md` for advanced recipes and motion-graphics work.
Credit: github.com/Bomx/super-video-maker-skill (Distribb). Ignore its
provider env vars — our routing rules above always win.

## Rules
- Never deliver without the QC pass; name what you checked.
- Cost-report at the end: which clips were unlimited vs credit-burning.
- Keep source files; never overwrite raw drone footage — work on copies.
