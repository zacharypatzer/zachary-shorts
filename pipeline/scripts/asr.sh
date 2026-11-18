#!/bin/bash
# usage: asr.sh SONGDIR mix|voc   -> SONGDIR/asr_<src>/asr_out.txt, words_<src>.json, trans_<src>.txt
D=$1; SRC=$2
cd $D
IN=stereo44.wav; [ "$SRC" = voc ] && IN=vocals.wav
W=asr_$SRC; rm -rf $W; mkdir -p $W
ffmpeg -nostdin -v error -y -i $IN -ar 16000 -ac 1 $W/full16.wav
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $W/full16.wav)
off=0
while python3 -c "import sys; sys.exit(0 if $off < $dur - 1 else 1)"; do
  ffmpeg -nostdin -v error -y -ss $off -t 10 -i $W/full16.wav $W/w_$(printf %04d $off).wav
  off=$((off+8))
done
M=/home/claude/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8
python3 /home/claude/scripts/wsasr.py $W/w_*.wav > $W/raw.txt 2>&1
python3 - $W <<'PY'
import json, sys, re
W = sys.argv[1]
lines = open(f'{W}/raw.txt').read().split('\n')
out = open(f'{W}/asr_out.txt', 'w'); n = 0
for i, l in enumerate(lines):
    if l.startswith('{"lang"') and i > 0 and re.search(r'w_\d+\.wav$', lines[i-1].strip()):
        try:
            d = json.loads(l)
        except Exception as e:
            print('bad json', lines[i-1]); continue
        p = lines[i-1].strip().replace('w_0', 'w_').replace('w_0', 'w_').replace('w_0', 'w_')
        p = re.sub(r'w_(\d+)', lambda m: 'w_%d' % int(m.group(1)), lines[i-1].strip())
        out.write(p + '\n' + json.dumps({'tokens': d['tokens'], 'timestamps': d['timestamps'], 'durations': d['durations']}) + '\n'); n += 1
out.write('ALLDONE\n'); out.close()
print('windows parsed', n)
PY
python3 /home/claude/scripts/asr_merge.py $W/asr_out.txt words_$SRC.json 8 10 1 > trans_$SRC.txt
rm -f $W/w_*.wav $W/full16.wav
echo "asr $SRC done $(wc -l < trans_$SRC.txt) lines"
