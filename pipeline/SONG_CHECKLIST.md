# Zachary's New-Song Checklist (fine-tooth comb)

Every lesson from every past rating, fix and rewrite, in one place.
A new song is NOT ready until every box below passes. Fix problems first; don't just list them.

Step 1 is automatic: `python3 scripts/lyric_check.py draft.txt "Title" songs --style style.txt --exclude exclude.txt`
Everything it prints under **FIX** must be fixed. Then walk the manual boxes below.

---

## A. The stranger test (most important)
Read it as someone who has never heard of Zachary.
- [ ] Would a stranger who never had cancer still feel it's about *them*? (I'm Fine, That's Up, Lion's Heart score highest with strangers.)
- [ ] Does any line need backstory to make sense? (Say Thank You For Me needs the Facebook story; "ain't me singin'" confuses strangers.) If yes, explain it inside the song or cut it.
- [ ] Is it about the listener, not just Zachary? Point the song at them by the end.
- [ ] Could someone retell the story in two sentences after one listen?

## B. Intro and hook
- [ ] The first line makes you NEED the next one: a mystery, a jolt or a question. A scene description is not a hook.
- [ ] Something musical or the hook lands in the first 3-5 seconds. No long slow a cappella or spoken build unless it's a quiet song by design.
- [ ] The ending pays off the intro (Take a Number's ticket #99, I'm Fine's "how you doin'?").

## C. One idea, one image
- [ ] One central image carries the whole song (death in the lobby, paper lanterns, the full glass).
- [ ] Only one big idea. "Too many ideas at once" is the #1 reason songs scored low (Island Time, Make Your Time Count, Quiet Fire).
- [ ] No verse that's just a list of people/things unless each item builds (Pour One More verse 2 problem).
- [ ] No verse that wanders off topic or feels like it came from another song (Live Now, Die Later's "bones as heavy as lead" part).
- [ ] No filler verse (I Live On Through You's iced-coffee verse).

## D. Chorus
- [ ] One big line anyone can say back, memorable enough to take away alone.
- [ ] The chorus moves the song by itself, even without the verses.
- [ ] End words actually rhyme. Loose chorus rhymes (believin'/seein'/livin'/singin') were what held What I'm Livin' at 8.
- [ ] No vague lines ("it truly has me believin' that it really is what I'm seein'"). Every chorus line says something concrete.
- [ ] The hook isn't repeated so much it washes the rest of the song out (the "still here" problem).

## E. Every line
- [ ] Every line is a complete thought. No unfinished lines ("the ones we didn't get to say").
- [ ] Every rhyme lands. No forced rhymes or rhyming a word with itself ("ends/ends").
- [ ] No clunky phrasing or words stuffed in to fit ("grievance-free state of achievement").
- [ ] Show, don't explain. Don't name the feeling; show what it does ("the flat tire got real small real quick").
- [ ] No clichés (the checker has a list; also watch for anything that "sounds familiar").
- [ ] No preachy advice lists or calls-to-action that read like a sermon (Footprints of Gold, Light One's last section).
- [ ] No borrowed sayings or famous quotes (10%/90%, "empty your cup", 6-and-9).
- [ ] Nothing that's merely "fine". Check intro, every verse, bridge AND outro. Outros got missed before (I'm Fine, Say Thank You For Me).
- [ ] Read every line OUT LOUD the way it'll be sung. A great true story can still have a line that sounds off: too long, too graphic, or accidentally funny (Embrace Every Scar's "bicep... rolled up in my armpit like a window shade" got praised for the story but sounds off sung). Rate the line, not just the story.
- [ ] Lines sound like how people actually talk ("pour a double out for me", "maybe even two").

## F. Message safety
- [ ] No promises (his rule). Use "hopin'", not "I will/I promise". Also no "promise me" asks.
- [ ] Nothing implies people who died were weak ("only the strong survive", "the weak pass the blame"). Holding on or letting go both take strength.
- [ ] Story logic holds: nothing contradicts the payoff; facts are true (whales can't fly; don't guess why he rang the bell three times).
- [ ] No Spanish lines.
- [ ] No father's passing, no buggy/braces/gear details unless he asks (they throw off the vibe).

## G. Fresh for his catalog
- [ ] Zero recycled 4-word phrases (checker).
- [ ] No overused catalog themes: promising his family he wouldn't quit; walking/miles/steps (A Mile An Hour owns it); screen door / zoo visits; smiling to hide pain (5 songs already); ringing the bell (only if new angle).
- [ ] New genre, not the style of the song he just made.
- [ ] Still sounds like him: plain, rhyming real talk; dropped g's; his own words where possible ("Doorframe" was rejected as not him).

## H. Built for Suno
- [ ] Style box includes `clear enunciation`; Exclude box includes `static`.
- [ ] Style matches the message (quiet song starts small; party song starts big). Add `slow spoken intro` only when the intro must not be rushed.
- [ ] Musical cues written into section tags so Suno builds (e.g. `[Final Chorus - full band, key change]`).
- [ ] Section tags stay short; long descriptive tags act like a second Style box.
- [ ] Lines in each section have similar syllable counts (checker `!` flags) so Suno doesn't cram or stretch.
- [ ] Few mid-line commas; Suno pauses at each one and goes choppy.
- [ ] No words Suno's filter blocks (skank, brand names, delete/block/algorithm) and no lines close to famous song titles ("a man my size don't cry").
- [ ] Hard words spaced if Suno may slur them ("dis-play-in'").
- [ ] Under 5,000 characters; title sung 10+ times.

## I. After Suno (before anything goes out)
- [ ] Compare Suno's vocal to the lyrics: changed, dropped or mushed lines get fixed by a new take or noted for him.
- [ ] The intro of the take hooks (make-or-break). Generate 2-3 takes; keep the one with the best intro and the one that still moves you with vocals down.
- [ ] Full pre-release check: audio level, lyric video sync, thumbnail (readable at phone size, bold high-contrast font, different from recent ones), title/tags/description, Facebook post (template, under 400 chars), Metricool post.

## J. Rating
- [ ] Give an honest rating three ways: lyrics, stranger view, and what the Suno take adds.
- [ ] Name the weakest remaining line. Ready only when nothing weak is left.
