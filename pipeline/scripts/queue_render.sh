#!/bin/bash
# renders any song folder that has ready.flag and no video.ok, in list order
cd /home/claude/songs
while true; do
  did=0
  while IFS=$'\t' read -r n k f title; do
    [ -f $k/ready.flag ] || continue
    [ -f $k/video.ok ] && continue
    mkdir $k/render.lock 2>/dev/null || continue
    echo "$(date +%H:%M:%S) render $k" >> queue_render.log
    bash /home/claude/scripts/render_song.sh $k >> queue_render.log 2>&1 < /dev/null
    echo "$(date +%H:%M:%S) finished $k" >> queue_render.log
    did=1; break
  done < list.tsv
  if [ $did = 0 ]; then
    [ -f stop_render ] && break
    sleep 20
  fi
done
