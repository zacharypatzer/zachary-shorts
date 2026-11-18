#!/usr/bin/env python3
"""Build Metricool payloads that turn the removed songs' draft slots into the new songs' Shorts.
Writes sched.json: [{date, id, uuid, name, info}]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from plan import V2, QH, TITLE
P = '/home/claude/zachary-shorts/pipeline'
RAW = 'https://raw.githubusercontent.com/zacharypatzer/zachary-shorts/main/shorts/new6'
v2 = {n: (s, a, b, h1, h2) for s, n, a, b, h1, h2 in V2}
qh = {n: (s, a, b, l1, big, pk) for s, n, a, b, l1, big, pk in QH}
PAY = {'A': 'That was 4 years ago. Still here.', 'B': "Stage 4 Hodgkin's. 3 bells rung.", 'C': 'Send this to someone who needs it.'}
GENERIC = "August 17, 2022. I rang the bell. Life after cancer has been its own fight, but I'm still here."
TRUE = {  # story-test window (through Nov 16): open with a real moment he has shared
    'N_am_2': "Pain or panic wakes me up most nights. That's when I write, for whoever's up alone.",
    'N_wl_1': "I've taken notes on life for decades. After chemo, I started turning them into songs.",
    'N_if_1': 'When I heard stage four, I said "I\'m fine."',
    'N_tu_4': 'People message me: "How can I complain after seeing what you go through?"',
    'N_hl_5': "I don't meet people in person anymore, for my health. These songs are how I reach you.",
}
STORY = [('2026-11-06', 415863664, '5389688414245044474', 'N_am_2'), ('2026-11-10', 415864564, '4687133092710205075', 'N_wl_1'),
         ('2026-11-14', 415864600, '-172292889922353368', 'N_if_1'), ('2026-11-15', 415887637, '-2350761705570023106', 'N_tu_4'),
         ('2026-11-16', 415887650, '8190023457099039722', 'N_hl_5'), ('2026-11-19', 415887709, '6150824306203312230', 'N_hy_1'),
         ('2026-11-23', 415888133, '940060227546269152', 'N_tu_1'), ('2026-11-27', 415888624, '-282453897178169183', 'N_if_5'),
         ('2026-11-28', 415888632, '4231326389008287247', 'N_hl_1'), ('2026-11-29', 415888643, '-5359208567741199743', 'N_wl_2'),
         ('2026-12-10', 415889918, '-5783721295203186144', 'N_am_4'), ('2026-12-11', 415889930, '-5542980357858310584', 'N_hy_5')]
DAILY = [('2026-11-07', 415863764, '-7549463533787723904', 'N_am_1'), ('2026-11-08', 415863836, '-1748547489262056704', 'N_tu_2'),
         ('2026-11-09', 415863913, '5324055688727380634', 'N_if_2'), ('2026-11-20', 415888100, '1231700823310290566', 'N_hl_2'),
         ('2026-11-21', 415888107, '-722024930724591452', 'N_wl_3'), ('2026-11-24', 415888121, '-3760306708036956236', 'N_hy_3'),
         ('2026-11-28', 415888603, '-3047229900973389297', 'N_am_3'), ('2026-12-02', 415889158, '5336669164386406081', 'N_tu_3'),
         ('2026-12-03', 415889185, '-5417794562835595016', 'N_if_3'), ('2026-12-04', 415889193, '-3202745608791373631', 'N_hl_3'),
         ('2026-12-15', 415890265, '-6148192911685433288', 'N_wl_4'), ('2026-12-16', 415890275, '-1564757103001581394', 'N_hy_4'),
         ('2026-12-19', 415890287, '2529172831054611645', 'N_am_5'), ('2026-12-23', 415890614, '-5368062826439815399', 'N_tu_5'),
         ('2026-12-27', 415891044, '-3812990471101659363', 'N_if_4'), ('2026-12-28', 415891063, '6660619811785164759', 'N_hl_4'),
         ('2026-12-29', 415891080, '-4632811230373068507', 'N_wl_5')]
QHS = [('2026-11-08', 415863568, '8069558173356805252', 'QN_am_A'), ('2026-11-12', 415864496, '8916991020215714489', 'QN_hl_A'),
       ('2026-11-16', 415887656, '729386449153182550', 'QN_if_A'), ('2026-11-17', 415887666, '2449141551628832184', 'QN_wl_A'),
       ('2026-11-18', 415887688, '5848833311537318914', 'QN_hy_A'), ('2026-11-29', 415888613, '1371806660445947771', 'QN_tu_A'),
       ('2026-11-30', 415889150, '-7699478755133272688', 'QN_am_B'), ('2026-12-03', 415889173, '8123603287791649363', 'QN_hl_B'),
       ('2026-12-07', 415889318, '6548892679421579263', 'QN_if_B'), ('2026-12-11', 415889889, '7125807419894418000', 'QN_wl_B'),
       ('2026-12-12', 415889896, '1523924096454708652', 'QN_hy_B'), ('2026-12-13', 415889907, '416393178128991452', 'QN_tu_B'),
       ('2026-12-20', 415890586, '630375201175127716', 'QN_am_C'), ('2026-12-21', 415890601, '-5383442430772297600', 'QN_hl_C'),
       ('2026-12-28', 415891053, '5932827994282804541', 'QN_if_C'), ('2026-12-29', 415891070, '3570344613958406112', 'QN_tu_C'),
       ('2026-12-31', 415891215, '5565732436824572445', 'QN_wl_C')]


def lyric_line(slug, a, b, k=0):
    L = [x for x in json.load(open(f'{P}/songs/{slug}/lyrics_final.json')) if x.get('words')]
    ins = [' '.join(w['w'] for w in x['words']) for x in L if x['words'][0]['s'] >= a - 0.6 and x['words'][-1]['e'] <= b + 0.9]
    t = ins[min(k, len(ins) - 1)].strip().rstrip(',')
    return t[0].upper() + t[1:] + ('' if t[-1] in '.!?"' else '.')


def info(date, hm, name, text, yt_title, tiktok_title, song):
    tags = [TITLE[song], f'{TITLE[song]} Zachary Patzer', 'Zachary Patzer', 'Zachary Patzer shorts', 'cancer survivor song',
            'songs about hope', 'original music', 'shorts', 'ytshorts', 'youtubeshorts']
    return {"autoPublish": True, "draft": False, "descendants": [], "firstCommentText": "", "hasNotReadNotes": False,
            "shortener": False, "smartLinkData": {"ids": []},
            "media": [f'{RAW}/{name}.mp4'], "mediaAltText": [None], "videoThumbnailUrl": f'{RAW}/{name}_cover.jpg',
            "providers": [{"network": "instagram"}, {"network": "tiktok"}, {"network": "youtube"}, {"network": "threads"}],
            "publicationDate": {"dateTime": f'{date}T{hm}:00', "timezone": "America/Los_Angeles"},
            "text": text,
            "instagramData": {"type": "REEL", "showReelOnFeed": True, "isAiGenerated": True},
            "tiktokData": {"privacyOption": "PUBLIC_TO_EVERYONE", "title": tiktok_title, "isAigc": True},
            "youtubeData": {"title": yt_title, "type": "short", "privacy": "public", "tags": tags, "category": "MUSIC",
                            "madeForKids": False, "isAiGeneratedContent": True},
            "threadsData": {}}


def natural(l1, big):
    s = big.lower()
    s = s[0].upper() + s[1:] if l1.rstrip().endswith(('.', ':', '?', '."')) else s
    for a, b in (("i'm", "I'm"), ("i've", "I've"), ("i ", "I "), ("stage 4", "Stage 4")):
        s = s.replace(a, b) if a != "i " else (('I ' + s[2:]) if s.startswith('i ') else s.replace(' i ', ' I '))
    t = f'{l1} {s}'
    import re
    return re.sub(r'([.!?] )([a-z])', lambda m: m.group(1) + m.group(2).upper(), t)


out = []
for date, i, u, n in STORY:
    s, a, b, h1, h2 = v2[n]
    first = TRUE.get(n, GENERIC) if date <= '2026-11-16' else GENERIC
    hook = f'{h1} {h2}'
    text = (f'{first}\n\n{TITLE[s]} (Remastered) by Zachary Patzer. Full lyric video on my YouTube channel.\n'
            f'“{lyric_line(s, a, b).rstrip(".")}.”\n\nWhat\'s keeping you going right now?\n\n'
            '#cancersurvivor #hodgkinslymphoma #inspirationalmusic #stage4survivor #fyp')
    out.append(dict(date=date, slot='12:00 story', id=i, uuid=u, name=n, info=info(date, '12:00', n, text, f'{hook} #ytshorts #youtubeshorts', first if len(first) < 150 else hook, s)))
for date, i, u, n in DAILY:
    s, a, b, h1, h2 = v2[n]
    hook = f'{h1} {h2}'
    text = (f'{hook}\n\n{TITLE[s]} (Remastered) by Zachary Patzer. Full lyric video on my YouTube channel.\n'
            f'{lyric_line(s, a, b, 1)}\n\n#cancersurvivor #inspirationalmusic #stage4survivor #lifeaftercancer #fyp')
    out.append(dict(date=date, slot='17:30 daily', id=i, uuid=u, name=n, info=info(date, '17:30', n, text, f'{hook} #ytshorts #youtubeshorts', hook, s)))
for date, i, u, n in QHS:
    s, a, b, l1, big, pk = qh[n]
    hook = natural(l1, big)
    text = (f'{hook} {PAY[pk]}\n\n{TITLE[s]} by Zachary Patzer. Full song on my YouTube channel.\n\n'
            '#cancersurvivor #inspirationalmusic #stage4survivor #originalmusic #fyp')
    out.append(dict(date=date, slot='15:00 qh', id=i, uuid=u, name=n, info=info(date, '15:00', n, text, f'{hook} #ytshorts #youtubeshorts', hook, s)))
out.sort(key=lambda x: x['info']['publicationDate']['dateTime'])
json.dump(out, open(f'{P}/shorts/new6/sched.json', 'w'), indent=1)
for x in out:
    print(x['info']['publicationDate']['dateTime'][5:16], x['name'], '|', x['info']['text'].split('\n')[0][:90])
print(len(out))
