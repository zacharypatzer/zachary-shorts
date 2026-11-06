"""Shorts for the six new core songs (Nov 2026), to fill the slots left by the removed songs.
V2: (slug, name, start, end, hook1, hook2)  -> make_short_v2.py (5:30 PM daily and 12 PM story slots)
QH: (slug, name, start, end, small_line, BIG_LINE, payoff_key) -> make_quick_hook.py (3 PM slot)"""

ACCENT = {
    'accidental_motivation': '#8fb6ff',
    'thats_up': '#5ab4ff',
    'how_you_come_back': '#f2b552',
    'hold_it_lightly': '#ffb36b',
    'what_im_livin': '#ffcf7a',
    'im_fine': '#7fb0ff',
}
TITLE = {
    'accidental_motivation': 'Accidental Motivation',
    'thats_up': "That's Up",
    'how_you_come_back': 'How You Come Back',
    'hold_it_lightly': 'Hold It Lightly, Love It Hard',
    'what_im_livin': "What I'm Livin'",
    'im_fine': "I'm Fine",
}

V2 = [
    ('accidental_motivation', 'N_am_1', 2.5, 37, "You don't know me,", "but your thumb just stopped."),
    ('accidental_motivation', 'N_am_2', 65.5, 110.5, '3 a.m.', 'The ceiling fan and me.'),
    ('accidental_motivation', 'N_am_3', 114.5, 150.5, 'A nurse. A kid. A dad.', 'Same night. Same screen.'),
    ('accidental_motivation', 'N_am_4', 150, 187.5, 'A hundred "me too"s.', "You're not the only one up."),
    ('accidental_motivation', 'N_am_5', 186.5, 228, 'Passin\' it on', "without even tryin'."),

    ('thats_up', 'N_tu_1', 5.5, 50.5, 'My body gets a vote', "every morning."),
    ('thats_up', 'N_tu_2', 32, 72.5, '20 minutes now', 'to do what took me 2.'),
    ('thats_up', 'N_tu_3', 124.5, 167.5, 'Nobody hands out medals', 'for the mornings you got through.'),
    ('thats_up', 'N_tu_4', 166.5, 194, "The hurtin' ain't a contest.", 'Your little things are real.'),
    ('thats_up', 'N_tu_5', 193.5, 234.5, 'He counts to three out loud.', 'His little girl is watching.'),

    ('how_you_come_back', 'N_hy_1', 14.5, 47.5, 'Sitting in the driveway.', "The call's already done."),
    ('how_you_come_back', 'N_hy_2', 40.5, 75, 'Get up scared.', 'Get up shaking.'),
    ('how_you_come_back', 'N_hy_3', 78.5, 111.5, 'Nobody waits', "until they're brave."),
    ('how_you_come_back', 'N_hy_4', 143.5, 178.5, 'A stranger shaking', 'in the waiting room chair.'),
    ('how_you_come_back', 'N_hy_5', 170.5, 215.5, 'Endurance counts the days.', 'Resilience is how you come back.'),

    ('hold_it_lightly', 'N_hl_1', 21.5, 50, 'They read my chart', 'in a quiet voice.'),
    ('hold_it_lightly', 'N_hl_2', 50.5, 92.5, 'Nothing here', 'was ever ours.'),
    ('hold_it_lightly', 'N_hl_3', 100.5, 130.5, "You're carrying tomorrow", 'on a back built for today.'),
    ('hold_it_lightly', 'N_hl_4', 169.5, 207.5, 'I lost the hair. The strength.', 'Not the way I love.'),
    ('hold_it_lightly', 'N_hl_5', 206.5, 243.5, 'Laugh out loud', 'in the waiting room.'),

    ('what_im_livin', 'N_wl_1', 32.5, 59.5, "I been takin' notes on life", 'for twenty years.'),
    ('what_im_livin', 'N_wl_2', 58.5, 85.5, "It ain't my voice you're hearin'.", "It's every bit my life."),
    ('what_im_livin', 'N_wl_3', 84.5, 118.5, "Saw folks cryin' in the hallway.", "Heard 'em prayin' through the wall."),
    ('what_im_livin', 'N_wl_4', 156.5, 183.5, "Folks think I'm here 'cause I'm tough.", "I'm just here."),
    ('what_im_livin', 'N_wl_5', 183.5, 216.5, 'Wear your own shoes.', "Your style is what you're livin'."),

    ('im_fine', 'N_if_1', 14.5, 48.5, 'I said it in the chemo chair.', 'Two words: "I\'m fine."'),
    ('im_fine', 'N_if_2', 40.5, 72, 'Two little words', 'to hide behind.'),
    ('im_fine', 'N_if_3', 76.5, 111.5, "Years since the last bell rang.", 'They think the hard part\'s done.'),
    ('im_fine', 'N_if_4', 138.5, 172.5, 'Some days pain. Some days tired.', "Some days I just don't know."),
    ('im_fine', 'N_if_5', 185.5, 217, 'How you doin\'?', 'No, really. How you doin\'?'),
]

