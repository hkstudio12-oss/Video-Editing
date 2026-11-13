"""Kinetic-typography HyperFrames compositions (engine; project data lives in a config .py).

Style taken from the user's reference clip:
  * key phrases become a KINETIC BLOCK in the upper half: words pop in one by one
    exactly when spoken, mixing three faces --
      s = small bold sans (lowercase), b = huge condensed caps with a white glow,
      i = serif italic accent in warm yellow with a glow --
    staggered left / right like a magazine layout, and sitting BEHIND the person
    (background-removed cutout assets/cN.webm on top of the text).
  * everything else is a small, clean subtitle (no heavy stroke), keyword in yellow.
  * while a block is on screen the normal subtitle is hidden.

Usage: build_kinetic.py HF_DIR CONFIG.py [--cutouts]
"""
import json, os, sys, html

HF = sys.argv[1]
words = json.load(open(os.path.join(HF, "assets/base_transcript.json")))["base.mp4"]["words"]
CFG = sys.argv[2]  # project config .py (DURATION, FIX, BREAKS, KEYWORDS, BLOCKS, CUTOUTS, TITLE_TEXT, colours)
Y, G, W_ = "#FFC21A", "#2BE07A", "#FFFFFF"
MAX_WORDS, MAX_WORD_DUR = 3, 0.7
_ns = {"Y": Y, "G": G, "W_": W_, "MAX_WORDS": MAX_WORDS, "MAX_WORD_DUR": MAX_WORD_DUR}
exec(open(CFG).read(), _ns)
DURATION, FIX, BREAKS, KEYWORDS, BLOCKS = (_ns[k] for k in ("DURATION", "FIX", "BREAKS", "KEYWORDS", "BLOCKS"))
TITLE_TEXT = _ns.get("TITLE_TEXT", "")
if "CUTOUTS" in _ns:
    CUTOUTS = _ns["CUTOUTS"]
else:  # one cutout per block window, merged when windows touch
    _cw = []
    for _b in BLOCKS:
        if _b[0] in _ns.get("NO_CUTOUT", set()):
            continue
        s0, e0 = round(max(0.0, _b[1] - 0.1), 2), round(min(_b[2] + 0.05, DURATION), 2)
        if _cw and s0 - _cw[-1][1] < 0.6:
            _cw[-1][1] = e0
        else:
            _cw.append([s0, e0])
    CUTOUTS = {f"c{k + 1}": (s0, round(e0 - s0, 2)) for k, (s0, e0) in enumerate(_cw)}
if len(sys.argv) > 3 and sys.argv[3] == "--cutouts":
    for k, v in CUTOUTS.items():
        print(k, v[0], v[1])
    sys.exit()

def text(i):
    return FIX.get(i, words[i]["w"].strip()).strip(",.?").lower().replace("service", "servis")


def wstart(i):
    w = words[i]
    return max(w["s"], w["e"] - MAX_WORD_DUR)


# ---------------- kinetic blocks (behind the person) ----------------
FACE = {"s": ("Inter", 800, "normal", "none", 1.0), "b": ("Anton", 400, "normal", "uppercase", 0.88),
        "i": ("Instrument Serif", 400, "italic", "none", 0.95)}
