#!/usr/bin/env python3
"""Order the 67 quick-hook Shorts into daily 3 PM slots (Oct 26 - Dec 31, 2026) and build Metricool post payloads."""
import json, re, datetime
P = '/home/claude/zachary-shorts/pipeline/qh'
posts = json.load(open(f'{P}/posts.json'))
by = {(p['slug'], p['var']): p for p in posts}
songs = []
for p in posts:
    if p['slug'] not in songs: songs.append(p['slug'])
rA = [by[(s, 'A')] for s in songs]
rB = [by[(s, 'B')] for s in songs]
rC = [by[(s, 'C')] for s in songs if (s, 'C') in by]
# holiday touches: grief song on Christmas Day, "it's okay to not be okay" on New Year's Eve
def move(lst, slug, idx):
    x = next(p for p in lst if p['slug'] == slug); lst.remove(x); lst.insert(idx, x)
move(rC, 'remember_me_when_im_gone', 10)   # Dec 15 + 10 = Dec 25
move(rC, 'unfinished', len(rC) - 1)        # Dec 31
order = rA + rB + rC
assert len(order) == 67, len(order)
RAW = 'https://raw.githubusercontent.com/zacharypatzer/zachary-shorts/main/shorts/qh/'
out = []
d0 = datetime.date(2026, 10, 26)
for i, p in enumerate(order):
    day = d0 + datetime.timedelta(days=i)
    tag = re.sub(r"[^A-Za-z0-9]", '', p['title'].replace("'", ''))
    tag = ''.join(w[:1].upper() + w[1:] for w in re.sub(r"[^A-Za-z0-9 ]", '', p['title'].replace("'", '')).split())
    hook = p['hook'].rstrip()
    if hook[-1] not in '.?!': hook += '.'
    pay = re.sub(r"\b[A-Z][A-Z']+\b", lambda m: m.group(0).lower(), p['payoff'])
    pay = re.sub(r"([.?!] )([a-z])", lambda m: m.group(1) + m.group(2).upper(), pay)
    body = f"{hook} {pay}"
    text = f"{body}\n\n{p['title']} by Zachary Patzer. Full song on my YouTube channel.\n\n#{tag} #ZacharyPatzer #cancersurvivor #originalmusic #fyp"
    info = {
        'autoPublish': True, 'draft': False, 'descendants': [], 'firstCommentText': '', 'hasNotReadNotes': False, 'shortener': False,
        'smartLinkData': {'ids': []}, 'media': [RAW + p['file']], 'mediaAltText': [None], 'videoThumbnailUrl': RAW + p['cover'],
        'providers': [{'network': 'instagram'}, {'network': 'tiktok'}, {'network': 'youtube'}, {'network': 'threads'}],
        'publicationDate': {'dateTime': f'{day}T15:00:00', 'timezone': 'America/Los_Angeles'},
        'text': text,
        'instagramData': {'type': 'REEL', 'showReelOnFeed': True, 'isAiGenerated': True},
        'youtubeData': {'title': (hook[:88] + ' #Shorts'), 'type': 'short', 'privacy': 'public',
                        'tags': [p['title'], f"{p['title']} Zachary Patzer", 'Zachary Patzer', 'Zachary Patzer shorts', 'cancer survivor song',
                                 'songs about hope', 'original music', 'shorts'],
                        'category': 'MUSIC', 'madeForKids': False, 'isAiGeneratedContent': True},
        'tiktokData': {'privacyOption': 'PUBLIC_TO_EVERYONE', 'title': hook[:150], 'photoCoverIndex': 0, 'isAigc': True},
        'threadsData': {},
    }
    out.append({'i': i, 'date': f'{day}T15:00:00-0{8 if day >= datetime.date(2026, 11, 1) else 7}:00', 'file': p['file'], 'hook': hook, 'info': info})
json.dump(out, open(f'{P}/sched.json', 'w'), indent=1)
for o in out: print(o['i'], o['date'][:10], o['file'], '|', o['hook'])
