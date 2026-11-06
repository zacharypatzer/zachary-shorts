#!/usr/bin/env python3
"""Pre-release lyric check for a new song draft (Suno lyrics with [Section] tags).

usage: lyric_check.py draft.txt "Title" [catalog_dir] [--style style.txt] [--exclude exclude.txt]

Prints the raw stats (catalog overlaps, syllables, repeated words, title count, characters),
then two lists built from every past rating and fix (see pipeline/SONG_CHECKLIST.md):
  FIX   - definite problems. Must be zero before he runs it in Suno.
  CHECK - likely weak spots. Look at each one; fix it or be able to say why it's fine.
Drafts without [Section] tags work too: blank lines split sections, repeated blocks count as chorus.
"""
import argparse, re, glob, collections

ap = argparse.ArgumentParser()
ap.add_argument('path')
ap.add_argument('title')
ap.add_argument('cat_dir', nargs='?', default='/home/claude/zachary-shorts/pipeline/songs')
ap.add_argument('--style')
ap.add_argument('--exclude')
ap.add_argument('--replaces', help='song folder this draft replaces (left out of the overlap check)')
ap.add_argument('--skip-self', action='store_true', help='leave this song out of the catalog (for testing on catalog songs)')
a = ap.parse_args()
path, title, cat_dir = a.path, a.title, a.cat_dir
txt = open(path).read()
FIX, CHECK = [], []


def syl(w):
    w = w.lower().strip(".,!?\"…()").replace("'", "")
    if not w:
        return 0
    n = len(re.findall(r'[aeiouy]+', w))
    if w.endswith('e') and not w.endswith(('le', 'ee')) and n > 1:
        n -= 1
    return max(1, n)


def norm(l):
    return re.sub(r'\s+', ' ', re.sub(r'\([^)]*\)', '', l)).strip()


# ---- sections -------------------------------------------------------------
lines = [l for l in txt.splitlines() if not l.startswith('#')]
sections = []  # (tag, [lines])
has_tags = any(l.startswith('[') for l in lines)
cur = None
for l in lines:
    if l.startswith('['):
        cur = (l, [])
        sections.append(cur)
    elif not l.strip():
        if not has_tags:
            cur = None
    elif l.strip() == '~':
        continue
    else:
        if cur is None:
            cur = ('[untagged]' if not has_tags else '[top]', [])
            sections.append(cur)
        cur[1].append(l.strip())
blocks = collections.Counter('\n'.join(norm(x).lower() for x in s[1]) for s in sections)


def is_chorus(s):
    return 'chorus' in s[0].lower() or (not has_tags and blocks['\n'.join(norm(x).lower() for x in s[1])] > 1)


body = '\n'.join(l for l in lines if not l.startswith('['))
words = re.findall(r"[a-z']+", body.lower())

# ---- original stats ---------------------------------------------------------
cat_files = [f for f in glob.glob(f'{cat_dir}/*/lyrics.txt')
             if not (a.skip_self and open(f).read() == open(path).read())
             and not (a.replaces and f.split('/')[-2] == a.replaces)]
cat = ' '.join(open(f).read().lower() for f in cat_files)
cw = re.findall(r"[a-z']+", cat)
grams = set(tuple(cw[i:i + 4]) for i in range(len(cw) - 3))
FUNC = set("i you me my we the a an and to of in it that is was don't have it's i'm be with for on at so but your you're what all just".split())
hits = sorted(set(' '.join(words[i:i + 4]) for i in range(len(words) - 3)
                  if tuple(words[i:i + 4]) in grams and sum(w in FUNC for w in words[i:i + 4]) < 3))
print('CATALOG OVERLAPS (4+ words):', hits or 'none')
for h in hits:
    FIX.append(f'recycled phrase from another song: "{h}"')

