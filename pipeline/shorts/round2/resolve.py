import json, sys
sys.path.insert(0, '/home/claude/shorts/round2')
import importlib, clips; importlib.reload(clips)
C = clips.C
plan = {p['slug']: p for p in json.load(open('/home/claude/shorts/all24/plan.json'))}
plan['a_mile_an_hour'] = {'start': 101.6, 'end': 146.8, 'accent': '#5ec0ff', 'name': 'A Mile An Hour'}
plan['lions_heart'] = {'start': 45.9, 'end': 92.9, 'accent': '#ffc160', 'name': "Lion's Heart"}
rows = []
for slug, rnd, a, b, hook, title, quote, tags in C:
    d = json.load(open(f'/home/claude/songs/{slug}/lyrics_final.json'))
    L = [(it['words'][0]['s'], it['words'][-1]['e'], ' '.join(w['w'] for w in it['words'])) for it in d if 'words' in it]
    def find(spec, after=0):
        p, n = (spec.rsplit('#', 1) if '#' in spec else (spec, '1'))
        hits = [i for i, x in enumerate(L) if x[2].lower().replace('"','').startswith(p.lower().replace('"','')) and i >= after]
        if len(hits) < int(n): raise SystemExit(f'NOTFOUND {slug} {spec} hits={len(hits)}')
        return hits[int(n) - 1]
    i = find(a); j = find(b) if '#' in b else find(b, i)
    s, e = L[i][0] - 0.5, L[j][1] + 0.9
    r1 = plan[slug]
    ov = max(0, min(e, r1['end']) - max(s, r1['start']))
    rows.append(dict(slug=slug, name=r1.get('name'), round=rnd, start=round(s,2), end=round(e,2), dur=round(e-s,1), hook=hook, title=title, quote=quote, tags=tags,
                     accent=r1['accent'], first=L[i][2], last=L[j][2], overlap=round(ov,1)))
# overlap between R2 and R3 of the same song
for r in rows:
    o = [x for x in rows if x['slug'] == r['slug'] and x['round'] != r['round']][0]
    r['overlap23'] = round(max(0, min(r['end'], o['end']) - max(r['start'], o['start'])), 1)
for r in rows:
    flag = (' OVERLAP_R1' if r['overlap'] > 1 else '') + (' OVERLAP_23' if r['overlap23'] > 1.5 else '') + (' LONG' if r['dur'] > 75 else '') + (' SHORT' if r['dur'] < 25 else '')
    if flag: print(r['slug'], r['round'], r['start'], r['end'], r['dur'], flag)
json.dump(rows, open('/home/claude/shorts/round2/rows.json','w'), indent=1, ensure_ascii=False)
print(len(rows), 'clips', round(sum(r['dur'] for r in rows)/60,1), 'min total')
