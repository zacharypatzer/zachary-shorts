#!/usr/bin/env python3
"""Specs for one best Short per song (24 songs). Computes windows, renders (2 at a time), writes copy text."""
import sys, json, subprocess, os
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, '/home/claude/pkg')
from texts import T

OUT = '/home/claude/shorts/all24'
# slug, display title, hashtag, first line, last line, hook lines, accent, title, lyric line for description, song-specific tags
S = [
 ('take_a_number', 'Take a Number', 'TakeANumber', 'He rode into town', 'So take a number, take a seat', ["Death walked into my clinic.", "I told him: take a number."], '#f1d9ad',
  "Death walked into my clinic. I told him: take a number. 🎟️ #Shorts", "I got people I ain't done loving yet.", 'western, outlaw country, storytelling song'),
 ('light_one_let_it_go', 'Light One, Let It Go', 'LightOneLetItGo', "Somewhere there's a waitress", 'Light one, let it go#2', ["Somewhere tonight,", "someone needs this."], '#c7a6ff',
  "Somewhere tonight, someone needs this 🏮 #Shorts", "Every song I write is a paper lantern. Take it. It was always yours.", 'folk pop, paper lanterns, kindness song'),
 ('floor_of_shadows', 'Floor of Shadows', 'FloorOfShadows', "I'm wearing the clothes", 'Up on the fourth floor', ["Up on the fourth floor,", "the ghosts are real."], '#fff03a',
  "Up on the fourth floor, the ghosts are real #Shorts", "A piece of you stays up there.", 'dark blues, hospital song, chemo ward'),
 ('i_live_on_through_you', 'I Live On Through You', 'ILiveOnThroughYou', "I'm leaving you my boots", "That I haven't given you", ["I'm leaving you my boots.", "Not the kind you buy."], '#ffd890',
  "I'm leaving you my boots 🥾 #Shorts", "They were broken in for you.", 'heartland rock, legacy song, songs for family'),
 ('even_if_we_stumble', 'Even If We Stumble', 'EvenIfWeStumble', 'Every other week', "I don't want you to rush", ["Sounds like a love song.", "It's about chemo."], '#92f7cf',
  "Sounds like a love song. It's about chemo. #Shorts", "Every other week, right on schedule.", 'chemo song, love song twist, R&B'),
 ('beautiful_anyway', 'Beautiful Anyway', 'BeautifulAnyway', 'So before the night', 'And it was beautiful', ["It was heavy, and holy,", "and beautiful anyway."], '#e3874f',
  "It was heavy, and holy, and beautiful anyway #Shorts", "Go hold them too long.", 'power ballad, goodbye song, grief song'),
 ('island_time', 'Island Time', 'IslandTime', 'They handed me a calendar', 'Every slow sunset', ["They gave me a date.", "I buried it in the sand."], '#46e8e4',
  "They gave me a date. I buried it in the sand. 🏝️ #Shorts", "Now the tide does the counting and the sun keeps the score.", 'island music, tropical, beach song'),
 ('living_in_the_echo', 'Living in the Echo', 'LivingInTheEcho', 'That alarm they said', "But I'm living in the echo", ["Four years clear.", "The alarm's still on."], '#ffa31a',
  "Four years clear. The alarm's still on. #Shorts", "Don't build a prison for tomorrow out of what might not come true.", 'survivor anxiety, PTSD song, scanxiety'),
 ('no_complaints', 'No Complaints', 'NoComplaints', "These legs don't hold", 'Come on, tell me, how we doing', ["How you doing?", "No complaints."], '#5f8bff',
  "How you doing? No complaints. #Shorts", "Got a timer in my legs and a buggy on the go.", 'Delta blues, blues, walker'),
 ('unfinished', 'Unfinished', 'Unfinished', 'I said "I\'m fine" when', 'Is you don\'t have to stand alone', ['I said "I\'m fine"', "when I heard stage four."], '#ffbf9c',
  "I said \"I'm fine\" when I heard stage four #Shorts", "It's okay to not be okay. There is still love in people.", "it's okay to not be okay, mental health song, orchestral ballad"),
 ('im_a_witness', "I'm a Witness", 'ImAWitness', "I don't know how much time", "I'm a witness, I'm a witness to the light", ["They wrote me down in numbers.", "The numbers didn't know."], '#ff4fae',
  "They wrote me down in numbers. The numbers didn't know. 🙏 #Shorts", "What a mother's prayers can carry, and how far a heart can go.", 'gospel, testimony song, faith song'),
 ('remember_me_when_im_gone', "Remember Me When I'm Gone", 'RememberMeWhenImGone', "So if you're missing me", "That's what I was here for", ["When I'm gone,", "do this one thing for me."], '#f6dcef',
  "When I'm gone, do this one thing for me #Shorts", "Find somebody who is hurting. Leave them better than before.", 'memorial song, funeral song, grief song'),
 ('my_word_wont_die', "My Word Won't Die", 'MyWordWontDie', 'Back in 2022', 'Still the guy you came to see', ["My family could only see me", "through a screen."], '#f6e3bc',
  "My family could only see me through a screen #Shorts", "They counted my days, so I made the days count.", 'family song, promise song, keep your word'),
 ('dying_to_live', 'Dying to Live', 'DyingToLive', 'Then I looked at my family', 'I was living to die, now', ["I never promised I'd beat it.", "I swore I'd fight it."], '#b4f24c',
  "I never promised I'd beat it. I swore I'd fight it. #Shorts", "I stopped begging for more time and started giving time more life.", 'fight song, promise, never give up'),
 ('embrace_every_scar', 'Embrace Every Scar', 'EmbraceEveryScar', "There's a scar upon my chest", 'Even though it hurts', ["My port scar is a stamp", "in my passport."], '#d0b8ff',
  "My port scar is a stamp in my passport #Shorts", "The pain is just proof you're alive.", 'scars, port scar, healing song'),
 ('live_now_die_later', 'Live Now, Die Later', 'LiveNowDieLater', "There's a tattoo on my arm", 'Both of them are true', ["Most tattoos say", "smile now, cry later."], '#c4ebff',
  "Not smile now, cry later. Live now, die later. #Shorts", "Both the masks are part of living. Both of them are true.", 'tattoo, two masks, Scandinavian folk'),
 ('a_seat_at_the_table', 'A Seat at the Table', 'ASeatAtTheTable', "They don't talk about the hard parts", "So we'll sing for 'em together", ["Whiskey or water,", "raise it for who you miss."], '#35d47d',
  "Whiskey or water, raise it for who you miss 🥃 #Shorts", "They're never gone while we're reminiscing.", 'Irish folk, pub song, toast song'),
 ('quiet_fire', 'Quiet Fire', 'QuietFire', 'Folks look to the stage', 'And I drew up a future', ["The hardest fights", "get fought in quiet places."], '#ff8a2a',
  "The hardest fights get fought in quiet places 🔥 #Shorts", "Kitchen tables. Hospital chairs. The cab of a truck at two in the morning.", 'underdog song, quiet strength, small town'),
 ('from_where_i_stand', 'From Where I Stand', 'FromWhereIStand', 'Life is ten percent', 'Still standing, here I am', ["You see a nine.", "I see a six."], '#e9d9a6',
  "You see a nine. I see a six. #Shorts", "I can't control the weather, but I can choose the way I stand.", 'perspective, mindset, still standing'),
 ('only_the_strong_survive', 'Only The Strong Survive', 'OnlyTheStrongSurvive', 'So I took the mask off', 'And strong is being me', ["Only the strong survive.", "But strong was never steel."], '#ff4a4a',
  "Only the strong survive. But strong was never steel. #Shorts", "It's the hand that reaches out and the courage to be real.", 'take the mask off, men mental health, strength'),
 ('we_die_before_we_quit', 'We Die Before We Quit', 'WeDieBeforeWeQuit', 'You can pump the poison', 'But we are built to', ["Let it take my body.", "It can't take my soul."], '#ff3640',
  "Let it take my body. It can't take my soul. 🥊 #Shorts", "The first song I ever made.", 'motivational rap, battle cry, warrior mindset'),
 ('make_your_time_count', 'Make Your Time Count', 'MakeYourTimeCount', 'Some folks are like a rooster', 'So make your time count', ["Some folks are roosters.", "The real ones are the sunrise."], '#f2a88a',
  "Some folks are roosters. The real ones are the sunrise. 🌅 #Shorts", "Quality over quantity. Pick the friends who come around.", 'real friends, quality over quantity, advice song'),
 ('footprints_of_gold', 'Footprints of Gold', 'FootprintsOfGold', 'Some nights it was a couch', 'So leave footprints of gold (footprints of gold, footprints', ["The gold ain't in your pocket.", "It's what you leave behind."], '#f4c23c',
  "The gold ain't in your pocket ✨ #Shorts", "Every little kindness leaves a step that glows.", 'kindness, pay it forward, be there for people'),
 ('shout_yes', 'Shout Yes', 'ShoutYes', 'When my father passed', 'But it got my feet', ["When my father passed,", "I chose one word."], '#4fe3ff',
  "When my father passed, I chose one word: yes #Shorts", "Feet on the floor, arms in the air.", 'morning motivation, grief, say yes'),
]


