# Zachary Patzer – master catalog (where everything lives)

Updated Nov 16, 2026. Paths are inside this repo (`pipeline/`). Drive = private folder "Zachary Song Backup" (id `1Wr4SVfgp8hZKFQTFkZcAn-t3Cy9R6JkH`); MP3 ids open with Google Drive download_file_content.

- **MP3s**: Drive only (repo is public, never put audio here).
- **Lyrics as sung**: `songs/<slug>/lyrics.txt`; word timings `songs/<slug>/lyrics_final.json` (or `aligned.json`).
- **Artwork**: released/new songs `out/<Title>_Cover.jpg`, `_Thumbnail.jpg`, `_Facebook_Vertical.jpg`; square covers `qh/covers/<slug>.jpg`; Drive-take covers are rebuilt from `drive_versions/scenes/<slug>.jpg` + `scripts/cover_generic.py` (config `covers_cfg/`); early-take covers = `qh/covers/<slug>.jpg` + `scripts/take_cover.py` badge.
- **MP4 lyric videos**: released songs are on YouTube @zacharypatzer. Drive/early-take videos were sent in chat on Nov 16, 2026 (Drive folder "Lyric Videos" id `1vM0ChQnyB8X59E226k0lO7mpNmx4GRkD`, if saved there). Any video can be rebuilt in ~5 min: restore.sh, download the MP3, then `scripts/drive_build.sh <slug> "<palette>"` (palette in `scripts/prep_song.py` PAL).
- Lines still to check by ear: `drive_versions/REVIEW.md`.

## Released and new songs (final versions) (50)

