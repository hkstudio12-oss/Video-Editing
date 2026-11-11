"""Generate the HyperFrames compositions for the Abg Polo testimonial.

Same concept as the first video (build_hf.py): lowercase karaoke captions in
the centre, plus BIG keyword text placed *behind* the person, made by putting a
background-removed cutout of the footage (assets/cN.webm) above the text.

Usage: build_polo.py HF_DIR
"""
import json, os, sys, html

HF = sys.argv[1]
words = json.load(open(os.path.join(HF, "assets/base_transcript.json")))["base.mp4"]["words"]
DURATION = 56.42  # ffprobe of assets/base.mp4 (53.40 s cut + 3.0 s held last frame)

# Whisper mishearings fixed against the source-clip transcripts ("" = drop the token)
# (where two re-transcriptions of the cut agreed against the clip transcript, the majority wins)
FIX = {15: "ada", 19: "ouuu", 20: "waaa!", 22: "", 31: "", 32: "", 34: "", 43: "siut",
       51: "uuuh", 52: "sedap", 53: "weh", 63: "ui", 138: ""}
BREAKS = {4, 9, 13, 18, 19, 20, 25, 28, 36, 40, 42, 47, 50, 52, 55, 60, 62, 63, 65, 72, 76, 82,
          85, 89, 99, 107, 110, 115, 122, 126, 131, 133, 138}
MAX_WORDS, MAX_WORD_DUR = 3, 0.7

# cutouts of the person: id -> (start, duration) in the base timeline
# c1 (0.9-5.0, lying-down hook) is not used: its matte swallowed the curtain, so the hook text sits in front.
CUTOUTS = {"c2": (16.7, 1.0), "c3": (19.2, 1.9), "c4": (25.8, 1.4),
           "c5": (29.0, 1.5), "c6": (35.1, 3.9), "c7": (40.6, 15.82)}

G, W_, Y = "#25D366", "#FFFFFF", "#FFE600"
# id, [(text, colour, px)], start, end, align
OVERLAYS = [  # id, [(text, colour, px)], start, end, align, top(px)
    ("o-sakit", [("sakit", W_, 230), ("belakang", Y, 170)], 1.00, 3.15, "left", 175),
    ("o-4thn", [("4 tahun", Y, 210), ("construction", W_, 120)], 3.20, 4.98, "left", 175),
    ("o-nangis", [("nak", W_, 260), ("nangis", Y, 330)], 16.84, 17.68, "center", 250),
    ("o-bunyi", [("boleh", W_, 260), ("bunyi!", Y, 340)], 19.30, 21.08, "center", 250),
    ("o-power", [("power!", Y, 300)], 25.90, 27.18, "center", 175),
    ("o-champ", [("champion", Y, 300)], 29.14, 30.48, "center", 250),
    ("o-baloi", [("berbaloi", Y, 300)], 35.20, 37.40, "center", 250),
    ("o-worth", [("worth it!", Y, 270)], 37.45, 38.98, "center", 175),
    ("o-hari", [("jumaat", W_, 175), ("sabtu", W_, 185), ("ahad", Y, 235)], 40.78, 43.60, "right", 250),
    ("o-tempat", [("perlis", Y, 185), ("kedah", W_, 185), ("penang", W_, 170)], 43.64, 48.65, "right", 250),
    ("o-promo", [("harga", W_, 185), ("promosi", Y, 155), ("3 hari", W_, 175)], 48.70, 51.52, "right", 250),
    ("o-wa", [("whatsapp", G, 140), ("booking", W_, 160), ("slot", Y, 250)], 51.58, DURATION, "right", 250),
]

# ---------------- captions ----------------
W = []
for i, w in enumerate(words):
    t = FIX.get(i, w["w"].strip()).strip(",.?").lower()
    e = w["e"]; s = max(w["s"], e - MAX_WORD_DUR)
    W.append({"i": i, "t": t, "s": round(s, 3), "e": round(e, 3)})
phrases, cur = [], []
for w in W:
    if w["t"]:
        cur.append(w)
    if w["i"] in BREAKS and cur:
        phrases.append(cur); cur = []
if cur:
    phrases.append(cur)
