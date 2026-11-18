#!/bin/bash
# usage: drive_build.sh SLUG "glow,particles,tint,speed,gain"  -> refine, cover, prep, render, qc (Drive versions)
S=$1; P=$2; D=/home/claude/songs/$S
cd $D || exit 1
[ -f vocals16.wav ] || ffmpeg -nostdin -v error -y -i vocals.wav -ac 1 -ar 16000 vocals16.wav
python3 /home/claude/scripts/refine.py aligned.json lyrics_final.json vocals16.wav > refine.log 2>&1
cp -n /home/claude/zachary-shorts/pipeline/drive_versions/scenes/$S.jpg scene_src.jpg
mkdir -p /home/claude/covers
[ -f /home/claude/covers/x4_$S.png ] || SLUG=$S python3 /home/claude/scripts/cover_generic.py /home/claude/covers/x4_$S.png > cover.log 2>&1
python3 - "$S" "$P" <<'PY'
import sys
s,p=sys.argv[1:3]; g,e,t,sp,ga=p.split(',')
f='/home/claude/scripts/prep_song.py'; x=open(f).read()
if f"'{s}'" not in x:
    x=x.replace("    'things_break_people_rebuild':",f"    '{s}': ('{g}', '{e}', '{t}', {sp}, {ga}),\n    'things_break_people_rebuild':",1); open(f,'w').write(x)
PY
UPL=$D python3 /home/claude/scripts/prep_song.py $S > prep.log 2>&1
bash /home/claude/scripts/render_song.sh $S
TITLE=$(python3 -c "import json;print(json.load(open('cfg.json'))['title'])")
FN=$(python3 -c "import re,sys;t=sys.argv[1];print(re.sub(r'[^A-Za-z0-9]+','_',t.replace(\"'\",'')).strip('_'))" "$TITLE")
mkdir -p /home/claude/out/drive /tmp/qc/$S
mv /home/claude/out/${FN}_Lyric_Video.mp4 /home/claude/out/drive/${FN}_Drive_Lyric_Video.mp4 2>/dev/null
ln -sf /home/claude/out/drive/${FN}_Drive_Lyric_Video.mp4 /home/claude/out/${FN}_Lyric_Video.mp4
QC_DIR=/tmp/qc/$S python3 /home/claude/scripts/qc.py $S > qc.log 2>&1
rm -f /home/claude/out/${FN}_Lyric_Video.mp4
echo "$S BUILD_DONE $(tail -1 qc.log | head -c 0)$(grep -o 'size.*' qc.log)" >> /home/claude/songs/build.log