| Song | Folder | MP3 (Drive id) | Artwork |
|---|---|---|---|
| A Mile An Hour | `songs/a_mile_an_hour` | `1kXf7pi71JRZoVyFxYqIdJ_nR3AuZKlj6` (A Mile An Hour (Remastered) (3).mp3) | out/A_Mile_An_Hour_Thumbnail.jpg, out/A_Mile_An_Hour_Facebook_Vertical.jpg, qh/covers/a_mile_an_hour.jpg |
| A Seat at the Table | `songs/a_seat_at_the_table` | `1ofsOs9j6Rv7439FxY40yoVGYQHfjySe9` (A Seat at the Table (Remastered) (1).mp3) | out/A_Seat_at_the_Table_Thumbnail.jpg, out/A_Seat_at_the_Table_Facebook_Vertical.jpg, qh/covers/a_seat_at_the_table.jpg |
| Accidental Motivation | `songs/accidental_motivation` | `1idFKxyFX-pLHt1w2tynPoqXnj25LS7tQ` (Accidental Motivation (Remastered).mp3) | out/Accidental_Motivation_Cover.jpg, out/Accidental_Motivation_Facebook_Vertical.jpg, out/Accidental_Motivation_Thumbnail.jpg |
| Beautiful Anyway | `songs/beautiful_anyway` | `14wX_4vXSpO6AikxHFHCHqVoNTLM-JJSt` (Beautiful Anyway (Remastered) (3).mp3) | out/Beautiful_Anyway_Facebook_Vertical.jpg, out/Beautiful_Anyway_Thumbnail.jpg, qh/covers/beautiful_anyway.jpg |
| Lost It in the Paperwork | `songs/count_the_arms_you_hold` | `1BK0exhIW2k5Gc6Cg9nQn31RZO_scMVLc` (Count the Arms You Hold (Remastered).mp3) | out/Lost_It_in_the_Paperwork_Facebook_Vertical.jpg, out/Lost_It_in_the_Paperwork_Cover.jpg, out/Lost_It_in_the_Paperwork_Thumbnail.jpg |
| Dying to Live | `songs/dying_to_live` | `1P8ow8hJ1Q32iwRR6Wrw8fQ8sTkMIpgg1` (Dying to Live (Remastered) (1).mp3) | out/Dying_to_Live_Thumbnail.jpg, out/Dying_to_Live_Facebook_Vertical.jpg, qh/covers/dying_to_live.jpg |
| Embrace Every Scar | `songs/embrace_every_scar` | `1wQV4qGWCRMF1C1zLidt7-A9gYeG8YteL` (Embrace Every Scar (Remastered) (5).mp3) | out/Embrace_Every_Scar_Thumbnail.jpg, out/Embrace_Every_Scar_Facebook_Vertical.jpg, qh/covers/embrace_every_scar.jpg |
| Even If We Stumble | `songs/even_if_we_stumble` | `1dEjxUN0l4g1hdevnuc4Odpdxou6wajra` (Every Other Week (Remastered) (1).mp3) | out/Even_If_We_Stumble_Facebook_Vertical.jpg, out/Even_If_We_Stumble_Thumbnail.jpg, qh/covers/even_if_we_stumble.jpg |
| Floor of Shadows | `songs/floor_of_shadows` | `1IATPJMY0mdORZpC09PvSM7Lu_GEarCNs` (The Floor of Shadows (Remastered) (1).mp3) | out/Floor_of_Shadows_Facebook_Vertical.jpg, out/Floor_of_Shadows_Thumbnail.jpg, qh/covers/floor_of_shadows.jpg |
| Footprints of Gold | `songs/footprints_of_gold` | `1iGSwmvjoF57QnvAbLje9sWqcQNVyjBXE` (Footprints of Gold (Remastered) (5).mp3) | out/Footprints_of_Gold_Thumbnail.jpg, out/Footprints_of_Gold_Facebook_Vertical.jpg, qh/covers/footprints_of_gold.jpg |
| From Where I Stand | `songs/from_where_i_stand` | `1U0C4ppWEgug2J1luCcOe2afEcP3ENkpk` (From Where I Stand (Remastered) (2).mp3) | out/From_Where_I_Stand_Facebook_Vertical.jpg, out/From_Where_I_Stand_Thumbnail.jpg, qh/covers/from_where_i_stand.jpg |
| Giving Time More Life | `songs/givin_time_more_life` | `19iJWXcO3wpLIgA4vCx13XoX3ENualqok` (Givin' Time More Life (Remastered).mp3) | out/Giving_Time_More_Life_Facebook_Vertical.jpg, out/Giving_Time_More_Life_Thumbnail.jpg, out/Giving_Time_More_Life_Cover.jpg |
| Glad You're Here | `songs/glad_youre_here` | `1otWb_Yqsv5lIOuK4WwsEAV87BF1R7Ez_` (Glad You're Here (Remastered) (1).mp3) | out/Glad_Youre_Here_Cover.jpg, out/Glad_Youre_Here_Facebook_Vertical.jpg, out/Glad_Youre_Here_Thumbnail.jpg |
| Hold It Lightly, Love It Hard | `songs/hold_it_lightly` | `1UQPxWMnVIgumYBZ5vdTkjaBVUmrarrIb` (Hold It Lightly, Love It Hard (Remastered).mp3) | out/Hold_It_Lightly_Love_It_Hard_Cover.jpg, out/Hold_It_Lightly_Love_It_Hard_Facebook_Vertical.jpg, out/Hold_It_Lightly_Love_It_Hard_Thumbnail.jpg |
| How You Come Back | `songs/how_you_come_back` | `15hP4C3JH-nfsjZbfrlVYQiQ_cd6pCdhJ` (How You Come Back (Remastered) (1).mp3) | out/How_You_Come_Back_Cover.jpg, out/How_You_Come_Back_Facebook_Vertical.jpg, out/How_You_Come_Back_Thumbnail.jpg |
| I Live On Through You | `songs/i_live_on_through_you` | `1IJeODhALu04wnNeGiCC15waocqi1oLgl` (Live On Through You (Remastered) (3).mp3) | out/I_Live_On_Through_You_Facebook_Vertical.jpg, out/I_Live_On_Through_You_Thumbnail.jpg, qh/covers/i_live_on_through_you.jpg |
| I See You | `songs/i_see_you` | `12q71c3b49uxDk2KHKETSuKTIDh4Whuvq` (I See You  (Remastered) (1).mp3) | out/I_See_You_Cover.jpg, out/I_See_You_Thumbnail.jpg, out/I_See_You_Facebook_Vertical.jpg |
| If We Can, We Do | `songs/if_we_can_we_do` | `1Fs_bP3-rnvQMqAep-KjB5JocpWA2NGJT` (If We Can, We Do (Remastered).mp3) | out/If_We_Can_We_Do_Thumbnail.jpg, out/If_We_Can_We_Do_Cover.jpg, out/If_We_Can_We_Do_Facebook_Vertical.jpg |
| I'm a Witness | `songs/im_a_witness` | `1D9GrVIfShtxnHqqUK7-0nCV_t7bB1Sqt` (I'm a Witness (Remastered) (2).mp3) | out/Im_a_Witness_Thumbnail.jpg |
| I'm Fine | `songs/im_fine` | `18q1aKLE8doANYwK0WgFoafB8M4wdevT7` (I'm Fine (Remastered) (1).mp3) | out/Im_Fine_Cover.jpg, out/Im_Fine_Thumbnail.jpg |
| Good for It | `songs/im_good_for_it` | `10fbj8Ev0jOfp08sGWtUXpHd9Mo4tSB8N` (I'm Good for It (Remastered).mp3) | out/Good_for_It_Thumbnail.jpg, out/Good_for_It_Cover.jpg, out/Good_for_It_Facebook_Vertical.jpg |
| Island Time | `songs/island_time` | `1cyEAKZMG7QNB7grJf2xo9TBIBQrzax4G` (Island Time (Remastered) (2).mp3) | out/Island_Time_Thumbnail.jpg, out/Island_Time_Facebook_Vertical.jpg, qh/covers/island_time.jpg |
| It's Your Birthday | `songs/its_your_birthday` | `1UQKhzFuyzLZMGr33rBJY_hFdRWJRjBH_` (It's Your Birthday (Remastered) (1).mp3) | out/Its_Your_Birthday_Facebook_Reel_Cover.jpg, out/Its_Your_Birthday_Cover.jpg, out/Its_Your_Birthday_Share_Card.jpg, out/Its_Your_Birthday_Facebook_Vertical.jpg |
| Just a Nod | `songs/just_a_nod` | `1PK3Ih1FcTII1vWu-OREybvnoGPuCbqsa` (Just a Nod (Remastered).mp3) | out/Just_a_Nod_Cover.jpg, out/Just_a_Nod_Thumbnail.jpg, out/Just_a_Nod_Facebook_Vertical.jpg |
| Light One, Let It Go | `songs/light_one_let_it_go` | `1bP9c5RbQ1jgxzGN4dAuAvh5aQoGPdRO_` (Light One, Let It Go (Remastered) (2).mp3) | out/Light_One_Let_It_Go_Thumbnail.jpg, out/Light_One_Let_It_Go_Facebook_Reel_Cover.jpg, qh/covers/light_one_let_it_go.jpg |
| Lion's Heart | `songs/lions_heart` | `1s-QUDt6Rskez0FZFeDQPMcffiikfIRe-` (Lion's Heart (Remastered) (1).mp3) | out/Lions_Heart_Thumbnail.jpg, out/Lions_Heart_Facebook_Vertical.jpg, out/Lions_Heart_Cover.jpg, qh/covers/lions_heart.jpg |
| Live Now, Die Later | `songs/live_now_die_later` | `1XPqhV-0GO2L2kVB1O7oFsGBtsseCpyQU` (Live Now, Die Later (Remastered) (2).mp3) | out/Live_Now_Die_Later_Facebook_Vertical.jpg, out/Live_Now_Die_Later_Thumbnail.jpg, qh/covers/live_now_die_later.jpg |
| Living in the Echo | `songs/living_in_the_echo` | `1DfyJifUTlh0NOu_e0GhLpwJcJKiQu6uR` (Living in the Echo (Remastered) (3).mp3) | out/Living_in_the_Echo_Thumbnail.jpg, out/Living_in_the_Echo_Facebook_Reel_Cover.jpg, qh/covers/living_in_the_echo.jpg |
| Make Your Time Count | `songs/make_your_time_count` | `1RcY-sxr21S5Mwqkvw3y-z2TeGo9FXzj9` (Make Your Time Count (Remastered) (1).mp3) | out/Make_Your_Time_Count_Facebook_Vertical.jpg, out/Make_Your_Time_Count_Thumbnail.jpg, qh/covers/make_your_time_count.jpg |
| My Word Won't Die | `songs/my_word_wont_die` | `1kiEjzzw_Wj4MpwAx9XxWgnnH_JsNr4my` (My Word Won't Die (Remastered) (2).mp3) | out/My_Word_Wont_Die_Thumbnail.jpg, out/My_Word_Wont_Die_Facebook_Vertical.jpg, qh/covers/my_word_wont_die.jpg |
| No Complaints | `songs/no_complaints` | `1HIHyMuVx96B1c_3LOZpNc3cirm-Wnxth` (Timer in My Legs (Remastered) (2).mp3) | out/No_Complaints_Facebook_Vertical.jpg, out/No_Complaints_Thumbnail.jpg, qh/covers/no_complaints.jpg |
| Only The Strong Survive | `songs/only_the_strong_survive` | `1XmA0at-5DVYfaCoPLsE3GI9FBW8Mgbwq` (Only The Strong Survive (Remastered) (5).mp3) | out/Only_The_Strong_Survive_Facebook_Vertical.jpg, out/Only_The_Strong_Survive_Thumbnail.jpg, qh/covers/only_the_strong_survive.jpg |
| Pray for Somebody Else | `songs/pray_for_somebody_else` | `1VQGutNKcub7QXarw3os6zWte_CxRWqVi` (Pray for Somebody Else (Remastered).mp3) | out/Pray_for_Somebody_Else_Cover.jpg, out/Pray_for_Somebody_Else_Facebook_Vertical.jpg, out/Pray_for_Somebody_Else_Thumbnail.jpg |
| Put It Together | `songs/put_it_together` | `1SAiRSTnzueAxUqz4TLVKpTmguEJQPFUM` (Put It Together (Remastered).mp3) | out/Put_It_Together_Cover.jpg, out/Put_It_Together_Thumbnail.jpg, out/Put_It_Together_Facebook_Vertical.jpg |
| Quiet Fire | `songs/quiet_fire` | `1BVf3PiDnIyJKD00p_4iEPkFQ5FneNxMh` (Quiet Fire (Remastered) (2).mp3) | out/Quiet_Fire_Facebook_Vertical.jpg, out/Quiet_Fire_Thumbnail.jpg, qh/covers/quiet_fire.jpg |
| Remember Me When I'm Gone | `songs/remember_me_when_im_gone` | `1NH273fQ7vPiDNbw8dLJZ3PGl88mmPWUS` (Remember Me When I'm Gone (Remastered) (3).mp3) | out/Remember_Me_When_Im_Gone_Facebook_Reel_Cover.jpg, out/Remember_Me_When_Im_Gone_Thumbnail.jpg, qh/covers/remember_me_when_im_gone.jpg |
| Say It Like a Kid Would | `songs/say_it_like_a_kid_would` | `1kYVMrUcu7anLz7LrjDvBqm5qjlxEUUZ6` (Say It Like a Kid Would (Remastered).mp3) | out/Say_It_Like_a_Kid_Would_Facebook_Vertical.jpg, out/Say_It_Like_a_Kid_Would_Cover.jpg, out/Say_It_Like_a_Kid_Would_Thumbnail.jpg |
| Say Thank You For Me | `songs/say_thank_you_for_me` | `1UI66BCvdR43-fjPIErkGznyl_av6HsQI` (Say Thank You For Me (Remastered) (1).mp3) | out/Say_Thank_You_For_Me_Thumbnail.jpg, out/Say_Thank_You_For_Me_Cover.jpg, out/Say_Thank_You_For_Me_Facebook_Vertical.jpg |
| Shout Yes | `songs/shout_yes` | `1sKrK9W1hXbyTgex6K8g6-C-Z9M0LzdUu` (Feet on the Floor (Remastered) (2).mp3) | out/Shout_Yes_Thumbnail.jpg, out/Shout_Yes_Facebook_Vertical.jpg, qh/covers/shout_yes.jpg |
| Take a Number | `songs/take_a_number` | `1Py6hXP_ZLAUMhWDv64XvHDdvssWYxyXJ` (Take a Number (Remastered) (2).mp3) | out/Take_a_Number_Facebook_Vertical.jpg, out/Take_a_Number_Thumbnail.jpg, qh/covers/take_a_number.jpg |
| That'd Be Easy | `songs/thatd_be_easy` | `1YI4fZTLYxwmKSOkTKeRljNRyYlYIf1k1` (That'd Be Easy (Remastered).mp3) | out/Thatd_Be_Easy_Cover.jpg, out/Thatd_Be_Easy_Thumbnail.jpg |
| That's Up | `songs/thats_up` | `1e3SLPTTNWyjIpNhuFhwPp60cXIRgKikL` (That's Up (Remastered) (1).mp3) | out/Thats_Up_Thumbnail.jpg, out/Thats_Up_Cover.jpg |
| The Seventh Day | `songs/the_seventh_day` | `1-gL8ZSIewbMJhaSVLKrboQsVSx91LjPt` (The Seventh Day (Remastered) (1).mp3) | out/The_Seventh_Day_Facebook_Vertical.jpg, out/The_Seventh_Day_Facebook_Reel_Cover.jpg, out/The_Seventh_Day_Cover.jpg |
| The Sunrise Kind | `songs/the_sunrise_kind` | `1flYq-Wkuc2oAu5gCsHud_iUn6X4vQQ5s` (The Sunrise Kind (Remastered).mp3) | out/The_Sunrise_Kind_Cover.jpg, out/The_Sunrise_Kind_Thumbnail.jpg, out/The_Sunrise_Kind_Facebook_Vertical.jpg |
| People Rebuild | `songs/things_break_people_rebuild` | `10P8wHXQWC3kokZWC8mbDkcbRiwav_zCV` (Things Break, People Rebuild (Remastered).mp3) | out/People_Rebuild_Facebook_Vertical.jpg, out/People_Rebuild_Cover.jpg, out/People_Rebuild_Thumbnail.jpg |
| Unfinished | `songs/unfinished` | `1UhRowAX8l0DCpB6GD8h6WAh7oB5ZpHTV` (Unfinished (Remastered) (1).mp3) | out/Unfinished_Thumbnail.jpg, out/Unfinished_Cover.jpg, out/Unfinished_Facebook_Vertical.jpg, qh/covers/unfinished.jpg |
| We Die Before We Quit | `songs/we_die_before_we_quit` | `15zLWw6rlE1JdrA56kpNMGPwFLY4wtA0J` (We Die Before We Quit.mp3) | out/We_Die_Before_We_Quit_Facebook_Reel_Cover.jpg, out/We_Die_Before_We_Quit_v2_Facebook_Vertical.jpg, out/We_Die_Before_We_Quit_v2_Thumbnail.jpg, out/We_Die_Before_We_Quit_Thumbnail.jpg, qh/covers/we_die_before_we_quit.jpg |
| We Die Before We Quit (rewrite, on hold) | `songs/we_die_v2` (+ `hold/` Suno boxes) | `1kvjouuWyaK90Xxls4e8SiK7FRKK0v6Is` (We Die Before We Quit (Remastered) (12).mp3) | out/We_Die_Before_We_Quit_Facebook_Reel_Cover.jpg, out/We_Die_Before_We_Quit_v2_Facebook_Vertical.jpg, out/We_Die_Before_We_Quit_v2_Thumbnail.jpg, out/We_Die_Before_We_Quit_Thumbnail.jpg |
| What I'm Livin' | `songs/what_im_livin` | `1nV0E5ivdo0wVyHgUxwBxnpnlx5qkNv9F` (What I'm Livin' (Remastered).mp3) | out/What_Im_Livin_Cover.jpg, out/What_Im_Livin_Facebook_Vertical.jpg, out/What_Im_Livin_Thumbnail.jpg |
| Who You Stay For | `songs/who_you_stay_for` | `1a90L44h4NOIImtPB-nqSvlKhVoaoNS7m` (Who You Stay For (Remastered).mp3) | out/Who_You_Stay_For_Facebook_Vertical.jpg, out/Who_You_Stay_For_Cover.jpg, out/Who_You_Stay_For_Thumbnail.jpg |

