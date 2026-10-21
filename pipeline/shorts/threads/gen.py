import json, sys
r1 = {p['date'][:10]: p['info'] for p in json.load(open('/home/claude/kit/posts.json'))}
r2 = {p['date'][:10]: p['info'] for p in json.load(open('/home/claude/shorts/round2/posts2.json'))}
out = []
for line in open('map.tsv'):
    d, pid, uuid, f = line.split()
    info = json.loads(json.dumps(r1.get(d) or r2[d]))
    info['media'] = [f'https://static.metricool.com/planner/202610/7494992-file-{f}.mp4']
    if not any(p['network'] == 'threads' for p in info['providers']):
        info['providers'].append({'network': 'threads'})
    info['threadsData'] = {}
    out.append({'date': d, 'id': pid, 'uuid': uuid, 'info': info})
json.dump(out, open('updates.json', 'w'), ensure_ascii=False)
print(len(out), 'updates;', sum(len(o['info']['text']) > 500 for o in out), 'over 500 chars')
