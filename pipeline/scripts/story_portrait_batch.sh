#!/bin/bash
# Re-render all 50 Story Shorts on his real portrait (fullbleed_portrait.py) from the original
# card-style versions in git commit 6b25d7e. Overwrites shorts/story/*.mp4 + *_cover.jpg. Skips done ones.
cd /home/claude/zachary-shorts
SRC=/home/claude/story_orig; DONE=/home/claude/story_done; mkdir -p $SRC $DONE
grep story pipeline/shorts/fullbleed_jobs.tsv | while IFS=$'\t' read -r f slug style; do
  b=$(basename $f .mp4)
  [ -e $DONE/$b ] && continue
  title=$(awk -F'\t' -v s="$slug" '$2==s{print $4}' pipeline/songs/list.tsv)
  git show 6b25d7e:$f > $SRC/$b.mp4
  python3 pipeline/scripts/fullbleed_portrait.py $SRC/$b.mp4 $SRC/$b.new.mp4 story "$title" </dev/null || { echo "FAIL $b"; continue; }
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $SRC/$b.new.mp4)
  t=$(python3 -c "print(max(1, $d - 3))")
  ffmpeg -v error -y -ss $t -i $SRC/$b.new.mp4 -frames:v 1 -q:v 2 shorts/story/${b}_cover.jpg </dev/null
  mv $SRC/$b.new.mp4 $f && touch $DONE/$b && echo "done $b"
done
echo ALL_DONE