## Drive takes (unreleased songs) (24)

| Song | Folder | MP3 (Drive id) | Artwork |
|---|---|---|---|
| A New God Rises | `songs/d_a_new_god_rises` | `1j5_Ppwt_nHUq8BuZJPHQEeCLLajgeMbs` | rebuild: drive_versions/scenes/d_a_new_god_rises.jpg |
| Beacon of Hope | `songs/d_beacon_of_hope` | `16DUKOb0x2HgkN8cnrD-_G1iUP--xb6uz` | rebuild: drive_versions/scenes/d_beacon_of_hope.jpg |
| Bleeding the Same | `songs/d_bleeding_the_same` | `1zwiOi1vaQTlfOgnT_w0GpjZCwFZwr2VI` | rebuild: drive_versions/scenes/d_bleeding_the_same.jpg |
| Bleeding the Same Red | `songs/d_bleeding_the_same_red` | `1wHl4PYUs19zXtdc6pvvhMxlGX8b58Tss` | rebuild: drive_versions/scenes/d_bleeding_the_same_red.jpg |
| Bloodline Endures | `songs/d_bloodline_endures` | `1mt_yMQj2oSmTIyuH6oWJI2Gy_r-WdAHE` | rebuild: drive_versions/scenes/d_bloodline_endures.jpg |
| Cancer Fighter | `songs/d_cancer_fighter` | `1iGFxtWUh8cWzM1Aj3sX0RR7Oryk0LbF1` | rebuild: drive_versions/scenes/d_cancer_fighter.jpg |
| Cancer Fighters Blueprint | `songs/d_cancer_fighters_blueprint` | `1Hf7B2DwCB2KgUOt592Y0pSBvaVVMthKe` | rebuild: drive_versions/scenes/d_cancer_fighters_blueprint.jpg |
| Empty Out the Cup | `songs/d_empty_out_the_cup` | `1DDuNQYtL0R9Z12_-m4ogjqisfaKV2QJe` | rebuild: drive_versions/scenes/d_empty_out_the_cup.jpg |
| Even If We Fall | `songs/d_even_if_we_fall` | `1daRIEEmZpxVrm8JNE_9s73ePWiROyIEu` | rebuild: drive_versions/scenes/d_even_if_we_fall.jpg |
| Intertwined Motivational Minds | `songs/d_intertwined_motivational_minds` | `1lIDYv18Glu4vU5msOCzyBn9d-LGyrSBR` | rebuild: drive_versions/scenes/d_intertwined_motivational_minds.jpg |
| Just Remember My Name | `songs/d_just_remember_my_name` | `1oVQrkEcm1R79JxtCALRBIT0kzO37meyV` | rebuild: drive_versions/scenes/d_just_remember_my_name.jpg |
| Keep On Breathing | `songs/d_keep_on_breathing` | `1lt5krDV-w2KMWccaKACZ6kc3RmcDd5wt` | rebuild: drive_versions/scenes/d_keep_on_breathing.jpg |
| Living 2 Die or Dying 2 Live | `songs/d_living_2_die` | `1SYkgDlbMGlX0PV3McJBCpnqGEnLpQxio` | rebuild: drive_versions/scenes/d_living_2_die.jpg |
| Lone Wolf Rising | `songs/d_lone_wolf_rising` | `1Rj6Lv2G84PFiMEM04AQmzEPUEhb19zsG` | rebuild: drive_versions/scenes/d_lone_wolf_rising.jpg |
| The Man Behind the Scenes | `songs/d_man_behind_the_scenes` | `1exQok490sd6Z0WNKYtU_w0l3GeIHqeyQ` | rebuild: drive_versions/scenes/d_man_behind_the_scenes.jpg |
| Maze Made the Man | `songs/d_maze_made_the_man` | `1A-R7Oxh9Eig793GhWissKqGGR7aAB88h` | rebuild: drive_versions/scenes/d_maze_made_the_man.jpg |
| Monsters Out of Shadows | `songs/d_monsters_out_of_shadows` | `1n3PVqKwWpuez87UYWKDXIOos_eO2pCq1` | rebuild: drive_versions/scenes/d_monsters_out_of_shadows.jpg |
| The Patzer Pro-Files | `songs/d_patzer_pro_files` | `1EVvBTB7g6-RhLfM8unF7_1FwgcfSingo` | rebuild: drive_versions/scenes/d_patzer_pro_files.jpg |
| Quality Over Quantity | `songs/d_quality_over_quantity` | `1ghra3O2qQB4kBcuBpxNoxjXeMSFsT8wt` | rebuild: drive_versions/scenes/d_quality_over_quantity.jpg |
| Stranger's Anchor | `songs/d_strangers_anchor` | `1iTeoooCrTMYUhR00TkB_1LpicggPnV0a` | rebuild: drive_versions/scenes/d_strangers_anchor.jpg |
| The Ink Is Setting | `songs/d_the_ink_is_setting` | `18zaNtGM0Tulh0biTrAG51W7FwzImN09W` | rebuild: drive_versions/scenes/d_the_ink_is_setting.jpg |
| Time Is the Currency | `songs/d_time_is_the_currency` | `1Ct84EAJafFbhJWY1-JxF8QmgaTbSpF6C` | rebuild: drive_versions/scenes/d_time_is_the_currency.jpg |
| True Strength Isn't Loud | `songs/d_true_strength` | `1EAslYTAbSXPiTknkn9aWnDxUGrsG9vjp` | rebuild: drive_versions/scenes/d_true_strength.jpg |
| Words Unspoken Remain Thoughts | `songs/d_words_unspoken` | `1N75LgHYDKf2tVeglP_nhsq6skbl81JoS` | rebuild: drive_versions/scenes/d_words_unspoken.jpg |

