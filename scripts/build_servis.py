"""Generate the HyperFrames compositions for the "servis sebelum kahwin" shockwave promo.

Same concept as the first video (build_hf.py): lowercase karaoke captions in
the centre, plus BIG keyword text placed *behind* the person, made by putting a
background-removed cutout of the footage (assets/cN.webm) above the text.

Usage: build_servis.py HF_DIR [--cutouts]
"""
import json, os, sys, html

HF = sys.argv[1]
words = json.load(open(os.path.join(HF, "assets/base_transcript.json")))["base.mp4"]["words"]
DURATION = 106.25  # ffprobe of assets/base.mp4 (103.24 s cut + 3.0 s held last frame)

H_ = "hampa"  # northern "hampa" (you), Whisper hears "Ampua/Ampuan/Ampun"
FIX = {1: "geng-geng", 2: "", 11: "imaginasi", 12: H_, 19: "", 20: "ping-pong", 22: "ping-pong",
       23: "sendirilah", 24: "", 26: "mari", 27: "sini", 28: "", 30: H_, 40: "apa", 42: H_, 47: H_,
       51: H_, 65: "mak", 66: "mentua,", 72: H_, 76: H_, 78: "je", 113: "urut", 114: "pelik-pelik", 115: "", 128: "barang-barang",
       129: "", 139: "atas", 151: "kawasan", 159: "kawasan", 166: "shockwave", 167: "", 203: H_,
       209: H_, 212: "ribu-ribu", 213: "", 217: "kenduri", 226: H_, 247: H_, 248: "shockwave", 251: "rm40", 252: "", 253: "",
       258: "mana-mana", 259: "", 263: "rm40", 264: "", 265: "", 274: H_, 279: "urut", 283: "servis", 288: "servis", 290: "apa",
       297: H_, 299: "booking,", 300: H_, 317: H_}
BREAKS = {5, 8, 10, 15, 18, 21, 24, 28, 33, 36, 39, 42, 45, 50, 56, 58, 62, 67, 70, 75, 79, 84, 87,
          95, 99, 102, 107, 110, 115, 119, 124, 127, 130, 135, 140, 145, 148, 152, 157, 160, 165, 170, 175,
          179, 182, 183, 188, 190, 194, 196, 201, 204, 208, 213, 217, 222, 225, 228, 233, 238, 244,
          248, 254, 259, 262, 265, 270, 273, 276, 281, 285, 288, 294, 299, 301, 306, 309, 315, 317, 321}
MAX_WORDS, MAX_WORD_DUR = 3, 0.7

G, W_, Y = "#25D366", "#FFFFFF", "#FFE600"
T = 170  # overlay top: the zone between the ceiling and the head
OVERLAYS = [  # id, [(text, colour, px)], start, end, align, top(px)
    ("o-kahwin", [("belum", W_, 210), ("kahwin", Y, 270)], 1.20, 2.95, "center", T),
    ("o-imaj", [("imaginasi", W_, 170), ("tinggi!", Y, 290)], 3.04, 4.98, "center", T),
    ("o-ping", [("ping-pong", Y, 250)], 6.42, 8.80, "center", T),
    ("o-servis", [("servis", W_, 220), ("dulu", Y, 260)], 11.08, 13.95, "center", T),
    ("o-bini", [("malam pertama", W_, 130), ("bini lari!", Y, 250)], 19.30, 21.85, "center", T),
    ("o-problem", [("problem", Y, 230), ("ke tak?", W_, 200)], 26.80, 28.70, "center", T),
    ("o-speed", [("top", W_, 220), ("speed", Y, 270)], 33.18, 35.04, "center", T),
    ("o-ubat", [("tak ada ubat", Y, 170)], 36.82, 38.14, "center", 140),
    ("o-urut", [("urut", Y, 170), ("pelik-pelik", W_, 115)], 38.14, 40.30, "left", 110),
    ("o-blood", [("blood", W_, 190), ("circulation", Y, 130)], 50.62, 52.96, "center", 140),
    ("o-shock", [("shockwave", Y, 210)], 54.58, 56.70, "center", T),
    ("o-gelom", [("gelombang", Y, 200)], 56.70, 58.20, "center", T),
    ("o-overhaul", [("servis", W_, 200), ("overhaul", Y, 230)], 61.40, 62.75, "center", T),
    ("o-piston", [("piston", W_, 160), ("baru", Y, 200)], 63.44, 65.18, "center", 130),
    ("o-promo", [("harga", W_, 170), ("promosi", Y, 200)], 65.94, 69.90, "center", 140),
    ("o-ribu", [("ribu-ribu", Y, 230)], 71.34, 73.00, "center", T),
    ("o-pilih", [("bekam / urut", Y, 180)], 77.48, 81.00, "center", 160),
    ("o-rm40", [("rm40 je!", Y, 240)], 82.50, 84.50, "center", 150),
    ("o-rendah", [("harga paling", W_, 140), ("rendah", Y, 270)], 86.28, 87.44, "center", T),
    ("o-syarat", [("syarat:", W_, 170), ("bekam / urut", Y, 170)], 87.62, 91.26, "center", T),
    ("o-wa", [("whatsapp", G, 150), ("booking slot", Y, 130)], 95.24, DURATION, "center", 120),
]

# cutouts of the person behind each overlay (id -> (start, duration)); merged when windows touch
_cw = []
for _o in OVERLAYS:
    s0, e0 = round(_o[2] - 0.1, 2), round(min(_o[3] + 0.05, DURATION), 2)
    if _cw and s0 - _cw[-1][1] < 0.6:
        _cw[-1][1] = e0
    else:
        _cw.append([s0, e0])
CUTOUTS = {f"c{k + 1}": (s0, round(e0 - s0, 2)) for k, (s0, e0) in enumerate(_cw)}
if __name__ == "__main__" and len(sys.argv) > 2 and sys.argv[2] == "--cutouts":
    for k, v in CUTOUTS.items():
        print(k, v[0], v[1])
    sys.exit()

# ---------------- captions ----------------
W = []
for i, w in enumerate(words):
    t = FIX.get(i, w["w"].strip()).strip(",.?").lower().replace("service", "servis")
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
    ge = max(min(g[-1]["e"] + 0.25, nxt, DURATION - 0.04), gs + 0.1)
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
    <div id="t-kicker" class="clip" data-start="0" data-duration="{TITLE_END}"><span>servis sebelum kahwin</span></div>
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
