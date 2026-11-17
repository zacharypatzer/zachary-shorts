# Zachary Patzer: lyric-video and Shorts pipeline (backup)

This folder holds everything needed to rebuild the production setup in a fresh workspace: scripts, lyrics, timings, fonts, the portrait and the finished thumbnails.

It does **not** hold any audio. To make anything with sound, the song's MP3 or WAV is needed again.

## Restore in a new session

```bash
git clone https://github.com/zacharypatzer/zachary-shorts /home/claude/zachary-shorts
bash /home/claude/zachary-shorts/pipeline/restore.sh   # copies files back to /home/claude/... and installs tools
```

All scripts use absolute paths under `/home/claude/` (`scripts/`, `songs/<slug>/`, `shorts/`, `kit/`, `fonts/gfonts/`, `out/`). `restore.sh` puts everything back in those places.

## Tools (downloaded by restore.sh)

| What | Where it lives | Source |
|---|---|---|
| sherpa-onnx prebuilt CLI | `/home/claude/sherpa/bin` | github.com/k2-fsa/sherpa-onnx releases (linux-x64 shared) |
| Spleeter 2-stem ONNX | `/home/claude/models/sherpa-onnx-spleeter-2stems-fp16` | sherpa-onnx `source-separation-models` release |
| Parakeet TDT 0.6b v2 int8 (ASR) | `/home/claude/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8` | sherpa-onnx `asr-models` release |
| Real-ESRGAN general x4v3 | `/home/claude/models/esr/realesr-general-x4v3.pth` | github.com/xinntao/Real-ESRGAN releases (cover upscaling only) |
| Python | numpy, scipy, pillow, opencv-python-headless, onnxruntime | pip (`--break-system-packages`) |
| ffmpeg | system | apt or a static build |

## New song → full package

1. Put the song in `songs/list.tsv` (`n<TAB>slug<TAB>file<TAB>Title`) and convert it to `songs/<slug>/stereo44.wav`. Use 44.1 kHz stereo.
2. `LIST=<one-row tsv> scripts/pipeline_one.sh`: Spleeter vocal separation, then ASR on the mix and on the vocals.
3. Write `songs/<slug>/lyrics.txt` as sung. A blank line starts a new section, and `~` marks an instrumental gap (shown as dots).
4. `scripts/align.py` → `scripts/refine.py` → `lyrics_final.json` (word timings).
5. Add a palette entry to `PAL` in `scripts/prep_song.py`, then run `scripts/render_song.sh` and `scripts/qc.py`.
   - Output: a 1080×1920 karaoke video at -14 LUFS, under 30 MiB.
6. Cover: copy `scripts/cover_lions_heart.py` and change it.
   - Every cover has the portrait `assets/face_src.jpg` in the series position, a unique scene, and a unique title font and color.
   - "ZACHARY PATZER" goes at the top.
7. Thumbnail: run `scripts/thumbs.py` (1280×720) after adding the song's `S` entry.
8. Text: `pkg/texts.py`.
   - YouTube title: `Song (Remastered) by Zachary Patzer - Official Lyric Video`.
   - Tags must be under 500 characters, and the description under 5,000 characters with a LYRICS placeholder.
   - DistroKid lyrics: no tags, no end punctuation, exactly as sung.
   - Facebook post: no engagement bait, and end with a real question.

## Shorts

- `scripts/make_short_v2.py SLUG START END OUT "hook1" "hook2" --accent #hex`, then `scripts/norm_short.sh in out` (≈ -14 LUFS).
- Round 2/3 definitions are in `shorts/round2/` (`clips.py` → `resolve.py` → `rows.json`; `render_all.sh`; `posts2.json`; `push_batch.sh`).
- Hosting: finished Shorts go in `shorts/` of this repo. Metricool reads `https://raw.githubusercontent.com/zacharypatzer/zachary-shorts/main/shorts/<file>`.

## Scheduling (Metricool MCP)

- **Account:** blogId `7494992`, timezone `America/Los_Angeles`. Posts go out daily at 17:30.
- **Providers:** youtube (type `short`, MUSIC), tiktok (needs `tiktokData.title`), instagram (type `REEL`) and threads (`threadsData: {}`, connected Oct 21, 2026). Facebook is not connected; that was his choice.
- **Plan:** Metricool paid plan (upgraded Oct 21, 2026). He chose to stay at 1 Short a day until real stats show what works.
- **AI disclosure is always on:** `tiktokData.isAigc`, `instagramData.isAiGenerated` and `youtubeData.isAiGeneratedContent` are all set to true.
- **Media:** must be a public URL. Metricool re-hosts it when the post is created.
- **Editing:** `updateScheduledPost` changes the post id (the uuid stays the same). The API has no delete.
- **Already scheduled:**
  - Round 1: Oct 18–Nov 11, 2026.
  - Rounds 2 and 3: Nov 12–Dec 31, 2026.

## Preferences

- His face goes on every cover.
- Nothing preachy.
- Give honest ratings.
- Put copy-ready text in boxes.
- Don't redo finished songs. He can't afford more changes.
- Keep his physical effort to a minimum and make reasonable decisions without asking.
- Never touch the 25 published lyric videos.

## New song lyrics
Before he runs any new song in Suno: run `python3 scripts/lyric_check.py draft.txt "Title" songs --style style.txt --exclude exclude.txt` (FIX list must be empty), then walk every box in `SONG_CHECKLIST.md`.

## Nov 2026 quick-hook batch in the 5:30 PM slot
Approved by Zachary Nov 17, 2026. 14 new "leaving something behind" quick-hooks (`qh/plan_nov.py`, rendered by `qh/batch_nov.py`, files `shorts/qh/QH_*_L1/L2.mp4`), all ending on "Send this to someone WHO NEEDS IT."
They post at 5:30 PM every other day, Nov 19 - Dec 15 (payloads in `qh/sched_nov.json`). The 5:30 lyric Shorts they replaced were switched to drafts in Metricool (not deleted).
The in-between days keep the usual 5:30 lyric Shorts, so the weekly report can compare the two styles in the same slot.
Face fix (Nov 17): the 4x-upscaled cover face looks waxy/clay. `scripts/real_face_cover.py SLUG` pastes his real portrait (assets/face_src.jpg) onto `qh/covers4x/SLUG.png` -> `qh/covers_real/SLUG.png`; `batch_nov.py` uses those. The scheduled Nov batch uses the `_rf` files.
Nov 17: the 29 remaining 3 PM quick-hooks (Nov 19 - Dec 30, from `qh/plan.py`) were re-rendered on the real-portrait covers with `qh/batch_rf.py` (files `shorts/qh/QH_*_[ABC]_rf.mp4`) and their Metricool posts point at those now; list in `qh/fix_rf_posts.tsv`. The 3 PM Shorts for the six new songs (`shorts/new6/QN_*`) already used the real portrait.
