#!/bin/bash
# usage: render_song.sh SLUG   (needs lyrics_final.json, cfg.json, cover.png, song_14.m4a)
# single pass: renderer pipes into x264 medium CRF 20 with a VBV cap sized for < 30 MiB
K=$1
D=/home/claude/songs/$K
cd $D
TITLE=$(python3 -c "import json;print(json.load(open('cfg.json'))['title'])")
FN=$(python3 -c "import re,sys;t=sys.argv[1];print(re.sub(r'[^A-Za-z0-9]+','_',t.replace(\"'\",'')).strip('_'))" "$TITLE")
DUR=$(cat dur.txt)
VB=$(python3 -c "d=float('$DUR'); v=int((29.0*1048576*8*0.96)/d/1000 - 160 - 8); print(max(300, min(v, 900)))")
mkdir -p small
echo "$(date +%H:%M:%S) render start (cap ${VB}k)" >> pipeline.log
RENDER_PRESET=faster RENDER_CRF=20 RENDER_MAXRATE=$VB SONG_CFG=$D/cfg.json nice -n 5 python3 /home/claude/scripts/render.py lyrics_final.json small/v.mp4 > render.log 2>&1 < /dev/null
echo "$(date +%H:%M:%S) render done" >> pipeline.log
ffmpeg -nostdin -v error -y -i small/v.mp4 -i song_14.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart -metadata title="$TITLE (Remastered)" -metadata artist="Zachary Patzer" "/home/claude/out/${FN}_Lyric_Video.mp4"
SZ=$(stat -c %s "/home/claude/out/${FN}_Lyric_Video.mp4")
echo "$(date +%H:%M:%S) encoded ${FN}_Lyric_Video.mp4 $SZ bytes" >> pipeline.log
rm -f small/v.mp4
if [ "$SZ" -gt 31457280 ]; then echo "TOO BIG $SZ" >> pipeline.log; else echo VIDEO_DONE > video.ok; fi