## Early takes of released songs (18)

| Song | Folder | MP3 (Drive id) | Artwork |
|---|---|---|---|
| Beautiful Anyway (Early Take) | `songs/o_beautiful_anyway` | `1LcatkCfrer-zNhfq1yIG1eY8PGfCmDIs` (Beautiful Anyway (Remastered) (3).mp3) | qh/covers/beautiful_anyway.jpg + badge |
| Embrace Every Scar (Early Take) | `songs/o_embrace_every_scar` | `1Gky4iE_y8PTJLHxJkhs7llAkszs-ZsUt` (Embrace Every Scar (Remastered).mp3) | qh/covers/embrace_every_scar.jpg + badge |
| Even If We Stumble (Early Take) | `songs/o_even_if_we_stumble` | `1XhuRaDrLAaXzfyzI_q_VCext944b6mtt` (Even If We Stumble  (Remastered).mp3) | qh/covers/even_if_we_stumble.jpg + badge |
| Floor of Shadows (Early Take) | `songs/o_floor_of_shadows` | `1wdTBZuhWJ07ZthPrPgOumZToU1sYlTAx` (Floor Of The Shadows  (Remastered).mp3) | qh/covers/floor_of_shadows.jpg + badge |
| Footprints of Gold (Early Take) | `songs/o_footprints_of_gold` | `1Dj7p70-L0vrBcnDsMwm2Y6pdebnuamod` (Footprints of Gold (Remastered) (4).mp3) | qh/covers/footprints_of_gold.jpg + badge |
| I Live On Through You (Early Take A) | `songs/o_i_live_on_through_you_1` | `1x-_e78xVp9IueGgzKWcnjmAwmfWCBm9C` (Live On Through You (Remastered).mp3) | qh/covers/i_live_on_through_you.jpg + badge |
| I Live On Through You (Early Take B) | `songs/o_i_live_on_through_you_2` | `1vsvieTtO5sTELXEz91D1GAIMCNIXVHT_` (Live On Through You (Remastered) (3).mp3) | qh/covers/i_live_on_through_you.jpg + badge |
| Live Now, Die Later (Early Take A) | `songs/o_live_now_die_later_1` | `1_P1a-oSLYFCrxkVkO3NqjkSOJ2opSame` (Live Now Die Later (Remastered).mp3) | qh/covers/live_now_die_later.jpg + badge |
| Live Now, Die Later (Early Take B) | `songs/o_live_now_die_later_2` | `1kOvAqHgvg8dIJ97E6irel4PtueaaVB-a` (Live Now, Die Later (Remastered) (2).mp3) | qh/covers/live_now_die_later.jpg + badge |
| Live Now, Die Later (Early Take C) | `songs/o_live_now_die_later_3` | `1H4Hi0U_ZGqiUsOXK9d6vBoVIJlgQFN6s` (Live Now Die Later  (Remastered).mp3) | qh/covers/live_now_die_later.jpg + badge |
| Only The Strong Survive (Early Take A) | `songs/o_only_the_strong_survive_1` | `19zksX2fYdYWoH0odIYM3ei_8KJG1WFCs` (Only The Strong Survive (Remastered) (4).mp3) | qh/covers/only_the_strong_survive.jpg + badge |
| Only The Strong Survive (Early Take B) | `songs/o_only_the_strong_survive_2` | `1mt2BSGxzbWjM8zc89kXQucLthSjUwDua` (Only The Strong Survive (Remastered).mp3) | qh/covers/only_the_strong_survive.jpg + badge |
| Only The Strong Survive (Early Take C) | `songs/o_only_the_strong_survive_3` | `1r-ixphKDjgc5IfSBhcCx2Q3i0i5-A2Lz` (Only The Strong Survive  (Remastered).mp3) | qh/covers/only_the_strong_survive.jpg + badge |
| Remember Me When I'm Gone (Early Take A) | `songs/o_remember_me_when_im_gone_1` | `14Y7hbpinZv3PYZKi57GyyP7WSN_Aynug` (Remember Me When I'm Gone (Remastered) (2).mp3) | qh/covers/remember_me_when_im_gone.jpg + badge |
| Remember Me When I'm Gone (Early Take B) | `songs/o_remember_me_when_im_gone_2` | `1nGPjSOgPZd6hV5TkSmVzrEymE2u-z5IA` (Remember Me When I'm Gone (So I Might Live On) (Remastered x2).mp3) | qh/covers/remember_me_when_im_gone.jpg + badge |
| Shout Yes (Early Take) | `songs/o_shout_yes` | `1-R83b9-gJEIhbdbf6-sfJmhxCYIJrI9v` (Shout Yes (Remastered).mp3) | qh/covers/shout_yes.jpg + badge |
| Take a Number (Early Take) | `songs/o_take_a_number` | `1NkBJ1kcOpDGntXT72fdkGgcOrCQgpaRn` (Take a Number (Remastered) (2).mp3) | qh/covers/take_a_number.jpg + badge |
| We Die Before We Quit (Early Take) | `songs/o_we_die_before_we_quit` | `1KPxCWJaPUNaejeFpza1Cy2sE5bnk2lIn` (We Die Before We Quit (Remastered).mp3) | qh/covers/we_die_before_we_quit.jpg + badge |

