"""Cut the talking-head footage into one 1080x1920 @25fps edit.

Usage: edit.py SRC_DIR WORK_DIR OUT.mp4

Each segment below is a hand-picked range (source seconds) chosen from the
Whisper transcript: fillers ("aa", "err"), test takes and repeated sentences
are simply left out. Inside each kept range, silences are detected with
ffmpeg silencedetect and shortened, so long pauses disappear too.
"""
import json, os, re, subprocess, sys

FPS = 25
W, H = 1080, 1920

# (clip, start, end, mode)  mode: talk = tight pauses, action = keep breathing room
SEGMENTS = [
    # hook
    ("IMG_0525", 1.98, 6.35, "talk"),    # macam roh saya dah pergi, datang balik
    # problem
    ("IMG_0523", 21.00, 38.60, "talk"),  # kalau kita yang macam saya ... untuk treatment ni
    ("IMG_0531", 9.15, 11.82, "talk"),   # rasa kebas kat pinggang ke, sengal kat lutut
    # treatment
    ("IMG_0520", 0.00, 3.30, "talk"),    # okay, tarik nafas. lepas
    ("IMG_0519", 26.50, 33.30, "action"),# neck crack + reaction
    ("IMG_0517", 8.40, 9.68, "talk"),    # aduh, dah meletup dah
    ("IMG_0522", 37.80, 45.50, "talk"),  # ya allah sedapnya ... rasa gila dia tarik
    ("IMG_0522", 53.20, 60.25, "talk"),  # ini skill baru, tak pernah buat ni, sedap ni
    # result
    ("IMG_0523", 10.40, 16.90, "talk"),  # tarik, tegang, bila letup tu, puas, super puas
    ("IMG_0525", 19.30, 23.45, "talk"),  # ya allah, daripada sini, sini, sampai sini
    ("IMG_0525", 31.40, 33.10, "talk"),  # korang memang dahsyat
    ("IMG_0525", 39.30, 42.15, "talk"),  # sumpah korang kena try sekali seumur hidup
    ("IMG_0531", 17.40, 25.62, "talk"),  # tapi bila bangun tu okay lah ... 10 per 10
    # CTA
    ("IMG_0529", 7.60, 15.95, "talk"),   # korang kena cuba je datang ... bawah rm50
    ("IMG_0529", 21.20, 23.60, "talk"),  # korang akan menyesal tak datang
    ("IMG_0529", 26.25, 28.75, "talk"),  # korang mesti akan datang lagi, percayalah
    ("IMG_0529", 45.95, 47.20, "talk"),  # super best
]

MODES = {  # min silence to shorten, padding kept each side of speech
    "talk": dict(min_gap=0.28, pad=0.09),
    "action": dict(min_gap=0.80, pad=0.15),
}


def silences(path):
    out = subprocess.run(
        ["ffmpeg", "-nostats", "-i", path, "-af",
         "highpass=f=100,silencedetect=noise=-38dB:d=0.2", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return list(zip(st, en))


def q(t):  # snap to frame grid so audio and video pieces stay in sync
    return round(t * FPS) / FPS


def pieces_for(seg, sil):
    clip, a, b, mode = seg
    p = MODES[mode]
    keep, cur = [], a
    for s, e in sil:
        if e <= a or s >= b:
            continue
        s, e = max(s, a), min(e, b)
        if e - s < p["min_gap"]:
            continue
        cut0 = s + p["pad"] if s > a else a
        cut1 = e - p["pad"] if e < b else b
        if cut0 > cur:
            keep.append((cur, cut0))
        cur = max(cur, cut1)
    if b > cur:
        keep.append((cur, b))
    out = []
    for x, y in keep:
        x, y = q(x), q(y)
        if y - x >= 0.12:
            out.append((clip, x, y))
    return out


def main():
    src, work, out = sys.argv[1:4]
    os.makedirs(work, exist_ok=True)
    sil_cache = {}
    pieces = []
    for seg in SEGMENTS:
        f = os.path.join(src, seg[0] + ".MOV")
        if f not in sil_cache:
            sil_cache[f] = silences(f)
        pieces += pieces_for(seg, sil_cache[f])

    vlist, alist, edl, t = [], [], [], 0.0
    for i, (clip, x, y) in enumerate(pieces):
        f = os.path.join(src, clip + ".MOV")
        d = y - x
        v = os.path.join(work, f"v{i:03d}.mp4")
        a = os.path.join(work, f"a{i:03d}.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{x:.3f}", "-i", f, "-t", f"{d:.3f}",
                        "-an", "-vf", f"fps={FPS},scale={W}:-2:flags=lanczos,crop={W}:{H},setsar=1",
                        "-frames:v", str(round(d * FPS)),
                        "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", v], check=True)
        fade = min(0.012, d / 4)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{x:.3f}", "-i", f, "-t", f"{d:.3f}",
                        "-vn", "-ac", "2", "-ar", "48000",
                        "-af", f"afade=t=in:d={fade},afade=t=out:st={d - fade:.4f}:d={fade},apad=whole_dur={d:.3f}",
                        a], check=True)
        vlist.append(v); alist.append(a)
        edl.append({"clip": clip, "src_in": x, "src_out": y, "out_in": round(t, 3), "out_out": round(t + d, 3)})
        t += d

    for name, lst in (("v.txt", vlist), ("a.txt", alist)):
        with open(os.path.join(work, name), "w") as fh:
            fh.writelines(f"file '{p}'\n" for p in lst)
    vcat = os.path.join(work, "video_cat.mp4")
    acat = os.path.join(work, "audio_cat.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "v.txt"),
                    "-c", "copy", vcat], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "a.txt"),
                    "-af", "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", acat], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vcat, "-i", acat, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    json.dump(edl, open(os.path.splitext(out)[0] + ".edl.json", "w"), indent=1)
    print(f"{len(pieces)} pieces, {t:.2f}s -> {out}")


if __name__ == "__main__":
    main()