print('\nSYLLABLES (! = far off section average)')
for tag, rows in sections:
    print(tag)
    if not rows:
        continue
    n = [sum(syl(w) for w in r.split()) for r in rows]
    avg = sum(n) / len(n)
    for k, r in zip(n, rows):
        off = abs(k - avg) > 4
        print(f"{'!' if off else ' '}{k:3d}  {r}")
        if off:
            CHECK.append(f'{tag} line length way off the others ({k} vs ~{avg:.0f} syllables), Suno may cram or stretch: "{r}"')

stop = set('the and you that they for with but when there this what your from have will just been were into them then than our are its'.split())
c = collections.Counter(w for w in words if len(w) > 3 and w not in stop)
print('\nMOST REPEATED:', c.most_common(15))
tcount = body.lower().count(title.lower())
print('TITLE SUNG:', tcount, 'times')
print('CHARACTERS:', len(txt), '(Suno max 5000)')
if len(txt) > 5000:
    FIX.append(f'{len(txt)} characters, over Suno\'s 5000 limit')
if tcount < 10:
    CHECK.append(f'title only sung {tcount} times (aim 10+) - is the title the hook?')

# ---- phrase lists (from past critiques) ------------------------------------
CLICHES = ['turns to gold', 'turn to gold', 'pain is proof', 'proof you\'re alive', 'happens for a reason',
           'end of the tunnel', 'dancing in the rain', 'dance in the rain', 'closer than they appear',
           'numbers don\'t lie', 'ghost inside a cage', 'like a christmas tree', 'heavy, and holy',
           'the fight is done', 'against all odds', 'beat the odds', 'from the ashes', 'phoenix', 'silver lining',
           'stronger than ever', 'never give up', 'one day at a time', 'day by day', 'what doesn\'t kill',
           'broken wings', 'storm will pass', 'after the storm', 'heart of gold', 'tears of joy',
           'scars tell a story', 'rock bottom', 'keep your head up', 'chin up', 'born to fight', 'battle scars',
           'mountain to climb', 'fire inside', 'shine bright', 'rise above', 'unbreakable', 'pick up the pieces',
           'light in the dark', 'light the way', 'won\'t back down', 'stand tall', 'let it be', 'the sky\'s the limit',
           'live like you were dying', 'every cloud', 'count your blessings', 'face my fears', 'empty your cup',
           'ninety percent', '90%', 'six and nine', 'carry on', 'cry later', 'hold on tight', 'the whole world',
           'out of the crowd', 'up there', 'count the laughs that count']
for p in CLICHES:
    for l in body.splitlines():
        if p in l.lower():
            FIX.append(f'cliché "{p}": "{l.strip()}"')

PROMISE = r"\b(promise[ds]?|promisin'?g?|i swear|swore|i will always|i'll always|i'll never|i will never|guarantee)\b"
for l in body.splitlines():
    if re.search(PROMISE, l.lower()):
        FIX.append(f'promise (his rule: no promises; use "hopin\'"): "{l.strip()}"')

WEAK = r"only the strong|the weak\b|weak ones|weak might|strong survive|if you were strong|too weak"
for l in body.splitlines():
    if re.search(WEAK, l.lower()):
        FIX.append(f'could read like people who died were weak: "{l.strip()}"')

SUNO_BLOCK = ['skank', 'hammond', 'algorithm', 'delete', 'blocked', 'block me', 'shadowban', 'fender', 'gibson',
              'auto-tune', 'man my size don\'t cry']
for p in SUNO_BLOCK:
    if re.search(r'\b' + re.escape(p) + r'\b', txt.lower()):
        FIX.append(f'word Suno or the platforms may flag: "{p}"')

SPANISH = r"\b(mi|corazón|corazon|amigo|amor|vida|gracias|familia|señor|senor|dios|hermano)\b"
for l in body.splitlines():
    if re.search(SPANISH, l.lower()):
        FIX.append(f'Spanish word (he passed on Spanish lines): "{l.strip()}"')

