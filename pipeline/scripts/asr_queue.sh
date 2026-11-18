#!/bin/bash
# waits for each song's vocals.wav, then runs ASR on the mix and on the vocals
cd /home/claude/songs
while IFS=$'\t' read -r n slug f title; do
  while [ ! -f "$slug/vocals.wav" ]; do sleep 20; done
  [ -f "$slug/trans_voc.txt" ] && continue
  /home/claude/scripts/asr.sh /home/claude/songs/$slug mix >> asr_progress.log 2>&1
  /home/claude/scripts/asr.sh /home/claude/songs/$slug voc >> asr_progress.log 2>&1
  echo "$slug ASRDONE $(date +%H:%M:%S)" >> asr_progress.log
done < list.tsv
echo ALLASR >> asr_progress.log
