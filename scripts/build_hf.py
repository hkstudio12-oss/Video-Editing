"""Generate the HyperFrames compositions (captions, title, keyword overlays)
from the Whisper transcript of the cut (hf/assets/base_transcript.json).

Usage: build_hf.py HF_DIR
"""
import json, os, sys, html

HF = sys.argv[1]
words = json.load(open(os.path.join(HF, "assets/base_transcript.json")))["base.mp4"]["words"]
DURATION = 75.88  # ffprobe length of assets/base.mp4 (cut + 1.6 s held last frame)

# Whisper mishearings fixed by checking against the source-clip transcripts.
FIX = {1: "roh", 100: "seumur", 108: "sekarang"}
# Hard caption breaks (index of last word in a phrase).
BREAKS = {6, 16, 19, 25, 32, 38, 43, 46, 50, 53, 57, 60, 62, 66, 70, 74, 75, 78, 81, 82, 84,
          86, 88, 91, 94, 101, 107, 110, 113, 116, 119, 124, 129, 131, 136, 141, 142, 145}
MAX_WORDS = 3
MAX_WORD_DUR = 0.7  # whisper stretches a word over the pause before it

W = []
for i, w in enumerate(words):
    t = FIX.get(i, w["w"].strip()).strip(",.?!").lower()
    s, e = w["s"], w["e"]
    s = max(s, e - MAX_WORD_DUR)
    W.append({"i": i, "t": t, "s": round(s, 3), "e": round(e, 3)})

# phrases -> groups of <= MAX_WORDS, balanced
phrases, cur = [], []
for w in W:
    cur.append(w)
    if w["i"] in BREAKS:
        phrases.append(cur); cur = []
if cur:
    phrases.append(cur)
