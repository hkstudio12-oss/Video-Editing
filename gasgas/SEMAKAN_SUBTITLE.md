# Semakan subtitle

- perkataan subtitle: 123, perkataan transcribe semula: 146
- padanan tepat: 104/123 (84.6%)
- purata beza masa highlight: 0.054s; >0.25s: 6 perkataan

## Beza teks (subtitle vs Whisper pada video akhir)

| masa | jenis | subtitle | whisper |
|---|---|---|---|
| 3.54s | insert | — | Kalau lepas, oh, oh, angin, |
| 6.50s | replace | dada | dah ada |
| 8.80s | replace | gerd | get, hmm, |
| 13.70s | replace | lembutkan | lembukkan |
| 16.16s | insert | — | Oh. |
| 17.34s | replace | lembutkan | lembukkan, |
| 20.36s | insert | — | Oh. |
| 25.18s | insert | — | Oh. Ufff Hehehehe |
| 28.56s | replace | fleksibel | flexible Kita |
| 30.06s | insert | — | tu |
| 32.68s | replace | pemulihan | pemulihankan |
| 35.38s | insert | — | Jadi |
| 37.32s | replace | ada | Barang -barang |
| 38.46s | replace | tahap | tarik |
| 40.30s | replace | gas-gas | gas -gas Hmm |
| 48.34s | insert | — | tu |
| 49.24s | replace | sakit-sakit | Sakit -sakit |
| 53.14s | replace | bangun-bangun | bangun -bangun |
| 53.94s | replace | terus rasa | Asal |
| 59.56s | replace | ketat-ketat | Ketat -ketat |
| 63.04s | replace | gas-gas | gas -gas |
| 64.28s | replace | al-mukmin | almumin |
| 65.22s | replace | kepala batas | Pulau Batah |
| 67.40s | replace | bye-bye | Bye -bye |

## Highlight lari >0.25s

| masa | perkataan | beza (s) |
|---|---|---|
| 17.18 | tak | +0.32 |
| 30.88 | jadi | +0.26 |
| 31.74 | bila | +0.88 |
| 43.46 | dia | -0.26 |
| 44.04 | punya | -0.28 |
| 45.32 | kesedapan | +0.66 |

## Nota semakan

- **Ketepatan selepas ambil kira ejaan Whisper: 111/123 = 90.2%.** "lembukkan" = lembutkan, "flexible" = fleksibel, "almumin" = al-mukmin, "get" = gerd, "tarik" = tahap. Baki beza kebanyakannya perkataan bersempang yang Whisper pecahkan ("sakit -sakit", "gas -gas", "bangun -bangun"), jadi sebenarnya sama.
- Dibetulkan selepas render pertama, ikut majoriti (render + klip asal large-v3):
  - buang "kita" dalam "sebab kalau tak lembutkan"
  - tambah "bye-bye" di hujung, yang sebelum ni tersorok dalam blok CTA
- "oh / uff / hehe / hmm" (bunyi sendawa, reaksi, ketawa) sengaja tak dipapar.
- Hook 0–3.5s ialah teks tajuk (bukan percakapan): *aku buat rawatan "GASGAS" buang angin dalam badan*.
- Kekal walaupun Whisper lain:
  - "dada ketat": klip asal jelas "dada"
  - "terus rasa fresh": klip asal, Whisper di video akhir dengar "asal"
  - "ada orang": Whisper dengar "barang-barang orang"
  - "**kepala batas**": Whisper dengar "Pulau Batah". Awak dah luluskan dalam preview.
- Highlight lari pada 31.7s dan 45.3s: Whisper regangkan perkataan merentasi jeda. Subtitle ikut masa perkataan dalam cut.

## Pembetulan render (subtitle bertindih & warna pudar)

- Punca: footage iPhone ni **HDR (HLG/BT.2020)**. HyperFrames auto-tukar render ke mod HDR. Dalam mod tu, kumpulan subtitle lama tak disembunyikan (jadi bertindih) dan semua teks jadi kelabu/pudar.
- Penyelesaian: `base.mp4` di-tone-map ke **SDR BT.709** sebelum render. Log render sekarang tulis "No HDR sources detected, rendering SDR".
- Teks atas dinding putih: tukar glow putih kepada **bayang gelap** (`LIGHT_BG = True`), dan serif italic kuning diberi stroke nipis supaya lebih tebal.
- Babak CTA: tambah jarak antara "area kepala batas pulau pinang" dan "WHATSAPP UNTUK BOOKING".
- Selepas render semula, ketepatan subtitle masih 90.2%.