QH = [
    ('accidental_motivation', 'QN_am_A', 36.8, 50.4, 'They say watching me keeps them going.', 'I CALL IT ACCIDENTAL.', 'A'),
    ('accidental_motivation', 'QN_am_B', 44, 58.6, 'Stop counting what\'s left.', 'COUNT WHAT\'S BEHIND YOU.', 'C'),
    ('accidental_motivation', 'QN_am_C', 212.6, 227.8, 'You might be somebody\'s reason', 'WITHOUT EVEN TRYING.', 'C'),

    ('thats_up', 'QN_tu_A', 75.8, 87.5, 'However small it looks,', 'IF IT TOOK YOUR ALL, THAT\'S ENOUGH.', 'C'),
    ('thats_up', 'QN_tu_B', 178.5, 186.5, 'Hurting is not a contest.', 'YOUR LITTLE THINGS ARE REAL.', 'C'),
    ('thats_up', 'QN_tu_C', 58.6, 72.5, 'Not okay. Not done.', 'BUT I\'M UP.', 'A'),

    ('how_you_come_back', 'QN_hy_A', 59.6, 74.2, 'Scared is not', 'THE SAME AS STUCK.', 'C'),
    ('how_you_come_back', 'QN_hy_B', 170.8, 182.4, 'Endurance counts the days.', 'RESILIENCE COMES BACK.', 'B'),
    ('how_you_come_back', 'QN_hy_C', 104.6, 117.6, 'Nobody waits until they\'re brave.', 'MOVE SCARED ANYWAY.', 'C'),

    ('hold_it_lightly', 'QN_hl_A', 58.6, 71.4, 'Every breath. Every scar.', 'HOLD IT LIGHTLY. LOVE IT HARD.', 'B'),
    ('hold_it_lightly', 'QN_hl_B', 108.6, 122.4, 'Carrying tomorrow', 'ON A BACK BUILT FOR TODAY.', 'C'),
    ('hold_it_lightly', 'QN_hl_C', 192.6, 207.4, 'Fear can sit next to me.', 'IT DOESN\'T DRIVE.', 'A'),

    ('what_im_livin', 'QN_wl_A', 71.6, 85.2, 'Not my voice.', 'EVERY BIT MY LIFE.', 'B'),
    ('what_im_livin', 'QN_wl_B', 156.6, 170.4, 'They think I\'m tough.', 'I\'M JUST HERE.', 'A'),
    ('what_im_livin', 'QN_wl_C', 104.6, 118.4, 'Every morning I check', 'WHAT\'S BROKE, WHAT WORKS.', 'B'),

    ('im_fine', 'QN_if_A', 48.6, 62.4, 'Two little words', 'TO HIDE BEHIND.', 'C'),
    ('im_fine', 'QN_if_B', 185.6, 202.4, 'If you said "I\'m fine" today,', 'YOU\'RE NOT THE ONLY ONE.', 'C'),
    ('im_fine', 'QN_if_C', 80.6, 91.4, 'My legs give out by noon.', 'I DON\'T TELL ANYONE.', 'B'),
]
