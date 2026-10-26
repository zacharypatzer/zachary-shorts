#!/bin/bash
# Re-render all quick-hook Shorts (lighter edges) into $QH_OUT, then loudness-normalize into $QH_OUT/final
cd /home/claude/zachary-shorts/pipeline
export QH_OUT=${QH_OUT:-/home/claude/qh_out}; mkdir -p $QH_OUT/final
while pgrep -f fullbleed_batch.sh >/dev/null; do sleep 30; done
python3 qh/batch.py
for f in $QH_OUT/QH_*.mp4; do
  o=$QH_OUT/final/$(basename $f); [ -s $o ] || bash scripts/norm_short.sh $f $o
  cp -n ${f%.mp4}_cover.jpg $QH_OUT/final/ 2>/dev/null
done
echo QH ALL DONE
