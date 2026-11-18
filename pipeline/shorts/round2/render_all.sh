#!/bin/bash
# render all round 2/3 Shorts sequentially, then normalize loudness
cd /home/claude/shorts/round2
python3 - <<'PY' > jobs.txt
import json
for k, r in enumerate(json.load(open('rows.json'))):
    fn = f"R{r['round']}_{r['slug']}.mp4"
    print('\t'.join([r['slug'], str(r['start']), str(r['end']), fn, r['accent']] + r['hook']))
PY
while IFS=$'\t' read -r slug s e fn acc h1 h2; do
  [ -f "out/$fn" ] && continue
  python3 /home/claude/scripts/make_short_v2.py "$slug" "$s" "$e" "raw_$fn" "$h1" "$h2" --accent "$acc" >> render.log 2>&1 \
    && bash /home/claude/scripts/norm_short.sh "raw_$fn" "out/$fn" >> render.log 2>&1 && rm -f "raw_$fn" \
    || echo "FAIL $fn" >> render.log
  echo "$(date +%H:%M:%S) $fn" >> progress.log
done < jobs.txt
echo ALLDONE >> progress.log
