"""Kinetic-subtitle builder ("cenuai kinetic" style) for HyperFrames.

The subtitle IS the motion graphic (reference: Submagic-style edit):
  * "big" phrases  - the caption becomes mixed-size / mixed-font typography placed
                     BEHIND the person (base video -> big text -> cutout -> small captions).
                     Every word pops in exactly when it is spoken; "hero" lines are typed
                     letter-by-letter, optionally arched, then the block shakes on landing.
  * every other word - small clean captions (Inter 800) on the chest, the word being
                     spoken turns yellow.

Usage: kinetic.py SPEC_JSON HF_DIR
  SPEC_JSON (see ustaz/kinetic_spec.json):
  {
    "duration": 36.44,                    # ffprobe of assets/base.mp4
    "fix": {"25": "wangian", "7": ""},    # word index -> corrected text ("" drops it)
    "breaks": [10, 14],                   # small-caption phrase ends after these word indices
    "cap_top": 1250,                      # small captions y (px)
    "pill": ["wangian cenuai", 0, 4.9],   # optional yellow pill (text, start, end)
    "cutouts": {"c1": [0, 36.44]},        # id -> [start, duration]; background-removed person, assets/<id>.webm
    "phrases": [                          # big phrases, in time order
      {"top": 330, "theme": "light",      # light wall -> dark ink; dark bg -> white ink
       "align": "center",                 # center | left | right
       "hold": 36.44,                     # optional: keep on screen until this time
       "lines": [
         {"w": [0, 0], "style": "serif", "size": 120},
         {"w": [1, 1], "style": "hero", "size": 250, "arch": 1, "color": "#FFE600"}]}
    ]
  }
  styles: hero (League Gothic caps, typed + arched, yellow by default) | block (League Gothic
  caps, pops per word) | sans (Inter 800 lowercase) | serif (Playfair Display italic).
  optional per line: "dx": px sideways shift (move a small trailing line beside the face
  instead of letting the head cover it).
"""
import json, os, sys, html

spec = json.load(open(sys.argv[1]))
HF = sys.argv[2]
words = json.load(open(os.path.join(HF, "assets/base_transcript.json")))["base.mp4"]["words"]
DURATION = spec["duration"]
FIX = {int(k): v for k, v in spec.get("fix", {}).items()}
BREAKS = set(spec.get("breaks", []))
CAP_TOP = spec.get("cap_top", 1250)
Y, WH, K = "#FFE600", "#FFFFFF", "#141414"
MAX_WORD_DUR, SMALL_MAX = 0.7, 4

W = {}
for i, w in enumerate(words):
    t = FIX.get(i, w["w"].strip()).strip(",.?!").strip()
    if i not in FIX:
        t = t.lower()   # house style: lowercase (FIX entries are kept verbatim, e.g. "insyaAllah")
    if t:
        W[i] = {"i": i, "t": t, "s": round(max(w["s"], w["e"] - MAX_WORD_DUR), 3), "e": round(w["e"], 3)}

# ---------------- big phrases ----------------
big, in_big = [], set()
for p in spec["phrases"]:
    idx = [i for ln in p["lines"] for i in range(ln["w"][0], ln["w"][1] + 1) if i in W]
    in_big.update(idx)
    big.append(dict(p, idx=idx, s=W[idx[0]]["s"] - 0.06, last=W[idx[-1]]["e"]))
for k, p in enumerate(big):
    nxt = big[k + 1]["s"] if k + 1 < len(big) else DURATION
    p["e"] = p.get("hold") or min(p["last"] + 0.45, nxt - 0.02, DURATION)


def chars_html(txt, arch, px):
    n = len(txt); mid = (n - 1) / 2; out = []
    for j, c in enumerate(txt):
        d = (j - mid) / mid if mid else 0
        tr = f"translateY({arch * d * d * px * 0.10:.1f}px) rotate({arch * d * 7:.2f}deg)" if arch else "none"
        out.append(f'<span class="arc" style="transform:{tr}"><span class="ch">'
                   f'{"&nbsp;" if c == " " else html.escape(c)}</span></span>')
    return "".join(out)