THEMES = {
    'promise to family / not quitting (almost overused)': r"\bmy family\b.*(told|said|swore)|wouldn't quit|won't quit|told them what i'd do",
    'walking / miles / steps (A Mile An Hour owns it)': r"\bwalk(in'?g?|ed|s)?\b|\bmiles?\b|\bsteps?\b|one foot",
    'screen door / zoo visit (My Word Won\'t Die, Island Time)': r"screen door|zoo|through the screen|on the lawn",
    'smiling to hide pain (in 5 songs already)': r"smil(e|in'?g?).*(hide|pain|hurt|through)|\bmask\b",
    'ringing the bell (only with a new angle)': r"\bbells?\b|\brang\b|\bring the\b",
    'buggy / walker / braces (throws off the vibe)': r"buggy|walker|braces|rollator",
    'father\'s passing (he left it out of new songs)': r"daddy|my father|my dad\b",
    'stage four / chemo chair (fine once, don\'t lean on it)': r"stage (four|4)|chemo chair",
}
for name, rx in THEMES.items():
    found = [l.strip() for l in body.splitlines() if re.search(rx, l.lower())]
    if found:
        CHECK.append(f'catalog theme - {name}: "{found[0]}"' + (f' (+{len(found)-1} more)' if len(found) > 1 else ''))

VAGUE = r"\b(really|truly|somehow|somethin'?g?|stuff|things?|kinda|sorta|whatever|anyway)\b"
for tag, rows in sections:
    for r in rows:
        if is_chorus((tag, rows)) and re.search(VAGUE, r.lower()):
            CHECK.append(f'{tag} vague word in the chorus, is it saying something concrete?: "{r}"')

PREACH = r"^(so )?(you (gotta|need to|should|have to|must)|don't you|go (and )?|find (a|somebody|someone)|call the|help somebody|be the one)"
pre = [r for _, rows in sections for r in rows if re.search(PREACH, r.lower())]
if len(pre) >= 3:
    CHECK.append(f'{len(pre)} instruction lines - risk of sounding preachy, e.g. "{pre[0]}"')

# ---- rhymes ------------------------------------------------------------------
V = 'aeiouy'


def rkey(w):
    w = re.sub(r"[^a-z']", '', w.lower()).replace("in'", 'ing').replace("'", '')
    if w.endswith('ing') and len(w) > 4:
        w = w[:-3]
    m = list(re.finditer(r'[aeiouy]+', w))
    if not m:
        return w, w
    i = m[-1].start()
    if w.endswith('e') and len(m) > 1 and m[-1].group() == 'e' and m[-1].end() == len(w):
        i = m[-2].start()
    return w[i:], re.match(r'[aeiouy]+', w[i:]).group()


def rhymes(x, y):
    if not re.search('[aeiouy]', x.lower()) or not re.search('[aeiouy]', y.lower()):
        return 'no'
    if x == y:
        return 'same'
    kx, vx = rkey(x)
    ky, vy = rkey(y)
    if kx == ky or kx[-2:] == ky[-2:] and len(kx) > 1:
        return 'yes'
    ing = all(re.sub(r"[^a-z']", '', w.lower()).replace("in'", 'ing').endswith('ing') for w in (x, y))
    if ing:  # -in'/-ing endings only rhyme if the sound before matches (livin'/givin', not believin'/seein')
        return 'slant' if vx == vy else 'no'
    if vx[0] == vy[0] or kx[-1:] == ky[-1:]:
        return 'slant'
    return 'no'


def endw(l):
    t = re.findall(r"[A-Za-z']+", norm(l))
    return t[-1] if t else ''


