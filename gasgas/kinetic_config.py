"""Project data for scripts/build_kinetic.py -- rawatan "GasGas" (buang angin) testimonial."""
DURATION = 71.24  # ffprobe of assets/base.mp4 (68.24 s cut + 3.0 s held last frame)

FIX = {0: "", 1: "", 2: "", 3: "", 4: "",          # hook: patient's "oh.. oh.." (text hook instead)
       12: "dada", 36: "", 13: "", 19: "gerd", 30: "lembutkan", 38: "lembutkan", 46: "",
       59: "fleksibel", 60: "bila kita", 64: "", 80: "ada", 83: "tahap", 87: "gas-gas", 88: "",
       99: "sakit-sakit", 100: "", 104: "bangun-bangun", 105: "", 114: "ringan",
       117: "ketat-ketat", 118: "", 129: "gas-gas", 130: "", 133: "al-mukmin", 134: "",
       136: "kepala", 137: "batas", 138: "pulau", 140: "bye-bye", 141: ""}
BREAKS = {11, 16, 19, 22, 28, 33, 38, 41, 45, 50, 55, 59, 61, 63, 69, 73, 79, 84, 88, 92, 98, 102,
          107, 109, 111, 116, 122, 125, 130, 134, 139, 141}
KEYWORDS = {"angin", "gas-gas", "ketat", "dada", "detox", "demam", "sedap", "ringan", "fresh", "tekan",
            "lembutkan", "gerd", "al-mukmin"}
TITLE_TEXT = "testimoni rawatan gasgas"

# id, start, end, top(px), lines; line = (align, style s/b/i, px, [word idx] | [(literal, time)], colour)
BLOCKS = [
    # HOOK (patient lying on the table, no cutout: the matte of a lying person is unreliable)
    ("k1", 0.00, 3.50, 190, [("c", "s", 66, [("aku buat rawatan", 0.10)]),
                             ("c", "b", 300, [("“gasgas”", 0.55)], Y),
                             ("r", "i", 116, [("buang angin", 1.25)]),
                             ("l", "s", 66, [("dalam badan", 1.85)])]),
    ("k2", 3.50, 5.85, 200, [("l", "s", 62, [5, 6]), ("c", "b", 260, [7]), ("r", "i", 100, [8, 9, 10, 11])]),
    ("k3", 6.45, 9.45, 170, [("l", "s", 62, [12]), ("c", "b", 250, [14]), ("r", "i", 100, [15, 16]),
                             ("c", "s", 58, [17, 18, 19])]),
    ("k4", 13.55, 15.35, 170, [("l", "s", 62, [29]), ("c", "b", 220, [30]), ("r", "i", 100, [31, 32, 33])]),
    ("k5", 20.30, 21.65, 200, [("l", "s", 62, [47, 48]), ("c", "b", 260, [49]), ("r", "i", 100, [50])]),
    ("k6", 25.15, 28.85, 170, [("l", "s", 62, [51, 52, 53, 54]), ("c", "b", 240, [55]), ("r", "i", 96, [56, 57, 58, 59])]),
    ("k7", 33.50, 35.20, 190, [("l", "s", 62, [70, 71, 72]), ("c", "b", 280, [73], Y)]),
    ("k8", 37.30, 39.10, 190, [("l", "s", 62, [80, 81, 82, 83]), ("c", "b", 280, [84])]),
    ("k9", 39.10, 41.00, 190, [("l", "s", 62, [85, 86]), ("c", "b", 260, [87], Y)]),
    ("k10", 43.40, 48.30, 160, [("l", "s", 62, [89, 90]), ("r", "i", 110, [91, 92]), ("c", "b", 200, [93])]),
    ("k11", 49.05, 50.90, 190, [("c", "b", 220, [99]), ("r", "i", 120, [101, 102])]),
    ("k12", 52.50, 56.40, 150, [("l", "s", 56, [103, 104, 106, 107]), ("r", "i", 110, [108, 109]),
                                ("c", "b", 210, [110, 111])]),
    ("k13", 59.50, 61.15, 180, [("l", "s", 62, [117, 119, 120, 121]), ("c", "b", 260, [122])]),
    ("k14", 61.15, 63.55, 170, [("l", "s", 62, [123, 124, 125]), ("r", "i", 100, [126, 127, 128]),
                                ("c", "b", 250, [129], Y)]),
    ("k15", 63.55, DURATION, 90, [("l", "s", 58, [131, 132]), ("c", "b", 200, [133]),
                                   ("r", "i", 80, [135, 136, 137, 138, 139]),
                                   ("c", "s", 44, [("", 0)]),
                                   ("c", "b", 110, [("whatsapp untuk booking", 67.30)], G),
                                   ("r", "i", 80, [140])]),
]
# close-up selfies / therapist filling the top of frame: a cutout would hide the text, so all text sits in front
CUTOUTS = {}
LIGHT_BG = True  # white clinic walls: dark shadows instead of white glow
