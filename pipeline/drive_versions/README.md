# Drive versions: lyric videos for every song in "Zachary Song Backup"

Plan (Nov 16, 2026): every song in the Drive folder gets a complete lyric video, for follower perks / subscriber incentives (showing how ideas grow over time).

- `list.tsv`: the 28 unreleased takes to package (slug, file, title). Left out on purpose: Follow Along, Thank You for Joining, and the short Living 2 Die take (under 3 minutes).
- `cover_prompts.txt`: 23 cover prompts for those songs (one cover per song; repeat takes share it). Zachary makes each image and sends it back.
- Older takes of songs that already have covers reuse that song's cover with a version label; no new prompt needed.
- Words on screen must match what Suno actually sang; unclear spots get flagged for him to check by ear before rendering.

## Status (Nov 16, 2026, 1 AM)
- All 23 cover images received; 28 covers built (`covers_cfg/d_*.json`, scenes in `drive_versions/scenes/`, render with `SLUG=<slug> scripts/cover_generic.py`). He also made images for the two dropped songs (Follow Along bicycle road, Thank You for Joining open door) — unused.
- All 28 takes are transcribed (songs/d_*/trans_voc.txt, rebuilt by restore + pipeline_one if the workspace is fresh; MP3 ids in Drive).
- Next: lyrics as sung, one song at a time. Source = his written lyrics in past chats (mostly the Oct 2026 "Karaoke video with lyrics" chat) checked against Suno's vocal; flag unclear spots for him to check by ear before rendering. Do the sung songs first, fast rap songs last.
