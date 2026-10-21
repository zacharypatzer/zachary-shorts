#!/bin/bash
# chunked UVR vocal separation (20 s chunks, 18 s hop) for every song in list.tsv, in order
cd /home/claude/songs
HOP=18; M=1
while IFS=$'\t' read -r n slug f title; do
  [ -f "$slug/vocals.wav" ] && continue
  s0=$(date +%s); mkdir -p "$slug/sep"
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$slug/stereo44.wav")
  python3 -c "
d=$dur; i=0; print('# i st s hop')
while $HOP*i < d - 0.5:
    s=$HOP*i; print(i, max(0, s-$M), s, $HOP); i+=1" > "$slug/sep/chunks.txt"
  grep -v '^#' "$slug/sep/chunks.txt" | while read -r i st s hop; do
    [ -f "$slug/sep/v_$i.wav" ] && continue
    ffmpeg -nostdin -v error -y -ss $st -t 20 -i "$slug/stereo44.wav" "$slug/sep/in_$i.wav"
    /home/claude/sherpa/bin/sherpa-onnx-offline-source-separation --uvr-model=/home/claude/models/uvr.onnx --num-threads=2 \
      --input-wav="$slug/sep/in_$i.wav" --output-vocals-wav="$slug/sep/t_$i.wav" --output-accompaniment-wav="$slug/sep/a_$i.wav" > "$slug/sep/log_$i.txt" 2>&1 \
      && mv "$slug/sep/t_$i.wav" "$slug/sep/v_$i.wav"
    rm -f "$slug/sep/in_$i.wav" "$slug/sep/a_$i.wav"
  done
  python3 /home/claude/scripts/stitch.py "$slug" >> /home/claude/songs/sep_progress.log 2>&1
  echo "$slug $(( $(date +%s) - s0 ))s" >> /home/claude/songs/sep_progress.log
done < list.tsv
echo SEPDONE >> /home/claude/songs/sep_progress.log
