---
name: cenuai-kinetic
description: Edit a (usually Malay/BM) talking-head product video — e.g. ustaz promoting wangian cenuai / Pusat Rawatan Al-Fateh — into "kinetic subtitle" style like the Submagic reference: the subtitle itself is the motion graphic (mixed-size, mixed-font words popping in as spoken, big League Gothic hero word typed letter-by-letter and arched BEHIND the person's head), with small clean Inter captions (spoken word yellow) in between. 1080x1920 25fps via HyperFrames. Use when the user says "style kinetic", "macam submagic", "cenuai kinetic", or sends a cenuai video link and asks for this look.
---

# Cenuai kinetic (house style #2)

Approved concept from the ustaz wangian cenuai video (`ustaz/`). Reply in Bahasa Melayu, casual.
For the older testimonial style (small karaoke + separate big overlays) use `testimoni-video` instead.

## Look
- **Big phrases** (the hook / key words, ~60–70% of the talk): the caption becomes a stacked
  block placed so its lower part sits **behind the head** (layer order: base → kinetic text →
  person cutout → small captions → pill).
  - `hero`: League Gothic caps, yellow `#FFE600`, 4px dark stroke + hard drop shadow, typed
    letter-by-letter while the word is spoken, `arch: 1` for the warped/curved look.
  - `serif`: Playfair Display italic (small lead-in words: "sifat", "orang akan", "pastikan").
  - `sans`: Inter 800 lowercase. `block`: League Gothic caps without typing.
  - Ink colour by background: `theme: light` (light wall) → charcoal `#141414`; `theme: dark`
    (curtain / dark room) → white.
  - Every word pops in exactly at its Whisper timestamp; block shakes on landing, slow push-in,
    blurs up and out. A small trailing line that the head would fully cover gets `dx` (±300 px).
- **Small captions** for the rest: Inter 800 50px, white with dark glow, centred at y 1250,
  the spoken word turns yellow. Give the video rhythm: big → small → big.
- Lowercase everything except hero caps and words fixed verbatim in `fix` (e.g. "insyaAllah").
- Brand spelling: **Al-Fateh** (not Al-Fatih), **wangian cenuai**. Surah: Al-Fatihah.
- Yellow pill (e.g. "wangian cenuai · al-fateh") for the first ~5 s, last phrase held to the end.

## Pipeline
Scratch files in the session scratchpad; never commit media (`*.mp4/*.MOV/*.webm` are gitignored).
1. **Download** — Drive link must be *Anyone with the link → Viewer*;
   `curl -sSL -o src.mp4 "https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t"`, check `file` says ISO Media.
2. **Look** — contact-sheet the clip (`ffmpeg -vf fps=1/4,scale=270:-1,tile=5x2`), find shot changes
   (`select='gt(scene,0.25)'`), and **check the tail for a CapCut outro** (black frames + logo): find
   the first black frame with a gray 1x1 probe and trim before it.
3. **Base** — `ffmpeg -t <end> -i src -r 25 -vf tpad=stop_mode=clone:stop_duration=2 -af "loudnorm=I=-14:TP=-1.5:LRA=11,apad=pad_dur=2" -c:v libx264 -crf 16 -g 25 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -t <dur> <proj>/hf/assets/base.mp4`
   (GOP 25 required). If the footage is raw, cut it first with `scripts/edit.py` like `testimoni-video`.
4. **Transcribe** — `pip install faster-whisper`; `python3 -I scripts/transcribe.py OUT.json base.mp4`,
   save as `assets/base_transcript.json` keyed `"base.mp4"`. Re-run unclear snippets with beam 10,
   `ms` + `id`, and an `initial_prompt` of product words (load audio via numpy, the installed PyAV breaks
   faster-whisper's decoder).
5. **Cutout** — `npx hyperframes@0.9.33 telemetry disable` once, then
   `npx hyperframes@0.9.33 remove-background assets/base.mp4 -o assets/c1.webm --quality best`
   (~2 fps CPU; whole video). Held-frame tail: cut out a short tail clip separately (`c2`).
6. **Spec** — write `<proj>/kinetic_spec.json` (format in the `scripts/kinetic.py` docstring; example
   `ustaz/kinetic_spec.json`): `fix`, `breaks`, `pill`, `cutouts` ([start, duration]), and `phrases`
   with `top` (head is ~y 750–1000 in these framings: put the block so the hero line's bottom
   reaches the head), `theme`, `lines` (word-index ranges + style + size).
7. **Build** — `python3 -I scripts/kinetic.py <proj>/kinetic_spec.json <proj>/hf`
   (project files: copy `hyperframes.json/package.json/meta.json` from `ustaz/hf`).
8. **Check** — `export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium`; `npx hyperframes@0.9.33 lint`;
   `snapshot --at <each phrase end − 0.2> --no-end -o DIR`, look at every frame: hero readable,
   key word not >50% hidden, nothing off-frame. Fix `top`/`size`/`dx` and rebuild.
9. **Render** — `npx hyperframes@0.9.33 render --fps 25 --format mp4 -o renders/X.mp4`, delivery copy
   `ffmpeg -i renders/X.mp4 -c:v libx264 -crf 20 -preset slow -c:a copy output/X.mp4`.
10. **Verify** — transcribe the render, `python3 -I scripts/verify.py FINAL.json hf/assets/caption_groups.json REPORT.md`.
11. Commit spec/compositions/scripts (no media), push, send the video with `SendUserFile`.

## What the user needs to send
Drive link (public viewer) · raw or already edited · product/brand spelling · CTA for the end
(beg kuning / WhatsApp number) · optional must-be-big words. Everything else is picked from the transcript.