seen_same = set()
for tag, rows in sections:
    ends = [endw(r) for r in rows]
    for i in range(len(rows) - 1):
        if ends[i] and ends[i].lower() == ends[i + 1].lower() and norm(rows[i]).lower() != norm(rows[i + 1]).lower():
            key = (ends[i].lower(), rows[i])
            if key not in seen_same:
                seen_same.add(key)
                CHECK.append(f'{tag} rhymes a word with itself ("{ends[i]}"): "{rows[i]}" / "{rows[i+1]}"')
    if is_chorus((tag, rows)) and len(rows) >= 4:
        loose = []
        for i, e in enumerate(ends):
            if not e:
                continue
            partners = [ends[j] for j in range(max(0, i - 2), min(len(ends), i + 3)) if j != i]
            if not any(rhymes(e, p) != 'no' for p in partners):
                loose.append(rows[i])
        if len(loose) >= len(rows) * 0.4:
            CHECK.append(f'{tag} chorus rhymes are loose ({len(loose)}/{len(rows)} lines have no true rhyme nearby), e.g. "{loose[0]}"')

# ---- structure -----------------------------------------------------------------
first = next((r for _, rows in sections for r in rows), '')
if re.match(r"^(there's|there is|the |it's a|it was a|a |in the )", first.lower()):
    CHECK.append(f'first line opens like a scene description, not a hook (mystery / jolt / question?): "{first}"')

for tag, rows in sections:
    starts = collections.Counter(' '.join(r.lower().split()[:2]) for r in rows)
    lead, n = starts.most_common(1)[0] if starts else ('', 0)
    if n >= 4 and not is_chorus((tag, rows)):
        CHECK.append(f'{tag} reads like a list ({n} lines start "{lead}") - does each item build?')
    for r in rows:
        if norm(r).count(',') >= 2:
            CHECK.append(f'{tag} {norm(r).count(",")} mid-line commas, Suno may go choppy: "{r}"')
    if has_tags and len(tag) > 70:
        CHECK.append(f'long section tag acts like a 2nd Style box, keep it short: "{tag[:60]}..."')

near = []
for tag, rows in sections:
    if is_chorus((tag, rows)):
        continue
    ws = [re.findall(r"[a-z']+", r.lower()) for r in rows]
    for i in range(len(ws)):
        for w in set(ws[i]):
            if len(w) > 4 and w not in stop and w not in title.lower() and any(w in ws[j] for j in range(i + 1, min(len(ws), i + 3))):
                near.append((tag, w))
for tag, w in sorted(set(near))[:8]:
    CHECK.append(f'{tag} "{w}" repeated within 3 lines - cut one unless it\'s the hook')

if has_tags and not any('outro' in t.lower() for t, _ in sections):
    CHECK.append('no [Outro] - check the ending pays off the intro')
if has_tags and not any(re.search(r'-|:', t) for t, _ in sections):
    CHECK.append('no musical cues in section tags (e.g. [Final Chorus - full band, key change])')
mins = len(words) / 150
print(f'EST. LENGTH: ~{mins:.1f} min ({len(words)} words)')
if mins > 5.5:
    CHECK.append(f'~{mins:.1f} min - long songs scored lower with strangers; is every section earning its place?')

# ---- style boxes ---------------------------------------------------------------
if a.style:
    s = open(a.style).read().lower()
    if 'clear enunciation' not in s:
        FIX.append('Style box missing "clear enunciation"')
    if 'spanish' in s or 'latin' in s:
        CHECK.append('Style box mentions Spanish/Latin - make sure no Spanish vocals come out')
if a.exclude:
    if 'static' not in open(a.exclude).read().lower():
        FIX.append('Exclude box missing "static"')
if not a.style or not a.exclude:
    CHECK.append('style/exclude not checked - pass --style and --exclude files')

print(f'\n===== FIX ({len(FIX)}) - must be zero =====')
for x in FIX:
    print(' x', x)
print(f'\n===== CHECK ({len(CHECK)}) - look at each one =====')
for x in CHECK:
    print(' ?', x)
print('\nThen walk the manual boxes in pipeline/SONG_CHECKLIST.md (stranger test, hook, one idea, story logic).')