## Passed on / short songs (kept so they can be revisited)
| Song | Where | MP3 (Drive id) |
|---|---|---|
| Light the Way (Drive take) | `songs/d_light_the_way` (lyrics + timings, see PASSED_ON.md) | `1tKnfxsPjTsMfOY-gu3o2xDJ0zLnss1Bi` | (lyrics.txt = safe revision; old MP3 sings cautioned lines, never use)
| Follow Along | MP3 only (under 3 min) | `1IjX4Js6keQKODP4oaKaZ1hiD3Rm1HarJ` |
| Thank You for Joining | MP3 only (under 3 min) | `1yqsF9nMcqH1O-vdd5YdEUlKBqczkzWeo` |
| Living 2 Die (short take) | MP3 only (under 3 min) | `11z1EM4hj6RtOrkq02n4lmbCZaXtcCVZ-` |
| Tick Talk Whoa | MP3 only (viral edit sound) | `1yWgbOJQlmeTzLGxdPpu-BC9l5g6MoKmw` |
| That'd Be Easy (cleaned master) | `songs/thatd_be_easy` | `1qIfZ8JpO9zr-YD7__JRQzuSCVZuIyd5e` |

Removed songs (Quiet Fire, Shout Yes, No Complaints, Even If We Stumble, Unfinished, From Where I Stand, A Seat at the Table, I'm a Witness, What I'm Livin', That'd Be Easy, We Die Before We Quit and the 5+4 being replaced) keep their full folders above; nothing is deleted.
Song drafts that never went through Suno (People Rebuild drafts, Bury the Calendar, Pour One More, etc.) are in Claude's memory file `/areas/song-drafts.md` and past chats, by Zachary's choice not in this repo until a version works.
Ratings for all 75 songs: `RATINGS.md`.

## Not made (by choice)
- Light the Way Drive take: too close to "Redemption Song" — never make it. (lyrics.txt = safe revision; old MP3 sings cautioned lines, never use)
- Under 3 min, left out: Follow Along, Thank You for Joining, short Living 2 Die take, Tick Talk Whoa.
- Duplicates share a video: True Strength (1), A New God Rises (1), "I feel the weight…" (= Lone Wolf Rising), Embrace (4), Footprints (4), Remember Me "Remastered2".