kp_html, kp_js = [], []
for k, p in enumerate(big):
    pid = f"kp{k}"; ink = K if p.get("theme", "light") == "light" else WH
    land = p["s"]; lines_html = []
    for ln in p["lines"]:
        st = ln["style"]; px = ln["size"]
        col = ln.get("color", Y if st == "hero" else ink)
        spans = []
        for i in range(ln["w"][0], ln["w"][1] + 1):
            if i not in W:
                continue
            w = W[i]; wid = f"{pid}w{i}"
            if st == "hero":
                txt = w["t"].upper()
                spans.append(f'<span class="kw" id="{wid}">{chars_html(txt, ln.get("arch", 0), px)}</span>')
                n = len(txt); dt = min(0.045, max(0.02, 0.6 * (w["e"] - w["s"]) / max(n, 1)))
                kp_js.append(f'tl.fromTo("#{wid} .ch", {{opacity: 0, scale: 1.7, y: -30}}, {{opacity: 1, scale: 1, y: 0, '
                             f'duration: 0.12, ease: "power3.out", stagger: {dt:.3f}}}, {w["s"]:.3f});')
                land = max(land, w["s"] + dt * n + 0.1)
            else:
                spans.append(f'<span class="kw" id="{wid}">{html.escape(w["t"] if st != "block" else w["t"].upper())}</span>')
                kp_js.append(f'tl.fromTo("#{wid}", {{opacity: 0, y: 46, scale: 0.45, filter: "blur(8px)"}}, '
                             f'{{opacity: 1, y: 0, scale: 1, filter: "blur(0px)", duration: 0.22, ease: "back.out(2.2)"}}, {w["s"]:.3f});')
                land = max(land, w["s"] + 0.22)
        dx = f";transform:translateX({ln['dx']}px)" if ln.get("dx") else ""
        lines_html.append(f'<div class="kl {st}" style="font-size:{px}px;color:{col}{dx}">{" ".join(spans)}</div>')
    e = p["e"]; land = min(land, e - 0.2)
    kp_js.append(f'tl.to("#{pid} .stack", {{keyframes: {{x: [-14, 11, -7, 4, 0], y: [8, -6, 3, -1, 0]}}, '
                 f'duration: 0.26, ease: "none"}}, {land:.3f});')
    kp_js.append(f'tl.fromTo("#{pid} .stack", {{scale: 1}}, {{scale: 1.05, duration: {max(0.1, e - p["s"] - 0.16):.3f}, '
                 f'ease: "none"}}, {p["s"]:.3f});')
    if e < DURATION - 0.05:
        kp_js.append(f'tl.to("#{pid} .stack", {{y: -50, opacity: 0, filter: "blur(10px)", duration: 0.13, '
                     f'ease: "power2.in"}}, {e - 0.14:.3f});')
    kp_html.append(f'    <div id="{pid}" class="clip kp {p.get("align", "center")} {p.get("theme", "light")}" '
                   f'data-start="{p["s"]:.3f}" data-duration="{e - p["s"]:.3f}" style="top:{p["top"]}px" '
                   f'data-layout-allow-overlap><div class="stack">{"".join(lines_html)}</div></div>')

kinetic = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .kp {{ position: absolute; left: 0; width: 100%; overflow: visible; }}
    .stack {{ display: flex; flex-direction: column; align-items: center; transform-origin: 50% 40%; }}
    .left .stack {{ align-items: flex-start; padding-left: 50px; transform-origin: 0 40%; }}
    .right .stack {{ align-items: flex-end; padding-right: 50px; transform-origin: 100% 40%; }}
    .kl {{ white-space: nowrap; line-height: 0.95; }}
    .kw, .arc, .ch {{ display: inline-block; }}
    .ch {{ transform-origin: 50% 80%; }}
    .hero, .block {{ font-family: "League Gothic", sans-serif; font-weight: 400; line-height: 0.84; letter-spacing: 1px; }}
    .sans {{ font-family: Inter, sans-serif; font-weight: 800; letter-spacing: -1px; }}
    .serif {{ font-family: "Playfair Display", serif; font-style: italic; font-weight: 700; line-height: 1.0; }}
    .light .kl {{ text-shadow: 0 0 30px rgba(255,255,255,.55), 0 6px 18px rgba(0,0,0,.18); }}
    .dark .kl {{ text-shadow: 0 0 26px rgba(0,0,0,.55), 0 6px 18px rgba(0,0,0,.4); }}
    .kl.hero, .kl.block {{ -webkit-text-stroke: 4px #141414; paint-order: stroke fill;
          text-shadow: 7px 9px 0 rgba(0,0,0,.85), 0 16px 44px rgba(0,0,0,.4); }}
  </style>
  <div id="root" data-composition-id="kinetic" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-allow-caption-zone>
{chr(10).join(kp_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10) + '    '.join(kp_js)}
    window.__timelines["kinetic"] = tl;
  </script>
