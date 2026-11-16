import json,re
def norm(s): return re.sub(r"[^a-z0-9 ]","",s.lower().replace("’","'").replace("'",""))
def t(slug,phrase,nth=1):
    d=json.load(open(f'/home/claude/songs/{slug}/aligned.json'))
    n=0
    for L in d:
        if 'words' not in L: continue
        txt=norm(' '.join(w['w'] for w in L['words']))
        if norm(phrase) in txt:
            n+=1
            if n==nth:
                s=L['words'][0]['s']; return f"{int(s//60)}:{int(s%60):02d}"
    return "?:??"
S=[]
def song(title, slug, note, items):
    S.append(f"\n## {title}\n" + (f"{note}\n" if note else ""))
    for it in items:
        if isinstance(it,str): S.append(f"- {it}\n")
        else:
            ph, msg = it[0], it[1]; nth = it[2] if len(it)>2 else 1
            S.append(f"- {t(slug,ph,nth)} \"{ph}\" — {msg}\n")
exec(open('/tmp/rv/items.py').read())
open('/home/claude/zachary-shorts/pipeline/drive_versions/REVIEW.md','w').write("""# Drive lyric videos: lines to check by ear

Each video already shows my best guess. If a line is wrong, tell me the right words (or just the time) and I'll fix and re-render that song.
Songs marked "your sheet" use your own written lyrics, so they need little or no checking. The fast rap songs with no sheet need the most.

Duplicates found: "True Strength Isn't Loud (1)" and "A New God Rises (1)" are the exact same audio as the main files, and "I feel the weight of every heart..." is the same audio as "Lone Wolf Rising". So there are 25 videos, not 28.
"""+"".join(S))
print("ok")
