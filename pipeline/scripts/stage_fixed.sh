#!/bin/bash
# Stage fixed videos into the repo: check each, copy over the old file (and cover), commit + push.
# usage: stage_fixed.sh qh FILE...      (quick-hooks: normalize from /home/claude/qh_out first)
#        stage_fixed.sh full FILE...    (R2/R3/Story from /home/claude/fb_out)
# Prints the commit SHA on the last line, for immutable raw URLs.
set -e
cd /home/claude/zachary-shorts
kind=$1; shift
for f in "$@"; do
  if [ $kind = qh ]; then
    src=/home/claude/qh_out/final/$f; dst=shorts/qh/$f
    [ -s $src ] || bash pipeline/scripts/norm_short.sh /home/claude/qh_out/$f $src </dev/null >/dev/null
    cp /home/claude/qh_out/${f%.mp4}_cover.jpg shorts/qh/
  else
    src=/home/claude/fb_out/$f
    dst=$(grep -P "/${f}\t" pipeline/shorts/fullbleed_jobs.tsv | cut -f1)
    # cover for posts: frame at 1.5 s (text fully faded in)
    case $dst in shorts/story/*) ffmpeg -nostdin -v error -y -ss 1.5 -i $src -frames:v 1 -q:v 2 ${dst%.mp4}_cover.jpg ;; *) ffmpeg -nostdin -v error -y -ss 2 -i $src -frames:v 1 -q:v 2 ${dst%.mp4}_cover.jpg ;; esac
  fi
  python3 pipeline/scripts/check_platform.py $src $dst </dev/null >&2
  cp $src $dst; mkdir -p $(dirname $src)/staged; mv $src $(dirname $src)/staged/
  git add -f $dst ${dst%.mp4}_cover.jpg 2>/dev/null || git add -f $dst
done
git commit -q -m "Platform-pass versions: $*

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0174qJW34DEAtvz1cyBvbS9o"
git fetch -q origin main && git rebase -q origin/main && git push -q origin HEAD:main
git rev-parse HEAD