groups = []
for p in phrases:
    n = -(-len(p) // MAX_WORDS); size = -(-len(p) // n)
    groups += [p[k:k + size] for k in range(0, len(p), size)]

cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    gs = max(0.1, g[0]["s"] - 0.05)
    nxt = groups[gi + 1][0]["s"] - 0.05 if gi + 1 < len(groups) else DURATION
    ge = max(min(g[-1]["e"] + 0.25, nxt, DURATION - 0.04), g[-1]["e"])
    spans = []
    for w in g:
        wid = f"cw{w['i']}"
        spans.append(f'<span class="w" id="{wid}">{html.escape(w["t"])}</span>')
        cap_js.append(f'tl.set("#{wid}", {{color: "#FFE600", scale: 1.08}}, {w["s"]:.3f});')
        cap_js.append(f'tl.set("#{wid}", {{color: "#FFFFFF", scale: 1}}, {w["e"]:.3f});')
    cap_html.append(f'    <div id="cg{gi}" class="clip grp" data-start="{gs:.3f}" data-duration="{ge - gs:.3f}">'
                    f'<div class="line">{" ".join(spans)}</div></div>')
    cap_js.append(f'tl.fromTo("#cg{gi} .line", {{opacity: 0, y: 10}}, {{opacity: 1, y: 0, duration: 0.12, ease: "power2.out"}}, {gs:.3f});')

captions = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .grp {{ position: absolute; left: 0; width: 100%; top: 1010px; height: 120px; overflow: visible;
           display: flex; align-items: center; justify-content: center; }}
    .line {{ width: 100%; padding: 0 70px; text-align: center; font-family: Montserrat, sans-serif;
            font-weight: 900; font-size: 56px; line-height: 1.05; color: #FFFFFF;
            -webkit-text-stroke: 7px #000; paint-order: stroke fill;
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

# ---------------- big text behind the person ----------------
ov_html, ov_js = [], []
for oid, lines, s, e, align, top in OVERLAYS:
    divs = []
    for k, (txt, col, px) in enumerate(lines):
        cls = "ln"
        divs.append(f'<div id="{oid}-{k}" class="{cls}" style="color:{col};font-size:{px}px">{html.escape(txt)}</div>')
        ov_js.append(f'tl.fromTo("#{oid}-{k}", {{y: 150, opacity: 0}}, {{y: 0, opacity: 1, duration: 0.32, '
                     f'ease: "power4.out"}}, {s + 0.02 + 0.1 * k:.3f});')
    ov_js.append(f'tl.fromTo("#{oid} .stack", {{scale: 1}}, {{scale: 1.05, duration: {max(0.3, e - s - 0.5):.3f}, ease: "none"}}, {s + 0.4:.3f});')
    ov_js.append(f'tl.to("#{oid} .stack", {{opacity: 0, duration: 0.14, ease: "power2.in"}}, {e - 0.15:.3f});')
    ov_html.append(f'    <div id="{oid}" class="clip ov {align}" data-start="{s:.3f}" data-duration="{e - s:.3f}" '
                   f'style="top:{top}px" data-layout-allow-overlap><div class="stack">{"".join(divs)}</div></div>')

overlays = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .ov {{ position: absolute; left: 0; width: 100%; top: 250px; overflow: visible; }}
    .stack {{ display: flex; flex-direction: column; align-items: center; transform-origin: 50% 0; }}
    .left .stack {{ align-items: flex-start; padding-left: 56px; transform-origin: 0 0; }}
    .right .stack {{ align-items: flex-end; padding-right: 40px; transform-origin: 100% 0; }}
    .ln {{ font-family: "League Gothic", Oswald, sans-serif; font-weight: 400; text-transform: uppercase;
          line-height: 0.86; white-space: nowrap; text-shadow: 0 14px 40px rgba(0,0,0,.35); }}
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

TITLE_END = 4.9
title = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    #t-kicker {{ position: absolute; left: 0; width: 100%; top: 1160px; display: flex; justify-content: center; }}
    #t-kicker span {{ font-family: Montserrat, sans-serif; font-weight: 800; font-size: 40px; color: #111;
                     background: #FFE600; padding: 10px 28px; border-radius: 999px; text-transform: lowercase; }}
  </style>
  <div id="root" data-composition-id="title" data-width="1080" data-height="1920">
    <div id="t-kicker" class="clip" data-start="0" data-duration="{TITLE_END}"><span>testimoni abg polo</span></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#t-kicker span", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "power3.out" }}, 0.05);
    tl.to("#t-kicker span", {{ opacity: 0, y: -20, duration: 0.25, ease: "power2.in" }}, {TITLE_END - 0.3});
    window.__timelines["title"] = tl;
  </script>
</template>
"""

cut_tags = "\n".join(
    f'      <video id="{cid}" class="clip cut" src="assets/{cid}.webm" data-start="{s}" data-duration="{d}"\n'
    f'             data-track-index="{5 + k}" muted playsinline data-layout-allow-occlusion></video>'
    for k, (cid, (s, d)) in enumerate(CUTOUTS.items()))

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
      #base, .cut {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; }}
      #base {{ z-index: 1; }}
      #overlays {{ position: absolute; inset: 0; z-index: 2; }}
      .cut {{ z-index: 3; }}
      #captions {{ position: absolute; inset: 0; z-index: 4; }}
      #title {{ position: absolute; inset: 0; z-index: 5; }}
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
{cut_tags}
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
print(len(groups), "caption groups,", len(OVERLAYS), "overlays,", len(CUTOUTS), "cutouts")
