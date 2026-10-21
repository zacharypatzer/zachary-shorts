#!/bin/bash
# normalize a Short's audio to about -14 LUFS (true peak <= -1 dBTP), video stream copied
f=$1; out=$2
meas() { ffmpeg -nostdin -hide_banner -i "$1" -af ebur128=peak=true -f null - 2>&1 | tail -14; }
r=$(meas "$f"); I=$(echo "$r" | grep "I:" | awk '{print $2}')
g=$(python3 -c "print(round(-14.0 - $I + 0.2, 2))")
for lim in 0.89 0.84 0.79; do
  ffmpeg -nostdin -v error -y -i "$f" -map 0:v -map 0:a -c:v copy -af "aformat=sample_fmts=flt,volume=${g}dB,alimiter=limit=${lim}:attack=5:release=60:level=disabled" -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$out"
  r2=$(meas "$out"); I2=$(echo "$r2" | grep "I:" | awk '{print $2}'); P2=$(echo "$r2" | grep "Peak:" | awk '{print $2}')
  python3 -c "import sys; sys.exit(0 if $P2 <= -1.0 else 1)" && break
done
echo "$I -> $I2 LUFS, peak $P2  $(basename $out)"
