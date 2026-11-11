"""Re-transcribe the final render and compare it with the burned-in captions.

Usage: verify.py FINAL_TRANSCRIPT.json CAPTION_GROUPS.json REPORT.md
Reports word accuracy, every mismatch, and how far each caption word's
highlight time is from where Whisper hears that word in the final video.
"""
import json, re, sys, difflib

tx = json.load(open(sys.argv[1]))
tx = next(iter(tx.values()))["words"]
groups = json.load(open(sys.argv[2]))
cap = [w for g in groups for w in g]

norm = lambda s: re.sub(r"[^\w/]", "", s.lower())
A = [norm(w["t"]) for w in cap]
B = [norm(w["w"]) for w in tx]
sm = difflib.SequenceMatcher(a=A, b=B, autojunk=False)
lines, match, offs = [], 0, []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal":
        match += i2 - i1
        for k in range(i2 - i1):
            offs.append((cap[i1 + k]["s"] - tx[j1 + k]["s"], cap[i1 + k]["t"], cap[i1 + k]["s"]))
    else:
        lines.append(f"| {cap[i1]['s'] if i1 < len(cap) else tx[j1]['s']:.2f}s | {op} | "
                     f"{' '.join(w['t'] for w in cap[i1:i2]) or '—'} | {' '.join(w['w'].strip() for w in tx[j1:j2]) or '—'} |")
acc = match / len(A) * 100
big = [o for o in offs if abs(o[0]) > 0.25]
out = [f"# Semakan subtitle\n",
       f"- perkataan subtitle: {len(A)}, perkataan transcribe semula: {len(B)}",
       f"- padanan tepat: {match}/{len(A)} ({acc:.1f}%)",
       f"- purata beza masa highlight: {sum(abs(o[0]) for o in offs) / max(1, len(offs)):.3f}s; "
       f">0.25s: {len(big)} perkataan\n",
       "## Beza teks (subtitle vs Whisper pada video akhir)\n",
       "| masa | jenis | subtitle | whisper |", "|---|---|---|---|", *lines,
       "\n## Highlight lari >0.25s\n", "| masa | perkataan | beza (s) |", "|---|---|---|",
       *[f"| {s:.2f} | {t} | {d:+.2f} |" for d, t, s in big]]
open(sys.argv[3], "w").write("\n".join(out) + "\n")
print("\n".join(out[:4]))