k_html, k_js, in_block = [], [], set()
for bid, bs, be, top, lines in BLOCKS:
    rows = []
    for li, ln in enumerate(lines):
        align, sty, px, toks = ln[:4]
        col = ln[4] if len(ln) > 4 else (Y if sty == "i" else W_)
        items = []
        for t in toks:
            if isinstance(t, tuple):
                items.append((f"{bid}l{li}", t[0], t[1]))
            else:
                in_block.add(t)
                if text(t):
                    items.append((f"kw{t}", text(t), wstart(t)))
        if sty == "b":  # fit huge condensed words inside 950 px
            n = len(" ".join(x[1] for x in items))
            px = min(px, int(950 / (0.50 * max(n, 1))))
        spans = " ".join(f'<span class="kw" id="{sid}">{html.escape(tx)}</span>' for sid, tx, _ in items)
        rows.append(f'<div class="kl {sty} {align}" style="font-size:{px}px;color:{col}">{spans}</div>')
        for sid, _, ts in items:
            ts = max(ts, bs + 0.02)
            if sty == "b":
                k_js.append(f'tl.fromTo("#{sid}", {{opacity: 0, scale: 1.35, clipPath: "inset(0 100% 0 0)"}}, '
                            f'{{opacity: 1, scale: 1, clipPath: "inset(0 0% 0 0)", duration: 0.24, ease: "power3.out"}}, {ts:.3f});')
            else:
                k_js.append(f'tl.fromTo("#{sid}", {{opacity: 0, y: 26, filter: "blur(8px)"}}, '
                            f'{{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.2, ease: "back.out(2)"}}, {ts:.3f});')
    k_js.append(f'tl.fromTo("#{bid} .blk", {{scale: 1}}, {{scale: 1.04, duration: {max(0.3, be - bs):.3f}, ease: "none"}}, {bs:.3f});')
    if be < DURATION - 0.01:
        k_js.append(f'tl.to("#{bid} .blk", {{opacity: 0, y: -18, duration: 0.14, ease: "power2.in"}}, {be - 0.14:.3f});')
    k_html.append(f'    <div id="{bid}" class="clip kb" data-start="{bs:.3f}" data-duration="{be - bs:.3f}" '
                  f'style="top:{top}px" data-layout-allow-overlap><div class="blk">{"".join(rows)}</div></div>')

blocks = f"""<template>
  <style>
    @font-face {{ font-family: "Anton"; src: url("assets/fonts/Anton-Regular.ttf") format("truetype"); font-weight: 400; font-style: normal; }}
    @font-face {{ font-family: "Instrument Serif"; src: url("assets/fonts/InstrumentSerif-Italic.ttf") format("truetype"); font-weight: 400; font-style: italic; }}
    #root {{ position: absolute; inset: 0; }}
    .kb {{ position: absolute; left: 0; width: 100%; overflow: visible; }}
    .blk {{ padding: 0 64px; transform-origin: 50% 30%; }}
    .kl {{ white-space: nowrap; }}
    .kl.l {{ text-align: left; }} .kl.c {{ text-align: center; }} .kl.r {{ text-align: right; }}
    .kw {{ display: inline-block; transform-origin: 50% 70%; }}
    .s {{ font-family: Inter, sans-serif; font-weight: 800; letter-spacing: -0.02em; line-height: 1.12;
          text-shadow: 0 0 18px rgba(255,255,255,.35), 0 3px 14px rgba(0,0,0,.45); }}
    .b {{ font-family: Anton, "League Gothic", sans-serif; font-weight: 400; text-transform: uppercase;
          line-height: 1.0; letter-spacing: -0.005em; margin: 2px 0 4px;
          text-shadow: 0 0 22px rgba(255,255,255,.55), 0 0 60px rgba(255,255,255,.25), 0 8px 30px rgba(0,0,0,.35); }}
    .i {{ font-family: "Instrument Serif", "Playfair Display", serif; font-style: italic; font-weight: 400;
          line-height: 1.12; text-shadow: 0 0 16px rgba(255,170,0,.85), 0 0 42px rgba(255,140,0,.45), 0 3px 12px rgba(0,0,0,.35); }}
  </style>
  <div id="root" data-composition-id="blocks" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-allow-caption-zone>
{chr(10).join(k_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {chr(10) + '    '.join(k_js)}
    window.__timelines["blocks"] = tl;
  </script>
</template>
"""

# ---------------- small clean subtitles for the rest ----------------
windows = [(b[1], b[2]) for b in BLOCKS]
W = []
for i, w in enumerate(words):
    t = text(i)
    s = wstart(i)
    hidden = i in in_block or any(a - 0.05 <= s < b for a, b in windows)
    W.append({"i": i, "t": "" if hidden else t, "s": round(s, 3), "e": round(w["e"], 3)})
