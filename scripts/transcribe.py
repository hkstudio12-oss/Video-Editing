"""Transcribe clips with faster-whisper (word timestamps). Usage: transcribe.py OUT_JSON FILE..."""
import sys, json, os, subprocess
import numpy as np

def load(f):
    raw = subprocess.run(['ffmpeg','-v','error','-i',f,'-ac','1','-ar','16000','-f','s16le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32)/32768.0
from faster_whisper import WhisperModel
model = WhisperModel(os.environ.get("WHISPER_MODEL", "large-v3"), device="cpu", compute_type="int8", cpu_threads=4)
out = {}
for f in sys.argv[2:]:
    segs, info = model.transcribe(load(f), language=os.environ.get("LANG_CODE", "ms"), word_timestamps=True,
                                  vad_filter=False, beam_size=5, condition_on_previous_text=False,
                                  initial_prompt="Umm, aa, err, macam, so, okay.")
    words = []
    for s in segs:
        for w in s.words:
            words.append({"w": w.word, "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 3)})
    out[os.path.basename(f)] = {"lang": info.language, "lp": info.language_probability, "words": words}
    print(os.path.basename(f), info.language, round(info.language_probability, 2), "".join(x["w"] for x in words), flush=True)
json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
