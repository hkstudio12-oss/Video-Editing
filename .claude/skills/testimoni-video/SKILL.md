---
name: testimoni-video
description: Edit raw phone footage of customer testimonials (Malay/BM) into a 1080x1920 25fps social video — Whisper transcription, remove "aa"/pauses/repeated sentences, lowercase centred karaoke subtitles (spoken word turns yellow), big HyperFrames keyword text BEHIND the person (background-removed cutout), WhatsApp booking CTA on the last scene, then re-transcribe the render to verify the subtitles. Use when the user gives a Google Drive folder of footage and asks for this style of edit ("transcribe footage", "buang pause", "subtitle kuning", "overlay belakang orang", "konsep sama macam video testimoni").
---

# Testimoni video (house style)

Locked style, approved by the user on the first two videos (`hf/` = testimoni urut, `polo/hf/` = Abg Polo).
Reply to the user in Bahasa Melayu, casual.

## Locked style
- Output **1080x1920, 25fps**, H.264 + AAC, loudnorm -14 LUFS. Last frame held **3 s** for the CTA.
- Subtitles: **lowercase, centred** (`top: 1010px`), Montserrat 900 **56px**, 7px black stroke, 2–3 words per group, **the word being spoken turns yellow `#FFE600`**, others white.
- Overlays: **big League Gothic uppercase text BEHIND the person** — base video → overlay text → cutout `.webm` of the person → captions → title. Colours: white / yellow `#FFE600` / WhatsApp green `#25D366`. Each one lands exactly on its spoken keyword. Put text on the side away from the head; shrink rather than let a key word be >50% covered.
- Last scene always: **WHATSAPP / BOOKING / SLOT** behind the person until the end.
- Small yellow pill "testimoni …" for the first ~5 s (below the subtitles if overlays use the top).
- Workflow: give the user a **preview first (snapshots + `hyperframes preview`), render only when they say "ok render"**.

## Pipeline
Scripts live in `scripts/`. Scratch files go in the session scratchpad; never commit `.MOV/.mp4/.webm`.

1. **Download** — find the folder with Google Drive `search_files` (`parentId = '<id>'`, paginate). The MCP download caps at 10 MB, so ask the user to set the folder to *Anyone with the link → Viewer*, then
   `curl -sSL -o NAME.MOV "https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t"` (parallel). Check `file` says ISO Media, not HTML.
2. **Transcribe** — `python3 -I scripts/transcribe.py OUT.json clips...` (faster-whisper large-v3, `ms`, word timestamps; decodes via ffmpeg because the installed PyAV breaks faster-whisper's loader). Install once: `pip install faster-whisper`. Contact-sheet the clips (PIL) to see who/what is in each; drop mic tests and unrelated files (ask if unsure).
3. **Pick the story** — write `<project>/segments.json`: `[clip, start, end, "talk"|"action"]`. Order: hook/problem → treatment (keep the crack sound; find it with an RMS scan) → reaction → result → recommend → promo/CTA. Leave out fillers, test takes and repeated sentences (keep the clearest/last take).
4. **Cut** — `python3 -I scripts/edit.py SRC WORK <project>/hf/assets/base.mp4 <project>/segments.json` (silencedetect −38 dB; talk gaps >0.28 s cut to 0.09 s padding; frame-snapped, sync-safe). Then re-transcribe `base.mp4` → `assets/base_transcript.json` and **check the cut**: truncated last words → extend the segment end; unclear phrases → re-run the snippet (`ms` and `id`, beam 10) or swap for a clearer take.
5. **Hold the end**: `ffmpeg … -vf tpad=stop_mode=clone:stop_duration=3.0 -af apad=pad_dur=3.0 -g 25` (GOP 25 is required or HyperFrames freezes on seek).
6. **Cutouts** — for each overlay window, extract that range and run `npx hyperframes@0.9.33 remove-background cut.mp4 -o assets/cN.webm --quality best` (~2 fps on CPU). Skip a cutout (text in front instead) when the matte is bad — e.g. a person lying down against a curtain.
7. **Compose** — copy `scripts/build_polo.py` (the template), set `DURATION`, `FIX` (word-index → corrected text, `""` drops it), `BREAKS`, `CUTOUTS`, `OVERLAYS` (id, lines, start, end, align, top), title text. Run it on `<project>/hf`. Start the project with `npx hyperframes@0.9.33 init <dir> --example blank --resolution portrait --skip-skills --non-interactive` or copy `hyperframes.json/package.json/meta.json` from `hf/`.
8. **Preview** — `export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium`; `npx hyperframes@0.9.33 lint`; `snapshot --at t1,t2,… --no-end -o DIR` at every overlay; look at every frame, fix covered/overlapping text; build one contact sheet; `preview --port 3002 --no-open` + `report_preview_port`. Send the sheet and stop.
9. **Render** (only after approval) — `npx hyperframes@0.9.33 render --fps 25 --format mp4 -o renders/X.mp4`, then delivery copy `-crf 20 -preset slow` into `output/`.
10. **Verify** — `transcribe.py` the delivered file, `python3 -I scripts/verify.py FINAL.json hf/assets/caption_groups.json REPORT.md`. Where the render transcript and the cut transcript agree against your `FIX`, follow the majority and re-render. Report accuracy %, every remaining difference, highlight drift >0.25 s.
11. Commit scripts/compositions/reports (not media) and push; send the video + report with `SendUserFile`.

## Gotchas
- **iPhone footage is HDR (HLG / BT.2020).** If `base.mp4` is HDR, HyperFrames auto-promotes the render to HDR and the output breaks: old caption groups never hide (they stack into gibberish) and text turns grey. Check `ffprobe -show_entries stream=color_transfer` — if it says `arib-std-b67`/`smpte2084`, tone-map `base.mp4` to SDR before rendering:
  `-vf "zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" -color_primaries bt709 -color_trc bt709 -colorspace bt709 -g 25`.
  The render log must say "No HDR sources detected, rendering SDR". Always check frames from the **render itself**, not just snapshots (snapshots do not show this bug).
- Kinetic style (user's reference): `scripts/build_kinetic.py HF_DIR CONFIG.py` with a per-project config (`servis/kinetic_config.py`, `gasgas/kinetic_config.py`). Set `LIGHT_BG = True` for white walls (dark shadows instead of white glow). Close-up selfies: `CUTOUTS = {}` (text in front), the head would hide text behind it.
- Whisper hallucinates repeated lines / "Terima kasih kerana menonton!" over silence or screams — drop them.
- Whisper stretches a word across the preceding pause; captions clamp each word to ≤0.7 s.
- Check timings with `timeline`/snapshots, not assumptions; overlay text that is >50% hidden by the head must be moved or resized.
- Don't run the HyperFrames telemetry beacon; don't send user data to outside services.
