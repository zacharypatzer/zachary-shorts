#!/bin/bash
# Re-render R2/R3 + Story Shorts full-frame into $OUT (default /home/claude/fb_out), skipping finished ones.
cd /home/claude/zachary-shorts
OUT=${OUT:-/home/claude/fb_out}; mkdir -p $OUT
while IFS=$'\t' read -r f slug style; do
  o=$OUT/$(basename $f)
  [ -s $o ] && continue
  c=pipeline/qh/covers4x/$slug.png
  while [ ! -s $c ]; do sleep 20; done
  python3 pipeline/scripts/fullbleed.py $f $c $o.tmp.mp4 $style </dev/null && mv $o.tmp.mp4 $o && echo "done $f"
done < pipeline/shorts/fullbleed_jobs.tsv