</template>
"""

# ---------------- small captions (everything not in a big phrase) ----------------
groups, cur = [], []
order = sorted(W)
for n, i in enumerate(order):
    if i in in_big:
        if cur:
            groups.append(cur); cur = []
        continue
    if cur and (W[i]["s"] - cur[-1]["e"] > 0.35 or len(cur) >= SMALL_MAX):
        groups.append(cur); cur = []
    cur.append(W[i])
    if i in BREAKS:
        groups.append(cur); cur = []
if cur:
    groups.append(cur)
starts = sorted([g[0]["s"] for g in groups] + [p["s"] for p in big])
cap_html, cap_js = [], []
for gi, g in enumerate(groups):
    gs = max(0.03, g[0]["s"] - 0.05)
    nxt = min([t for t in starts if t > g[0]["s"]] or [DURATION])
    ge = max(min(g[-1]["e"] + 0.3, nxt - 0.03, DURATION - 0.04), g[-1]["e"])
    spans = []
    for w in g:
        wid = f"cw{w['i']}"
        spans.append(f'<span class="w" id="{wid}">{html.escape(w["t"].lower())}</span>')
        cap_js.append(f'tl.set("#{wid}", {{color: "{Y}"}}, {w["s"]:.3f});')
        cap_js.append(f'tl.set("#{wid}", {{color: "#FFFFFF"}}, {w["e"]:.3f});')
    cap_html.append(f'    <div id="cg{gi}" class="clip grp" data-start="{gs:.3f}" data-duration="{ge - gs:.3f}">'
                    f'<div class="line">{" ".join(spans)}</div></div>')
    cap_js.append(f'tl.fromTo("#cg{gi} .line", {{opacity: 0, y: 12, scale: 0.94}}, {{opacity: 1, y: 0, scale: 1, '
                  f'duration: 0.14, ease: "power3.out"}}, {gs:.3f});')

captions = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .grp {{ position: absolute; left: 0; width: 100%; top: {CAP_TOP}px; height: 110px;
           display: flex; align-items: center; justify-content: center; }}
    .line {{ padding: 0 90px; text-align: center; font-family: Inter, sans-serif; font-weight: 800;
            font-size: 50px; letter-spacing: -0.5px; line-height: 1.1; color: #FFFFFF;
            text-shadow: 0 0 18px rgba(0,0,0,.75), 0 2px 6px rgba(0,0,0,.6); }}
    .w {{ display: inline-block; }}
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

pill_txt, p0, p1 = spec.get("pill", ["", 0, 0.1])
pill = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    #t-pill {{ position: absolute; left: 0; width: 100%; top: {CAP_TOP + 140}px; display: flex; justify-content: center; }}
    #t-pill span {{ font-family: Inter, sans-serif; font-weight: 800; font-size: 36px; color: #111;
                   background: #FFE600; padding: 10px 26px; border-radius: 999px; text-transform: lowercase; }}
  </style>
  <div id="root" data-composition-id="title" data-width="1080" data-height="1920">
    <div id="t-pill" class="clip" data-start="{p0}" data-duration="{p1 - p0}"><span>{html.escape(pill_txt)}</span></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#t-pill span", {{ opacity: 0, scale: 0.6 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2.5)" }}, {p0 + 0.05});
    tl.to("#t-pill span", {{ opacity: 0, y: -16, duration: 0.22, ease: "power2.in" }}, {p1 - 0.25});
    window.__timelines["title"] = tl;
  </script>
</template>
"""

cut_tags = "\n".join(
    f'      <video id="{cid}" class="clip cut" src="assets/{cid}.webm" data-start="{s}" data-duration="{d}"\n'
    f'             data-track-index="{5 + k}" muted playsinline data-layout-allow-occlusion></video>'
    for k, (cid, (s, d)) in enumerate(spec["cutouts"].items()))

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
      #kinetic {{ position: absolute; inset: 0; z-index: 2; }}
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
      <div id="kinetic" data-composition-id="kinetic" data-composition-src="compositions/kinetic.html"
           data-start="0" data-duration="{DURATION}" data-track-index="1" data-track-kind="graphics"
           data-width="1080" data-height="1920"></div>
{cut_tags}
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
           data-start="0" data-duration="{DURATION}" data-track-index="2" data-track-kind="captions"
           data-width="1080" data-height="1920"></div>
      <div id="title" data-composition-id="title" data-composition-src="compositions/title.html"
           data-start="{p0}" data-duration="{p1 - p0}" data-track-index="3" data-track-kind="graphics"
           data-width="1080" data-height="1920"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""

os.makedirs(os.path.join(HF, "compositions"), exist_ok=True)
for name in ("overlays.html",):
    if os.path.exists(os.path.join(HF, "compositions", name)):
        os.remove(os.path.join(HF, "compositions", name))
for name, txt in (("compositions/kinetic.html", kinetic), ("compositions/captions.html", captions),
                  ("compositions/title.html", pill), ("index.html", index)):
    open(os.path.join(HF, name), "w").write(txt)
# every spoken word in order, for verify.py
allg = [[{"t": W[i]["t"].lower(), "s": W[i]["s"], "e": W[i]["e"]} for i in p["idx"]] for p in big] + \
       [[{"t": w["t"].lower(), "s": w["s"], "e": w["e"]} for w in g] for g in groups]
allg.sort(key=lambda g: g[0]["s"])
json.dump(allg, open(os.path.join(HF, "assets/caption_groups.json"), "w"), ensure_ascii=False, indent=1)
print(len(big), "big phrases,", len(groups), "small caption groups")