phrases, cur = [], []
for w in W:
    if w["t"]:
        cur.append(w)
    if (w["i"] in BREAKS or not w["t"]) and cur:
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
    nxt = min([nxt] + [a for a, _ in windows if a > gs])
    ge = max(min(g[-1]["e"] + 0.25, nxt, DURATION - 0.04), gs + 0.1)
    spans = []
    for w in g:
        cls = "w key" if w["t"] in KEYWORDS else "w"
        spans.append(f'<span class="{cls}" id="cw{w["i"]}">{html.escape(w["t"])}</span>')
    cap_html.append(f'    <div id="cg{gi}" class="clip grp" data-start="{gs:.3f}" data-duration="{ge - gs:.3f}">'
                    f'<div class="line">{" ".join(spans)}</div></div>')
    cap_js.append(f'tl.fromTo("#cg{gi} .line", {{opacity: 0, y: 12, scale: 0.96}}, '
                  f'{{opacity: 1, y: 0, scale: 1, duration: 0.14, ease: "power2.out"}}, {gs:.3f});')

captions = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    .grp {{ position: absolute; left: 0; width: 100%; top: 1180px; height: 90px; overflow: visible;
           display: flex; align-items: center; justify-content: center; }}
    .line {{ width: 100%; padding: 0 90px; text-align: center; font-family: Inter, sans-serif;
            font-weight: 800; font-size: 50px; line-height: 1.1; color: #FFFFFF; letter-spacing: -0.01em;
            text-shadow: 0 0 3px rgba(0,0,0,.7), 0 3px 14px rgba(0,0,0,.6); }}
    .w {{ display: inline-block; }}
    .key {{ color: {Y}; }}
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

TITLE_END = 4.9
title = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; }}
    #t-kicker {{ position: absolute; left: 0; width: 100%; top: 1180px; display: flex; justify-content: center; }}
    #t-kicker span {{ font-family: Inter, sans-serif; font-weight: 800; font-size: 38px; color: #111;
                     background: #FFFFFF; padding: 12px 30px 12px 26px; border-radius: 16px;
                     box-shadow: 0 6px 24px rgba(0,0,0,.35); letter-spacing: -0.01em; }}
    #t-kicker i {{ display: inline-block; width: 22px; height: 22px; border-radius: 6px; background: {Y};
                  margin-right: 14px; vertical-align: -2px; }}
  </style>
  <div id="root" data-composition-id="title" data-width="1080" data-height="1920">
    <div id="t-kicker" class="clip" data-start="0" data-duration="{TITLE_END}"><span><i></i>{TITLE_TEXT}</span></div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#t-kicker span", {{ opacity: 0, y: 20, scale: 0.9 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(2)" }}, 0.05);
    tl.to("#t-kicker span", {{ opacity: 0, y: 14, duration: 0.22, ease: "power2.in" }}, {TITLE_END - 0.28});
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
      #blocks {{ position: absolute; inset: 0; z-index: 2; }}
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
      <div id="blocks" data-composition-id="blocks" data-composition-src="compositions/blocks.html"
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
for old in ("compositions/overlays.html",):
    if os.path.exists(os.path.join(HF, old)):
        os.remove(os.path.join(HF, old))
for name, txt in (("compositions/captions.html", captions), ("compositions/blocks.html", blocks),
                  ("compositions/title.html", title), ("index.html", index)):
    open(os.path.join(HF, name), "w").write(txt)
# every word that is on screen (blocks + subtitles), for verify.py
shown = [{"t": text(i), "s": round(wstart(i), 3), "e": words[i]["e"]} for i in sorted(in_block) if text(i)]
shown += [{"t": w["t"], "s": w["s"], "e": w["e"]} for g in groups for w in g]
shown.sort(key=lambda w: w["s"])
json.dump([[w] for w in shown], open(os.path.join(HF, "assets/caption_groups.json"), "w"), ensure_ascii=False, indent=1)
print(len(groups), "subtitle groups,", len(BLOCKS), "kinetic blocks,", len(CUTOUTS), "cutouts")
