#!/bin/bash
# copy rendered Shorts not yet in the repo, commit and push in batches of 8
cd /home/claude/zachary-shorts
n=0
for f in /home/claude/shorts/round2/out/*.mp4; do
  b=$(basename "$f")
  [ -f "shorts/$b" ] && continue
  cp "$f" "shorts/$b"; git add "shorts/$b"; n=$((n+1))
  if [ $n -ge 8 ]; then
    git commit -q -m "Add $n Shorts

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01JpjghUPBhgRJYe4ctJKGPy" && git push -q origin HEAD 2>&1 | tail -2; n=0
  fi
done
if [ $n -gt 0 ]; then
  git commit -q -m "Add $n Shorts

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01JpjghUPBhgRJYe4ctJKGPy" && git push -q origin HEAD 2>&1 | tail -2
fi
ls shorts | wc -l
