#!/usr/bin/env python3
"""Build the Shorts Posting Kit page from the Shorts plan + asset URLs (kit/assets.json)."""
import json, html, os
P = json.load(open('/home/claude/shorts/all24/plan.json'))
items = []
for x in P:
    if x['slug'] == 'im_a_witness':
        continue
    items.append(dict(slug=x['slug'], name=x['name'], file=x['file'], title=x['title'], desc=x['desc'], tags=x['tags']))
items.append(dict(slug='a_mile_an_hour', name='A Mile An Hour', file='/home/claude/shorts/a_mile_an_hour_v2/AMAH_Short_Chorus.mp4',
    title="I can't walk fast. I still walk. 🛣️ #Shorts",
    desc="A Mile An Hour (Remastered) by Zachary Patzer. Full lyric video on my channel.\nSlow ain't stoppin'. Slow ain't gone. I woke up this mornin', so I'm movin' on.\n\n#AMileAnHour #ZacharyPatzer #shorts #cancersurvivor",
    tags="A Mile An Hour, A Mile An Hour Zachary Patzer, Zachary Patzer, Zachary Patzer shorts, blues, soul blues, music, new song, lyrics, lyric video, songs about cancer, cancer survivor song, never give up, songs about hope, inspirational songs, shorts"))
items.append(dict(slug='lions_heart', name="Lion's Heart", file='/home/claude/shorts/lions_heart/LionsHeart_Short.mp4',
    title="For everyone in the chair, and everyone by the bed 🦁 #Shorts",
    desc="Lion's Heart (Remastered) by Zachary Patzer. Full lyric video on my channel.\nNobody asked to be here. Nobody chose this fight. But look at all this love.\n\n#LionsHeart #ZacharyPatzer #shorts #cancersurvivor",
    tags="Lion's Heart, Lion's Heart Zachary Patzer, Zachary Patzer, Zachary Patzer shorts, reggae, roots reggae, music, new song, lyrics, lyric video, songs about cancer, cancer survivor song, songs for cancer patients, caregiver song, songs about hope, inspirational songs, shorts"))
A = json.load(open('/home/claude/kit/assets.json')) if os.path.exists('/home/claude/kit/assets.json') else {}
S = json.load(open('/home/claude/kit/schedule.json')) if os.path.exists('/home/claude/kit/schedule.json') else {}
for it in items:
    it['url'] = A.get(it['slug'], '')
    it['fname'] = it['file'].split('/')[-1]
    it['when'] = S.get(it['slug'], {}).get('when', '')
    it['status'] = S.get(it['slug'], {}).get('status', '')
items.sort(key=lambda it: S.get(it['slug'], {}).get('order', 99))
json.dump(items, open('/home/claude/kit/items.json', 'w'), indent=1, ensure_ascii=False)
data = json.dumps([{k: v for k, v in it.items() if k != 'file'} for it in items], ensure_ascii=False).replace('</', '<\\/')
page = open('/home/claude/kit/template.html').read().replace('/*DATA*/[]', data).replace('__FOLDER__', '11ASu0sHTwf66xybMupbbBBGaWV_ZVl7y')
open('/home/claude/kit/shorts_kit.html', 'w').write(page)
print(len(items), 'shorts;', sum(1 for i in items if i['url']), 'with video')
