"""Generate the HyperFrames compositions for the ustaz "wangian cenuai" video.

Same house style as build_polo.py (lowercase karaoke captions, spoken word turns
yellow, BIG League Gothic keyword text BEHIND the person via a background-removed
cutout), but with a punchier motion set: every overlay picks one of several
entrance animations (slam / chars / slideL / slideR / zoom / flip), gets an
outline "echo" burst and a short landing shake, and punches out on exit.

The source was already edited in CapCut, so there is no cut step: base.mp4 is
the source trimmed before the CapCut outro (34.44 s) + 2.0 s held last frame.

Usage: build_ustaz.py HF_DIR
"""
import json, os, sys, html

HF = sys.argv[1]
words = json.load(open(os.path.join(HF, "assets/base_transcript.json")))["base.mp4"]["words"]
DURATION = 36.44

# Whisper mishearings fixed against beam-10 re-transcriptions of the snippets ("" = drop the token)
FIX = {7: "", 6: "mudah-mudah", 25: "wangian", 27: "ini", 41: "", 42: "ayatul", 44: "qulhuwallah",
       45: "al-falaq", 46: "", 48: "an-nas", 49: "", 50: "selawat", 62: "wangian", 81: "al-fatih", 82: ""}
BREAKS = {1, 3, 5, 10, 14, 19, 24, 27, 31, 36, 38, 40, 43, 49, 52, 56, 57, 61, 64, 68, 69, 71, 74, 77, 78}
MAX_WORDS, MAX_WORD_DUR = 3, 0.7
CAP_TOP = 1300      # below the face (the face sits at ~750-1150 in every shot)

CUTOUTS = {"c1": (0, DURATION)}

