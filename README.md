# OsuThumbnailPy

This python project is made to automatically generate osu video thumbnails (1280x720) and titles.

# How to use

Inside `main.py` on `line 319`, you can enter a score id<br>
All thumbnails will be saved to `'./thumbnails/thumbnail_name.png'`
Example: `https://osu.ppy.sh/scores/mania/543698110`<br>
This would look like:
```py
type = 'mania'
score_id = 543698110

generate_thumbnail = True
print_title = False
use_score = True
```
If you want to create a video title, you can set `print_title` to `True`.<br>

Another way to generate a thumbnail is to input the score data manually.
Example:
```py
# VALID RANKS:
# A, B, C, D
#  S = S
# SH = S+
#  X = SS
# XH = SS+

game_mode:            str   = 'mania'                             # string gamemode
username:             str   = 'Anto_Crasher555'                   # string username
song_name:            str   = 'Kawaki o Ameku (TV Size)'          # string song name
song_artist:          str   = 'Minami'                            # string song artist
difficulty_name:      str   = 'Applequestria'                     # string difficulty name
bpm:                  int   = 129                                 # int    song bpm
star_rating:          float = 4.85                                # float  difficulty star rating
accuracy:             float = 100.00                              # float  score accuacy
misses:               int   = 0                                   # int    miss count
modifiers:            list  = ['HT', 'PF']                        # list   modifiers used (2 letters)
performance:          int   = 0                                   # int    performance points (pp)
max_combo:            int   = 1044                                # int    maximum combo achieved in score
combo_limit:          int   = 1044                                # int    maximum achievable combo
score_rank:           int   = -1                                  # int    score global rank
rank:                 str   = 'X'                                 # string score rank (see above for VALID RANKS)
background_path:      str   = './backgrounds/Kawaki_o_Ameku.jpg'  # string background path (starts by './backgrounds/')
pfp_path:             str   = './pfps/Anto_Crasher555.png'        # string profile picture path (starts by './pfps/')
flag_path:            str   = './flags/TH.png'                    # string flag path (starts by './flags/')
```
This will generate a thumbnails named `f'./backgrounds/{username}_{song_name}_{difficulty_name}_{score_rank}.png'`

# Auto map downloader

When `download.py` is run, it will allow you to copy a beatmap link to your clipboard, and then it will automatically download and open the osu map for you.

Link example: `https://osu.ppy.sh/beatmapsets/400078#mania/992512`