def window(slug, a, b):
    r = subprocess.run(['python3', '/home/claude/scripts/find_seg.py', slug, a, b], capture_output=True, text=True, check=True).stdout
    head = r.split('\n')[0]
    s, e = head.split(': ')[1].split('  ')[0].split(' -> ')
    return float(s), float(e)


BASE = 'music, new song, lyrics, lyric video, songs about cancer, cancer survivor song, songs about hope, inspirational songs, shorts'
items = []
for n, (slug, name, tag, a, b, hook, acc, title, line, spec_tags) in enumerate(S, 1):
    s, e = window(slug, a, b)
    fn = f'{n:02d}_{tag}_Short.mp4'
    tn = name.replace(',', '')
    tags = f'{tn}, {tn} Zachary Patzer, Zachary Patzer, Zachary Patzer shorts, {spec_tags}, {BASE}'
    assert len(tags) < 500 and len(title) <= 100, slug
    desc = f'{name} (Remastered) by Zachary Patzer. Full lyric video on my channel.\n{line}\n\n#{tag} #ZacharyPatzer #shorts #cancersurvivor'
    items.append(dict(n=n, slug=slug, name=name, start=s, end=e, hook=hook, accent=acc, file=f'{OUT}/{fn}', title=title, desc=desc, tags=tags))
json.dump(items, open(f'{OUT}/plan.json', 'w'), indent=1)
for it in items:
    print(f"{it['n']:2d} {it['name']:28s} {it['start']:7.2f}-{it['end']:7.2f} {it['end'] - it['start']:5.1f}s")

if '--render' in sys.argv:
    def job(it):
        if os.path.exists(it['file']):
            return it['file'] + ' (exists)'
        r = subprocess.run(['python3', '/home/claude/scripts/make_short_v2.py', it['slug'], f"{it['start']:.2f}", f"{it['end']:.2f}", it['file']]
                           + it['hook'] + ['--accent', it['accent']], capture_output=True, text=True)
        return (r.stdout.strip() or r.stderr.strip()[-300:])
    with ThreadPoolExecutor(2) as ex:
        for res in ex.map(job, items):
            print(res, flush=True)
    print('ALLDONE', flush=True)