groups = []
for p in phrases:
    n = -(-len(p) // MAX_WORDS)
    size = -(-len(p) // n)
    for k in range(0, len(p), size):
        groups.append(p[k:k + size])

for gi, g in enumerate(groups):
    g_start = max(0.0, g[0]["s"] - 0.05)
    nxt = groups[gi + 1][0]["s"] - 0.05 if gi + 1 < len(groups) else DURATION
    g_end = min(g[-1]["e"] + 0.25, nxt, DURATION - 0.04)
    g_end = max(g_end, g[-1]["e"])
    g[0]["gs"], g[0]["ge"] = round(g_start, 3), round(g_end, 3)

# ---------------- captions composition ----------------
cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    gs, ge = g[0]["gs"], g[0]["ge"]
    spans = []
    for w in g:
        wid = f"cw{w['i']}"
        spans.append(f'<span class="w" id="{wid}">{html.escape(w["t"])}</span>')
        cap_js.append(f'tl.set("#{wid}", {{color: "#FFE600", scale: 1.08}}, {w["s"]:.3f});')
        cap_js.append(f'tl.set("#{wid}", {{color: "#FFFFFF", scale: 1}}, {w["e"]:.3f});')
    cap_html.append(
        f'    <div id="cg{gi}" class="clip grp" data-start="{gs:.3f}" data-duration="{ge - gs:.3f}">'
        f'<div class="line">{" ".join(spans)}</div></div>')
    cap_js.append(f'tl.fromTo("#cg{gi} .line", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.12, ease: "power2.out"}}, {gs:.3f});')

captions = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .grp {{ position: absolute; left: 0; width: 100%; top: 990px; height: 150px; overflow: visible;
           display: flex; align-items: center; justify-content: center; }}
    .line {{ width: 100%; padding: 0 70px; text-align: center; font-family: Montserrat, sans-serif;
            font-weight: 900; font-size: 56px; line-height: 1.05; letter-spacing: -0.01em;
            color: #FFFFFF; -webkit-text-stroke: 7px #000; paint-order: stroke fill;
            text-shadow: 0 4px 12px rgba(0,0,0,.55); text-transform: lowercase; }}
    .w {{ display: inline-block; transform-origin: 50% 60%; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920" data-layout-allow-overflow>
{chr(10).join(cap_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10) + '    '.join(cap_js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""

# ---------------- overlays composition (keyword-locked) ----------------
def ws(i):
    return W[i]["s"]

OVERLAYS = [
    # id, text, start (word), end, style
    ("ov-sakit", "sakit pinggang", ws(18), 10.95, "pill-red"),
    ("ov-krek", "krek!", 25.35, 26.75, "stamp"),
    ("ov-puas", "super puas", ws(83), 48.20, "stamp"),
    ("ov-1010", "10/10", ws(117), 62.95, "score"),
    ("ov-rm50", "bawah rm50", ws(131), 72.95, "price"),
]
ov_html, ov_js = [], []
for oid, text, s, e, style in OVERLAYS:
    s, e = round(s, 3), round(e, 3)
    extra = '<div class="stars">★★★★★</div>' if style == "score" else ""
    ov_html.append(f'    <div id="{oid}" class="clip ov {style}" data-start="{s:.3f}" data-duration="{e - s:.3f}">'
                   f'<div class="card">{html.escape(text)}{extra}</div></div>')
    if style in ("stamp", "score"):
        ov_js.append(f'tl.fromTo("#{oid} .card", {{scale: 2.2, opacity: 0, rotation: -8}}, '
                     f'{{scale: 1, opacity: 1, rotation: -4, duration: 0.22, ease: "back.out(2.2)"}}, {s:.3f});')
    else:
        ov_js.append(f'tl.fromTo("#{oid} .card", {{scale: 0.6, opacity: 0, y: 30}}, '
                     f'{{scale: 1, opacity: 1, y: 0, duration: 0.25, ease: "back.out(1.8)"}}, {s:.3f});')
    ov_js.append(f'tl.to("#{oid} .card", {{opacity: 0, scale: 0.92, duration: 0.15, ease: "power2.in"}}, {e - 0.16:.3f});')

overlays = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .ov {{ position: absolute; left: 0; width: 100%; top: 1170px; height: 160px; overflow: visible;
          display: flex; align-items: center; justify-content: center; }}
    .card {{ font-family: Montserrat, sans-serif; font-weight: 900; text-transform: lowercase;
            text-align: center; white-space: nowrap; }}
    .pill-dark .card, .pill-red .card, .pill-yellow .card {{ font-size: 56px; padding: 18px 40px; border-radius: 999px;
            box-shadow: 0 10px 30px rgba(0,0,0,.35); }}
    .pill-dark .card {{ background: rgba(12,12,16,.86); color: #FFE600; }}
    .pill-red .card {{ background: #E8262B; color: #FFFFFF; }}
    .pill-yellow .card {{ background: #FFE600; color: #111111; }}
    .stamp .card {{ font-size: 130px; color: #FFE600; -webkit-text-stroke: 12px #111; paint-order: stroke fill;
            text-shadow: 0 10px 0 #E8262B, 0 16px 30px rgba(0,0,0,.5); }}
    .score .card {{ font-size: 150px; color: #FFE600; -webkit-text-stroke: 12px #111; paint-order: stroke fill;
            line-height: 1; text-shadow: 0 16px 30px rgba(0,0,0,.5); }}
    .score .stars {{ font-size: 64px; -webkit-text-stroke: 4px #111; letter-spacing: 6px; }}
    .price .card {{ font-size: 72px; background: #E8262B; color: #fff; padding: 16px 44px; border-radius: 22px;
            border: 6px solid #FFE600; box-shadow: 0 12px 30px rgba(0,0,0,.4); }}
  </style>
  <div id="root" data-composition-id="overlays" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-allow-caption-zone>
{chr(10).join(ov_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10) + '    '.join(ov_js)}
    window.__timelines["overlays"] = tl;
  </script>
</template>
"""

# ---------------- title composition ----------------
TITLE_END = 4.4
title = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    #title-wrap {{ position: absolute; left: 0; width: 100%; top: 230px; display: flex; flex-direction: column;
                  align-items: center; gap: 18px; }}
    #title-kicker {{ font-family: Montserrat, sans-serif; font-weight: 800; font-size: 40px; color: #111;
                    background: #FFE600; padding: 10px 28px; border-radius: 999px; text-transform: lowercase; }}
    #title-main {{ font-family: Montserrat, sans-serif; font-weight: 900; font-size: 96px; line-height: 1.02;
                  text-align: center; color: #fff; -webkit-text-stroke: 12px #000; paint-order: stroke fill;
                  text-shadow: 0 10px 28px rgba(0,0,0,.5); text-transform: lowercase; padding: 0 60px; }}
    #title-main .hl {{ color: #FFE600; }}
  </style>
  <div id="root" data-composition-id="title" data-width="1080" data-height="1920" data-layout-allow-overflow>
    <div id="title-wrap" class="clip" data-start="0" data-duration="{TITLE_END}">
      <div id="title-kicker">testimoni pelanggan</div>
      <div id="title-main">sakit <span class="hl">pinggang</span><br/>sebab kerja duduk?</div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#title-kicker", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, 0.05);
    tl.fromTo("#title-main", {{ opacity: 0, scale: 0.85 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(1.7)" }}, 0.1);
    tl.to("#title-kicker, #title-main", {{ opacity: 0, y: -24, duration: 0.25, ease: "power2.in" }}, {TITLE_END - 0.3});
    window.__timelines["title"] = tl;
  </script>
</template>
"""

index = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
      #base {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 1; }}
      #title, #overlays, #captions {{ position: absolute; inset: 0; }}
      #overlays {{ z-index: 2; }}
      #captions {{ z-index: 3; }}
      #title {{ z-index: 4; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DURATION}" data-fps="25"
         data-width="1080" data-height="1920">
      <video id="base" class="clip" src="assets/base.mp4" data-start="0" data-duration="{DURATION}"
             data-track-index="0" data-has-audio="true" playsinline></video>
      <div id="overlays" data-composition-id="overlays" data-composition-src="compositions/overlays.html"
           data-start="0" data-duration="{DURATION}" data-track-index="1" data-track-kind="graphics"
           data-width="1080" data-height="1920"></div>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
           data-start="0" data-duration="{DURATION}" data-track-index="2" data-track-kind="captions"
           data-width="1080" data-height="1920"></div>
      <div id="title" data-composition-id="title" data-composition-src="compositions/title.html"
           data-start="0" data-duration="{TITLE_END}" data-track-index="3" data-track-kind="graphics"
           data-width="1080" data-height="1920"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""

os.makedirs(os.path.join(HF, "compositions"), exist_ok=True)
for name, txt in (("compositions/captions.html", captions), ("compositions/overlays.html", overlays),
                  ("compositions/title.html", title), ("index.html", index)):
    open(os.path.join(HF, name), "w").write(txt)
json.dump([[{"t": w["t"], "s": w["s"], "e": w["e"]} for w in g] for g in groups],
          open(os.path.join(HF, "assets/caption_groups.json"), "w"), ensure_ascii=False, indent=1)
print(len(groups), "caption groups,", len(OVERLAYS), "overlays")
