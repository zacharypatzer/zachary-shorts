#!/bin/bash
# per song, in order: chunked Spleeter 2-stem separation (60 s chunks / 58 s hop, retried) -> stitch -> ASR on mix and vocals
cd /home/claude/songs
HOP=58; M=1
LOG=/home/claude/songs/pipe.log
while IFS=$'\t' read -r n slug f title; do
  if [ ! -f "$slug/vocals.wav" ]; then
    s0=$(date +%s); mkdir -p "$slug/sep"
    dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$slug/stereo44.wav")
    python3 -c "
d=$dur; i=0; print('# i st s hop')
while $HOP*i < d - 0.5:
    s=$HOP*i; print(i, max(0, s-$M), s, $HOP); i+=1" > "$slug/sep/chunks.txt"
    for attempt in 1 2 3; do
      grep -v '^#' "$slug/sep/chunks.txt" | while read -r i st s hop; do
        [ -f "$slug/sep/v_$i.wav" ] && continue
        ffmpeg -nostdin -v error -y -ss $st -t 60 -i "$slug/stereo44.wav" "$slug/sep/in_$i.wav"
        /home/claude/sherpa/bin/sherpa-onnx-offline-source-separation --spleeter-vocals=/home/claude/models/sherpa-onnx-spleeter-2stems-fp16/vocals.fp16.onnx --spleeter-accompaniment=/home/claude/models/sherpa-onnx-spleeter-2stems-fp16/accompaniment.fp16.onnx --num-threads=2 \
          --input-wav="$slug/sep/in_$i.wav" --output-vocals-wav="$slug/sep/t_$i.wav" --output-accompaniment-wav="$slug/sep/a_$i.wav" > "$slug/sep/log_$i.txt" 2>&1 \
          && mv "$slug/sep/t_$i.wav" "$slug/sep/v_$i.wav"
        rm -f "$slug/sep/in_$i.wav" "$slug/sep/a_$i.wav" "$slug/sep/t_$i.wav"
      done
    done
    need=$(grep -vc '^#' "$slug/sep/chunks.txt"); have=$(ls "$slug/sep" | grep -c '^v_')
    if [ "$need" = "$have" ]; then
      python3 /home/claude/scripts/stitch.py "$slug" >> $LOG 2>&1
      echo "$slug sep $(( $(date +%s) - s0 ))s $(date +%H:%M:%S)" >> $LOG
    else
      echo "$slug SEP FAILED $have/$need" >> $LOG; continue
    fi
  fi
  if [ ! -f "$slug/trans_voc.txt" ]; then
    s0=$(date +%s)
    /home/claude/scripts/asr.sh /home/claude/songs/$slug mix >> $LOG 2>&1
    /home/claude/scripts/asr.sh /home/claude/songs/$slug voc >> $LOG 2>&1
    echo "$slug ASRDONE $(( $(date +%s) - s0 ))s $(date +%H:%M:%S)" >> $LOG
  fi
done < "${LIST:-list.tsv}"
echo PIPEDONE >> $LOG
