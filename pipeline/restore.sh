#!/bin/bash
# Rebuild the production workspace from this backup: copies files back under /home/claude and downloads the tools.
# Safe to re-run: existing files are kept, downloads are skipped if present.
set -u
P=$(cd "$(dirname "$0")" && pwd); H=/home/claude
mkdir -p $H/{scripts,pkg,kit,shorts,songs,out,fonts/gfonts,models/esr,sherpa}
cp -rn $P/scripts/. $H/scripts/; cp -rn $P/pkg/. $H/pkg/; cp -rn $P/kit/. $H/kit/
cp -rn $P/shorts/. $H/shorts/; cp -rn $P/songs/. $H/songs/; cp -rn $P/out/. $H/out/
cp -rn $P/fonts/gfonts/. $H/fonts/gfonts/
cp -n $P/assets/face_src.jpg $H/songs/unfinished/face_src.jpg 2>/dev/null
mkdir -p /usr/share/fonts/opentype/inter /usr/share/fonts/truetype/google-fonts
cp -n $P/sysfonts/Inter*.otf /usr/share/fonts/opentype/inter/; cp -n $P/sysfonts/Lora-Variable.ttf /usr/share/fonts/truetype/google-fonts/
chmod +x $H/scripts/*.sh $H/shorts/round2/*.sh 2>/dev/null

pip install -q --break-system-packages numpy scipy pillow opencv-python-headless onnxruntime 2>/dev/null
command -v ffmpeg >/dev/null || (apt-get install -y -q ffmpeg >/dev/null 2>&1)

GH=https://github.com/k2-fsa/sherpa-onnx/releases/download
if [ ! -x $H/sherpa/bin/sherpa-onnx-offline-source-separation ]; then
  curl -sL $GH/v1.12.15/sherpa-onnx-v1.12.15-linux-x64-shared.tar.bz2 | tar xj -C /tmp && cp -r /tmp/sherpa-onnx-v1.12.15-linux-x64-shared/. $H/sherpa/
fi
[ -d $H/models/sherpa-onnx-spleeter-2stems-fp16 ] || curl -sL $GH/source-separation-models/sherpa-onnx-spleeter-2stems-fp16.tar.bz2 | tar xj -C $H/models
[ -d $H/models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8 ] || curl -sL $GH/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v2-int8.tar.bz2 | tar xj -C $H/models
[ -f $H/models/esr/realesr-general-x4v3.pth ] || curl -sL -o $H/models/esr/realesr-general-x4v3.pth https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth
echo "RESTORED. Audio is not in the backup: put each song's audio at songs/<slug>/stereo44.wav before rendering."
