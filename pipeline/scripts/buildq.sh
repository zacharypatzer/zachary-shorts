#!/bin/bash
# processes /home/claude/songs/buildq.txt lines "SLUG PALETTE" one at a time; marks done in buildq.done
Q=/home/claude/songs/buildq.txt; DN=/home/claude/songs/buildq.done; touch $Q $DN
while true; do
  next=$(grep -vxFf $DN $Q | head -1)
  if [ -z "$next" ]; then sleep 20; continue; fi
  set -- $next
  bash /home/claude/scripts/drive_build.sh $1 "$2" > /tmp/b_$1.log 2>&1
  echo "$next" >> $DN
done
