#!/bin/bash
# copy Drive-version text work (no audio) into the repo and push
R=/home/claude/zachary-shorts/pipeline
cd /home/claude/songs
for d in d_* o_*; do
  mkdir -p $R/songs/$d
  for f in lyrics.txt aligned.json lyrics_final.json win.json trans_mix.txt trans_voc.txt words_mix.json words_voc.json dur.txt cfg.json loudness.txt; do [ -f $d/$f ] && cp $d/$f $R/songs/$d/; done
done
cp /home/claude/songs/list.tsv $R/songs/list.tsv
for f in drive_build.sh buildq.sh drive_backup.sh prep_song.py; do cp /home/claude/scripts/$f $R/scripts/; done
cd /home/claude/zachary-shorts && git add -A pipeline >/dev/null && git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -qm "${1:-Drive versions: lyrics and timings progress}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01U2xS3WCUyx4vDFhZL6pXsf" && git -c push.negotiate=true push -q origin HEAD:main 2>&1 | tail -2; git log --oneline -1
