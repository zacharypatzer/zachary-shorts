# Drive versions: lyric videos for every song in "Zachary Song Backup"

Plan (Nov 16, 2026): every song in the Drive folder gets a complete lyric video, for follower perks / subscriber incentives (showing how ideas grow over time).

- `list.tsv`: the 28 unreleased takes to package (slug, file, title). Left out on purpose: Follow Along, Thank You for Joining, and the short Living 2 Die take (under 3 minutes).
- `cover_prompts.txt`: 23 cover prompts for those songs (one cover per song; repeat takes share it). Zachary makes each image and sends it back.
- Older takes of songs that already have covers reuse that song's cover with a version label; no new prompt needed.
- Words on screen must match what Suno actually sang; unclear spots get flagged for him to check by ear before rendering.

## Status (Nov 16, 2026, 2 AM)
- 3 files are exact duplicates (True Strength (1), A New God Rises (1), "I feel the weight..." = Lone Wolf Rising), so 25 videos.
- Lyrics as sung done for all 25 (`songs/d_*/lyrics.txt`, timings in `aligned.json` / `lyrics_final.json`). Sheets came from past chats where they existed; the rest are from the vocal.
- Lines to check by ear: `REVIEW.md` (regenerate with `review/make_review.py` after edits).
- Drive MP3 file ids: `ids.tsv`.
- Build one song: `scripts/drive_build.sh SLUG "glow,particles,tint,speed,gain"` (cover, -14 LUFS audio, render, QC). Queue: add lines to `songs/buildq.txt`, run `scripts/buildq.sh`. Videos go to `/home/claude/out/drive/` (not in the repo: they contain audio).
- To fix a line: edit `songs/<slug>/lyrics.txt`, rerun `align.py lyrics.txt words_mix.json,words_voc.json[,win.json] aligned.json`, then rebuild.
