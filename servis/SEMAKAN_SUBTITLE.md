# Semakan subtitle

- perkataan subtitle: 305, perkataan transcribe semula: 329
- padanan tepat: 256/305 (83.9%)
- purata beza masa highlight: 0.023s; >0.25s: 6 perkataan

## Beza teks (subtitle vs Whisper pada video akhir)

| masa | jenis | subtitle | whisper |
|---|---|---|---|
| 0.16s | replace | geng-geng | jengan |
| 1.18s | insert | — | kan, |
| 3.04s | replace | imaginasi hampa | imajinasi Ampua |
| 5.70s | replace | ada-ada ping-pong ping-pong sendirilah | nak ada, aduh, pimpong lah, pimpong sendiri lah. |
| 9.52s | replace | mari sini | main sendiri tu |
| 10.42s | replace | hampa | Ampua |
| 13.12s | replace | apa | Ampua |
| 13.66s | replace | hampa | Ampua. |
| 16.02s | replace | hampa | Ampua |
| 16.90s | replace | hampa | Ampua |
| 21.36s | replace | mentua | betul kan. |
| 24.10s | replace | hampa | Ampua |
| 25.60s | replace | hampa | Ampua |
| 26.26s | replace | je | aje |
| 29.64s | replace | dulu sekali | dulu sekali |
| 38.52s | replace | urut pelik-pelik | uruk pelik -pelik |
| 42.84s | replace | barang-barang | Barang ambar |
| 49.04s | replace | kawasan | kuasa |
| 52.54s | replace | kawasan | kuasa |
| 54.68s | insert | — | Buat |
| 61.68s | replace | servis | service |
| 68.30s | replace | hampa | Untuk Ampua |
| 68.66s | replace | servis | Service |
| 70.46s | replace | hampa | Ampua |
| 71.34s | replace | ribu-ribu | Ribu -ribu |
| 72.76s | replace | kenduri | kenuri |
| 74.30s | replace | servis | service |
| 75.50s | replace | diri sendiri hampa | diri sendiri Ampua |
| 81.60s | replace | hampa shockwave | Ampua Shopee |
| 82.50s | replace | rm40 | Empat puluh ringgit |
| 84.08s | replace | mana-mana | mana -mana |
| 85.68s | replace | rm40 | Empat puluh ringgit |
| 88.16s | replace | hampa | Ampun |
| 89.14s | replace | bekam | Bekar |
| 90.32s | replace | urut | uang |
| 91.06s | replace | satu je | satu je Ok |
| 91.64s | replace | servis | sebih |
| 93.32s | replace | servis | sebih |
| 93.90s | replace | apa | Ampun |
| 95.90s | replace | hampa | Ampun |
| 96.36s | replace | booking hampa | buka Ampun |
| 101.20s | replace | hampa | ubah Bila boleh slot |

## Highlight lari >0.25s

| masa | perkataan | beza (s) |
|---|---|---|
| 54.68 | shockwave | -0.66 |
| 73.50 | kali | +0.52 |
| 91.26 | kita | -0.50 |
| 101.46 | bila | -0.80 |
| 101.92 | ada | -0.58 |
| 102.12 | slot | -0.48 |

## Nota semakan

- **Ketepatan selepas ambil kira loghat: 291/308 = 94.5%.** Whisper sentiasa dengar "hampa" (loghat utara) sebagai "Ampua/Ampun", "servis" sebagai "service/sebih", "rm40" sebagai "empat puluh ringgit", "kawasan" sebagai "kuasa", "kenduri" sebagai "kenuri". Semua tu dianggap betul.
- Frasa yang tertutup tetingkap blok kinetic pada render pertama (tak ada benda tu, dekat kawasan situ, sama dia balik, dekat kenduri, tak jumpa dekat mana-mana, aku bagi, salah satu je) dah dikembalikan. Tambah juga perkataan yang tertinggal: "dulu sekali", "diri sendiri", "satu je", "buat (shockwave)".
- Yang sengaja dikekalkan walaupun Whisper lain:
  - "itu yang ada-ada ping-pong": "aduh" ialah sebutan "ada-ada", disahkan dengan snippet beam 10.
  - "mari sini" (bukan "main sendiri tu") dan "mak mentua" (bukan "mak betul"): ikut transcript klip asal, sebab snippet pada video akhir keluar halusinasi.
  - "booking" (bukan "buka"): klip asal jelas "booking".
- "bila boleh slot" dekat hujung ialah halusinasi Whisper (perkataan diulang). Highlight lari pada 101–102s datang dari situ, bukan dari subtitle.
- "kan" (1.2s) dan "ok" (91s) sengaja tak dipapar sebab filler.
- Frasa kurang pasti (Whisper dengar sama di semua transcript): "urut **pasok**", "**top belakang**", "**lajak rapi**".