Y, W_, K, G = "#FFE600", "#FFFFFF", "#141414", "#25D366"
# id, [(text, colour, px[, start])], start, end, align, top(px), animation
OVERLAYS = [
    ("o-asih", [("sifat", K, 170), ("pengasih", Y, 260)], 0.05, 1.96, "center", 330, "slam"),
    ("o-tarik", [("menarik", Y, 300)], 1.98, 2.64, "center", 470, "chars"),
    ("o-sejuk", [("penyejuk", Y, 280)], 2.66, 3.88, "center", 470, "slideL"),
    ("o-pakai", [("bila pakai", K, 170), ("cenuai", Y, 300)], 5.06, 6.04, "center", 330, "slideR"),
    ("o-kasih", [("orang akan", K, 150), ("kasih", Y, 340)], 6.06, 7.64, "center", 320, "zoom"),
    ("o-sayang", [("sayang", Y, 360)], 8.20, 9.64, "center", 420, "chars"),
    ("o-wangi", [("wangian", W_, 200), ("cenuai", Y, 300)], 9.70, 11.28, "center", 400, "slam"),
    ("o-yakin", [("dengan", W_, 150), ("keyakinan", Y, 250)], 11.30, 12.08, "center", 470, "slideR"),
    ("o-titis", [("titis di", W_, 170), ("tapak tangan", Y, 220)], 12.10, 14.18, "center", 470, "chars"),
    ("o-sapu", [("sapu", Y, 400)], 14.20, 15.86, "center", 360, "slam"),
    ("o-fatihah", [("al-fatihah", Y, 250)], 15.90, 16.94, "center", 400, "zoom"),
    ("o-kursi", [("ayatul", W_, 190), ("kursi", Y, 310)], 16.96, 17.92, "center", 320, "flip"),
    ("o-qul", [("qulhuwallah", W_, 160, 17.94), ("al-falaq", Y, 210, 18.38), ("an-nas", W_, 210, 18.96)],
     17.94, 19.46, "center", 250, "slam"),
    ("o-selawat", [("selawat", Y, 300), ("ke atas nabi", W_, 140)], 19.48, 20.54, "center", 330, "chars"),
    ("o-badan", [("seluruh", W_, 190), ("badan", Y, 330)], 20.56, 22.28, "center", 400, "slideL"),
    ("o-niat", [("niat", Y, 440)], 22.30, 23.26, "center", 330, "slam"),
    ("o-minat", [("yang", K, 150), ("berminat", Y, 280)], 23.30, 24.62, "center", 300, "zoom"),
    ("o-wangi2", [("wangian", K, 190), ("cenuai", Y, 310)], 24.66, 25.50, "center", 320, "slam"),
    ("o-beg", [("terus ke", K, 170), ("beg ni!", Y, 330)], 25.52, 26.70, "center", 320, "chars"),
    ("o-insya", [("insyaallah", Y, 250)], 26.72, 28.00, "center", 400, "flip"),
    ("o-ikhtiar", [("ikhtiar", Y, 330)], 28.02, 29.00, "center", 360, "slideR"),
    ("o-beri", [("allah", K, 200), ("berikan", Y, 270)], 29.00, 30.04, "center", 320, "zoom"),
    ("o-ori", [("pastikan", K, 180), ("original", Y, 290)], 30.06, 32.52, "center", 320, "slam"),
    ("o-fatih", [("pusat rawatan", K, 150), ("al-fatih", Y, 340)], 32.54, DURATION, "center", 300, "chars"),
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
    gs = max(0.05, g[0]["s"] - 0.05)
    nxt = groups[gi + 1][0]["s"] - 0.05 if gi + 1 < len(groups) else DURATION
    ge = max(min(g[-1]["e"] + 0.25, nxt, DURATION - 0.04), g[-1]["e"])
    spans = []
    for w in g:
        wid = f"cw{w['i']}"
        spans.append(f'<span class="w" id="{wid}">{html.escape(w["t"])}</span>')
        cap_js.append(f'tl.set("#{wid}", {{color: "#FFE600"}}, {w["s"]:.3f});')
        cap_js.append(f'tl.fromTo("#{wid}", {{scale: 1.22}}, {{scale: 1.08, duration: {min(0.12, w["e"] - w["s"] - 0.02):.3f}, ease: "back.out(3)"}}, {w["s"]:.3f});')
        cap_js.append(f'tl.set("#{wid}", {{color: "#FFFFFF", scale: 1}}, {w["e"]:.3f});')
    cap_html.append(f'    <div id="cg{gi}" class="clip grp" data-start="{gs:.3f}" data-duration="{ge - gs:.3f}">'
                    f'<div class="line">{" ".join(spans)}</div></div>')
    cap_js.append(f'tl.fromTo("#cg{gi} .line", {{opacity: 0, y: 14, scale: 0.92}}, {{opacity: 1, y: 0, scale: 1, duration: 0.14, ease: "back.out(2)"}}, {gs:.3f});')

captions = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .grp {{ position: absolute; left: 0; width: 100%; top: {CAP_TOP}px; height: 120px; overflow: visible;
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
def enter(sel, anim, t, k):
    """GSAP entrance for one line (sel) starting at t."""
    if anim == "slam":
        return [f'tl.fromTo("{sel}", {{scale: 2.8, opacity: 0, filter: "blur(18px)"}}, '
                f'{{scale: 1, opacity: 1, filter: "blur(0px)", duration: 0.22, ease: "power4.in"}}, {t:.3f});']
    if anim == "chars":
        return [f'tl.fromTo("{sel} .ch", {{y: -260, rotation: -35, opacity: 0}}, '
                f'{{y: 0, rotation: 0, opacity: 1, duration: 0.34, ease: "back.out(2.2)", stagger: 0.035}}, {t:.3f});']
    if anim in ("slideL", "slideR"):
        x = -1100 if (anim == "slideL") == (k % 2 == 0) else 1100
        return [f'tl.fromTo("{sel}", {{x: {x}, skewX: {-30 if x > 0 else 30}, opacity: 0}}, '
                f'{{x: 0, skewX: 0, opacity: 1, duration: 0.3, ease: "expo.out"}}, {t:.3f});']
    if anim == "zoom":
        return [f'tl.fromTo("{sel}", {{scale: 0.1, rotation: {-12 if k % 2 == 0 else 10}, opacity: 0}}, '
                f'{{scale: 1, rotation: 0, opacity: 1, duration: 0.36, ease: "back.out(3)"}}, {t:.3f});']
    if anim == "flip":
        return [f'tl.fromTo("{sel}", {{rotationX: -100, y: 60, opacity: 0}}, '
                f'{{rotationX: 0, y: 0, opacity: 1, duration: 0.36, ease: "back.out(2)"}}, {t:.3f});']
    raise ValueError(anim)


def chars(txt):
    return "".join('<span class="ch">&nbsp;</span>' if c == " " else f'<span class="ch">{html.escape(c)}</span>'
                   for c in txt)


ov_html, ov_js = [], []
for oid, lines, s, e, align, top, anim in OVERLAYS:
    divs, land = [], s
    for k, ln in enumerate(lines):
        txt, col, px = ln[:3]
        t = ln[3] if len(ln) > 3 else s + 0.02 + 0.09 * k
        inner = chars(txt) if anim == "chars" else html.escape(txt)
        cls = "ln dark" if col == K else ("ln hi" if col == Y else "ln")
        divs.append(f'<div id="{oid}-{k}" class="{cls}" style="color:{col};font-size:{px}px">{inner}</div>')
        ov_js += enter(f"#{oid}-{k}", anim, t, k)
        land = max(land, t + (0.22 if anim == "slam" else 0.3))
    # outline echo of the hero (largest) line bursting outwards when it lands
    hero = max(range(len(lines)), key=lambda k: lines[k][2])
    htxt, hcol, hpx = lines[hero][:3]
    echo = (f'<div id="{oid}-echo" class="ln echo" style="font-size:{hpx}px;-webkit-text-stroke-color:{hcol}">'
            f'{html.escape(htxt)}</div>')
    ov_js.append(f'tl.fromTo("#{oid}-echo", {{scale: 1, opacity: 0.9}}, {{scale: 1.55, opacity: 0, duration: 0.5, '
                 f'ease: "power2.out"}}, {land:.3f});')
    # landing shake + slow push-in for the rest of the window
    ov_js.append(f'tl.to("#{oid} .stack", {{keyframes: {{x: [-16, 13, -9, 5, 0], y: [9, -7, 4, -2, 0]}}, '
                 f'duration: 0.3, ease: "none"}}, {land:.3f});')
    ov_js.append(f'tl.fromTo("#{oid} .stack", {{scale: 1}}, {{scale: 1.06, duration: {max(0.1, e - land - 0.14):.3f}, '
                 f'ease: "none"}}, {land:.3f});')
    if e < DURATION - 0.05:
        ov_js.append(f'tl.to("#{oid} .stack", {{scale: 1.25, opacity: 0, filter: "blur(10px)", duration: 0.12, '
                     f'ease: "power2.in"}}, {e - 0.12:.3f});')
    hero_top = sum(lines[k][2] * 0.86 for k in range(hero))
    ov_html.append(f'    <div id="{oid}" class="clip ov {align}" data-start="{s:.3f}" data-duration="{e - s:.3f}" '
                   f'style="top:{top}px" data-layout-allow-overlap><div class="stack">{"".join(divs)}'
                   f'<div class="echo-wrap" style="top:{hero_top:.0f}px">{echo}</div></div></div>')

overlays = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; perspective: 1400px; }}
    .ov {{ position: absolute; left: 0; width: 100%; top: 250px; overflow: visible; perspective: 1400px; }}
    .stack {{ position: relative; display: flex; flex-direction: column; align-items: center; transform-origin: 50% 50%; }}
    .left .stack {{ align-items: flex-start; padding-left: 56px; transform-origin: 0 50%; }}
    .right .stack {{ align-items: flex-end; padding-right: 40px; transform-origin: 100% 50%; }}
    .ln {{ font-family: "League Gothic", Oswald, sans-serif; font-weight: 400; text-transform: uppercase;
          line-height: 0.86; white-space: nowrap; text-shadow: 0 14px 40px rgba(0,0,0,.35);
          transform-origin: 50% 60%; }}
    .ln.hi {{ -webkit-text-stroke: 5px #141414; paint-order: stroke fill;
          text-shadow: 8px 10px 0 rgba(0,0,0,.85), 0 18px 50px rgba(0,0,0,.45); }}
    .ln.dark {{ text-shadow: 0 10px 30px rgba(255,255,255,.35); }}
    .ch {{ display: inline-block; transform-origin: 50% 100%; }}
    .echo-wrap {{ position: absolute; left: 0; width: 100%; display: flex; justify-content: center; pointer-events: none; }}
    .echo {{ color: transparent; -webkit-text-stroke-width: 6px; -webkit-text-stroke-style: solid; text-shadow: none;
            opacity: 0; transform-origin: 50% 50%; }}
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
    #t-kicker {{ position: absolute; left: 0; width: 100%; top: {CAP_TOP + 150}px; display: flex; justify-content: center; }}
    #t-kicker span {{ font-family: Montserrat, sans-serif; font-weight: 800; font-size: 40px; color: #111;
                     background: #FFE600; padding: 10px 28px; border-radius: 999px; text-transform: lowercase; }}
  </style>
  <div id="root" data-composition-id="title" data-width="1080" data-height="1920">
    <div id="t-kicker" class="clip" data-start="0" data-duration="{TITLE_END}"><span>wangian cenuai · al-fatih</span></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#t-kicker span", {{ opacity: 0, y: -30, scale: 0.6 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.35, ease: "back.out(2.5)" }}, 0.05);
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
