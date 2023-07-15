from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageChops, ImageEnhance
from bs4 import BeautifulSoup
import subprocess
import requests
import zipfile
import json
import time
import os

# Consts ---------------------------------------------------------------------------------------------------------------
colors = {
    'D': '#E7935D',
    'C': '#33DF99',
    'B': '#009CFF',
    'A': '#FF0066',
    'S': '#FFFF00',
    'SH': '#ECECEC',
    'X': '#FFFF00',
    'XH': '#ECECEC',
    'FC': '#FFDE2E',
    'MISSES': '#FF0024',
    'PERFORMANCE': "#FFFFFF",
    'RANK': '#FF0024',
    'COL1': '#353340',
    'COL2': '#7A7392',
    'MOD': '#858383',
    'MOD2': '#494747',
    'NM': '#585858'
}
preview_ranks = {
    'D': 'D',
    'C': 'C',
    'B': 'B',
    'A': 'A',
    'S': 'S',
    'SH': 'S',
    'X': 'SS',
    'XH': 'SS'
}
# ----------------------------------------------------------------------------------------------------------------------

# Functions ------------------------------------------------------------------------------------------------------------
def map_value_to_color_rating(value:float):
    color_points = [
        (0.00, (85, 192, 249)),
        (0.15, (85, 192, 249)),
        (0.20, (82, 247, 210)),
        (0.25, (130, 242, 88)),
        (0.325, (244, 242, 86)),
        (0.45, (255, 124, 100)),
        (0.60, (255, 63, 114)),
        (0.70, (103, 99, 223)),
        (0.80, (0, 0, 0)),
        (1.00, (0, 0, 0))
    ]
    lower_color, upper_color = None, None
    for i in range(len(color_points) - 1):
        if color_points[i][0] <= value < color_points[i + 1][0]:
            lower_color = color_points[i]
            upper_color = color_points[i + 1]
            break
    if lower_color is None or upper_color is None:
        return None
    lower_value, lower_rgb = lower_color
    upper_value, upper_rgb = upper_color
    t = (value - lower_value) / (upper_value - lower_value)
    interpolated_rgb = tuple(int(lower + (upper - lower) * t) for lower, upper in zip(lower_rgb, upper_rgb))
    return interpolated_rgb
def choose_rank():
    choice = ''
    while not choice in valid_ranks:
        choice = input('Enter rank (B, A, S, SS): ').upper()
    return choice
def get_rating_color(rating:float, get_glow=False):
    return map_value_to_color_rating(rating/10.0)
def rounded_rectangle(image:Image, xy:tuple, radius:int, fill:str, outline=None, width=0, rotation=0):
    draw = ImageDraw.Draw(image)
    rotated_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw_rotated = ImageDraw.Draw(rotated_image)
    draw_rotated.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    rotated_image = rotated_image.rotate(rotation, center=((xy[2]+xy[0])/2, (xy[3]+xy[1])/2))
    image.alpha_composite(rotated_image)
    return image
def type_text(image:Image, xy:tuple, anchor:str, text:str, font:ImageFont, font_color:str, shadow=False, glow=False, glow_color='#FFFFFF', glow_size=30, glow_type=0):
    result = image
    if (shadow):
        text_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_image)
        text_draw.text((xy[0],xy[1]+3), text, anchor=anchor, font=font, fill='#000000')
        blurred_text = text_image.filter(ImageFilter.BoxBlur(8))
        result = Image.alpha_composite(image, blurred_text)
        result = Image.alpha_composite(result, blurred_text)
    if (glow):
        text_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_image)
        text_draw.text(xy, text, anchor=anchor, font=font, fill=glow_color)
        if glow_type == 0:
            blurred_text = text_image.filter(ImageFilter.BoxBlur(glow_size))
        elif glow_type == 1:
            blurred_text = text_image.filter(ImageFilter.GaussianBlur(glow_size))
        enhancer = ImageEnhance.Brightness(blurred_text)
        brightened_image = enhancer.enhance(1.5)
        result = Image.alpha_composite(image, brightened_image)
        result = Image.alpha_composite(result, brightened_image)
        result = Image.alpha_composite(result, brightened_image)
    draw = ImageDraw.Draw(result)
    draw.text(xy, text, anchor=anchor, font=font, fill=font_color)
    return result
def create_thumbnail(username:str, song_name:str, song_artist:str, difficulty_name:str, bpm:int, star_rating:float, accuracy:float, misses:int, modifiers:list, performance:int, max_combo:int, combo_limit:int, score_rank:int, rank:str, background_path:str, pfp_path:str, flag_path:str):
    width = 1280
    height = 720

    bpm = f'{bpm}bpm'
    accuracy = f'{format(accuracy, ".2f")}%'
    misses = f'{misses}x'
    performance = f'{performance}pp'
    if score_rank == -1:
        rank_offset = -70
        score_rank = 'N/A'
    else:
        score_rank = f'#{score_rank}'

    combo_max_combo = f'{max_combo}/{combo_limit}x'

    font38 = ImageFont.truetype('./fonts/VarelaRound-Regular.ttf', 38)
    font30 = ImageFont.truetype('./fonts/VarelaRound-Regular.ttf', 30)
    font40 = ImageFont.truetype('./fonts/VarelaRound-Regular.ttf', 40)
    font47 = ImageFont.truetype('./fonts/VarelaRound-Regular.ttf', 47)
    font50 = ImageFont.truetype('./fonts/VarelaRound-Regular.ttf', 50)
    font78 = ImageFont.truetype('./fonts/VarelaRound-Regular.ttf', 78)
    font125 = ImageFont.truetype('./fonts/VarelaRound-Regular.ttf', 125)
    font185 = ImageFont.truetype('./fonts/VarelaRound-Regular.ttf', 185)
    font284 = ImageFont.truetype('./fonts/VarelaRound-Regular.ttf', 284)

    mask_banner = Image.new('RGBA', (width, height))
    mask_bg = Image.new('RGBA', (width, height))
    mask_pfp = Image.new('RGBA', (width, height))
    rounded_rectangle(mask_banner, (18, 14, 1244 + 18, 262 + 14), 29, (255, 255, 255, 255))
    rounded_rectangle(mask_bg, (0, 0, width, height), 0, (255, 255, 255, int(255 * 0.18)))
    img = Image.new('RGBA', (width, height), (0,0,0,255))
    background = Image.open(background_path)
    pfp = Image.open(pfp_path).resize((273,273))
    flag = Image.open(flag_path).convert('RGBA')
    bg_width = background.width
    bg_height = background.height
    ox = (bg_width/2 * 1.8 - width/2)
    oy = (bg_height/2 * 1.8 - height/2 - 9)
    img.paste(background.resize((int(bg_width * 1.8), int(bg_height * 1.8))).crop((ox, oy, width + ox, height + oy)).crop((0, 0, width, height)).filter(ImageFilter.BoxBlur(10)), (0, 0, width, height), mask=mask_bg)
    rounded_rectangle(img, (18, 23, 1244 + 18, 262 + 23), 29, colors['COL2'])
    ox = (bg_width/2 * 1.31 - width/2)
    oy = (bg_height/2 * 1.31 - height/2 + 260)
    img.paste(background.resize((int(bg_width * 1.31), int(bg_height * 1.31))).crop((ox, oy, width + ox, height + oy)).crop((0, 0, width, height)), (0, 0, width, height), mask=mask_banner)
    if len(difficulty_name) > 22:
        difficulty_name = f'{difficulty_name[:19]}...'
    song_artist_name = f'{song_artist} - {song_name}'
    if len(song_artist_name) > 42:
        song_artist_name = f'{song_artist_name[:39]}...'
    difficulty_name = f'[{difficulty_name}]'
    difficulty_length = font38.getlength(difficulty_name)
    difficulty_height = font38.getbbox(difficulty_name)[3]
    ox = width/2
    oy = height/2 - 80
    rounded_rectangle(img, (ox - (difficulty_length/2 + 15), oy - 40, ox + (difficulty_length/2 + 15), oy + 40), 8, colors['COL1'], colors['COL2'], 7)
    img = type_text(img, (ox, oy), 'mm', difficulty_name, font38, '#FFFFFF')
    rounded_rectangle(img, (250 - 192.5/2, 281.75 - 70.5/2, 250 + 192.5/2, 281.75 + 70.5/2), 70.5/2, colors['COL1'], colors['COL2'], 7)
    rounded_rectangle(img, (width-250 - 192.5/2, 281.75 - 70.5/2, width-250 + 192.5/2, 281.75 + 70.5/2), 70.5/2, colors['COL1'], colors['COL2'], 7)
    img = type_text(img, (250, 281.75), 'mm', combo_max_combo, font30, '#FFFFFF')
    bpm_length = font30.getlength(bpm)
    bpm_height = font30.getbbox(bpm)[3]
    img = type_text(img, (width-250, 282), 'mm', bpm, font30, '#FFFFFF')
    img = type_text(img, (width/2, 386), 'mm', song_artist_name, font50, '#FFFFFF', True, True, 30, 1)
    img = type_text(img, (width/2, 74), 'mm', format(star_rating, '.2f'), font78, get_rating_color(star_rating), False, True, get_rating_color(star_rating, True), 10, 1)
    if misses != '0x':
        img = type_text(img, (200, 130), 'mm', misses, font125, colors['MISSES'], True, True, colors['MISSES'], 15, 1)
    else:
        img = type_text(img, (200, 130), 'mm', 'FC', font185, colors['FC'], True, True, colors['FC'], 15, 1)
    img = type_text(img, (1035, 130), 'mm', performance, font125, colors['PERFORMANCE'], True, True, colors['PERFORMANCE'], 15, 1)
    pfp_width = pfp.width
    pfp_height = pfp.height
    ox = (pfp_width/2 * 0.571 - width/2)
    oy = (pfp_height/2 * 0.571 - height/2 - 190)
    rounded_rectangle(mask_pfp, (-ox, -oy, -ox+pfp_width*0.571-1, -oy+pfp_height*0.571-1), 38, (255, 255, 255, 255))
    img.paste(pfp.resize((int(pfp_width * 0.571), int(pfp_height * 0.571))).crop((ox, oy, width + ox, height + oy)).crop((0, 0, width, height)), (0, 0), mask=mask_pfp)
    flag_width = flag.width;
    flag_height = flag.height;
    flag_x = 640-flag_width*1.528/2
    flag_y = 627-flag_height*1.528/2
    new_flag_width = int(flag_width * 1.528)
    new_flag_height = int(flag_height * 1.528)
    rounded_rectangle(img, (flag_x-1, flag_y + 7, flag_x+new_flag_width, flag_y+new_flag_height-8), 7, '#000000')
    img.alpha_composite(flag.resize((new_flag_width, new_flag_height)).crop((0-flag_x,0-flag_y,width-flag_x,height-flag_y)))
    rounded_rectangle(img, (1000-498/2, 517-90/2, 1000+498/2, 517+90/2), 20, colors['COL2'])
    rounded_rectangle(img, (1004-490/2, 517-90/2, 1004+490/2, 517+90/2), 20, colors['COL1'])
    img = type_text(img, (1004, 517), 'mm', username, font47, '#FFFFFF')
    if modifiers == []:
        rounded_rectangle(img, (791.3 - 78 / 2, 608.913 - 65 / 2, 791.3 + 78 / 2, 608.913 + 65 / 2), 20, colors['NM'])
        rounded_rectangle(img, (791.3 - 47 / 2, 608.913 - 47 / 2, 791.3 + 47 / 2, 608.913 + 47 / 2), 47/2, colors['NM'], '#FFFFFF', 6)
        rounded_rectangle(img, (791.3 - 47 / 2, 608.913 - 0 / 2, 791.3 + 47 / 2, 608.913 + 0 / 2), 0, colors['NM'], '#FFFFFF', 4, 45)
    else:
        for i in range(0, len(modifiers)):
            offset = 78 - 10
            rounded_rectangle(img, (791.3 - 78 / 2 + i * offset - 2, 608.913 - 65 / 2 + 5, 791.3 + 78 / 2 + i * offset, 608.913 + 65 / 2 + 5), 20, colors['MOD2'])
            rounded_rectangle(img, (791.3 - 78 / 2 + i * offset, 608.913 - 65 / 2, 791.3 + 78 / 2 + i * offset, 608.913 + 65 / 2), 20, colors['MOD'])
            img = type_text(img, (791.3 + i * offset, 608.913), 'mm', modifiers[i], font40, '#FFFFFF')
    img = type_text(img, (512, 514), 'rm', accuracy, font47, '#FFFFFF', True, True, '#FFFFFF', 15, 1)
    img = type_text(img, (512, 581), 'rm', score_rank, font47, colors['RANK'], True, True, colors['RANK'], 15, 1)
    if len(preview_ranks[rank]) < 2:
        img = type_text(img, (185, 561), 'mm', preview_ranks[rank], font284, colors[rank], True, True, colors[rank], 25, 1)
    else:
        img = type_text(img, (185-17, 561), 'mm', preview_ranks[rank][0], font284, colors[rank], True, True, colors[rank], 25, 1)
        img = type_text(img, (185+17, 561), 'mm', preview_ranks[rank][1], font284, colors[rank], True, True, colors[rank], 25, 1)
    return img
def download_img(uri:str, path:str):
    res = requests.get(uri)
    with open(path, "wb") as f:
        f.write(res.content)
def download(id:int):
    name = id
    path = f'./maps/{name}.osz'
    directory_to_extract_to = f'./maps/{name}/'
    resp = requests.get(f'https://beatconnect.io/b/{id}')
    with open(path, 'wb') as f:
        for buff in resp:
            f.write(buff)
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)
    time.sleep(0.1)
    os.remove(path)
def get_score_data(type:str, score_id:int):
    response_token = requests.post('https://osu.ppy.sh/oauth/token', headers={'Accept': 'application/json'}, data={'client_id': '23406', 'client_secret': 'lFeWQJ8qNMJgGsGlk8gj1b9rkgp7Zb0C4eFeA4IE', 'grant_type': 'client_credentials', 'scope': 'public'}, files=[])
    response_score = requests.get(f'https://osu.ppy.sh/api/v2/scores/{type}/{score_id}', headers={'Authorization': f'Bearer {response_token.json()["access_token"]}'})
    score = response_score.json()

    with open('test.json', 'w') as out:
        out.write(json.dumps(score))

    user = score['user']
    beatmap = score['beatmap']
    beatmapset = score['beatmapset']
    statistics = score['statistics']
    mods = score['mods']

    country_code = user['country_code']

    flag_svg_file_path = f'./flags/{country_code}.svg'
    flag_png_file_path = f'./flags/{country_code}.png'

    if not os.path.exists(f'./flags/{country_code}.png'):
        country_rankings = requests.get(f'https://osu.ppy.sh/rankings/osu/performance?country={country_code}')
        bs_country_rankings = BeautifulSoup(country_rankings.text, 'html.parser')
        flag_svg_path = bs_country_rankings.find('div', {'class': 'flag-country flag-country--medium'}).get('style').split('url(\'')[1].split('\'')[0]
        flag_svg_url = f'https://osu.ppy.sh{flag_svg_path}'
        download_img(flag_svg_url, flag_svg_file_path)
        flag_svg_data = open(flag_svg_file_path).read()
        subprocess.run(["magick", "-background", "none", flag_svg_file_path, flag_png_file_path], shell=True)
        os.remove(flag_svg_file_path)

    username = user['username']
    song_name = beatmapset['title']
    song_artist = beatmapset['artist']
    difficulty_name = beatmap['version']
    if type == 'mania':
        difficulty_name = ' '.join(difficulty_name.split(' ')[1:])
    bpm = beatmap['bpm']
    star_rating = beatmap['difficulty_rating']
    accuracy = round(score['accuracy'] * 100, 2)
    misses = statistics['count_miss']
    modifiers = mods
    performance = round(score['pp'])
    max_combo = score['max_combo']
    combo_limit = beatmap['max_combo']
    score_rank = score['rank_global']
    rank = score['rank']
    background_image_url = f'https://assets.ppy.sh/beatmaps/{beatmapset["id"]}/covers/cover@2x.jpg'
    background_path = f'./backgrounds/{beatmapset["id"]}.png'
    download_img(background_image_url, background_path)
    # if not os.path.exists(f'./maps/{beatmapset["id"]}'):
    #     download(beatmapset['id'])
    # files = os.listdir(f'./maps/{beatmapset["id"]}')
    # name = ''
    # for file in files:
    #     if file.find(f'[{difficulty_name}].osu') > 0:
    #         name = file
    # path = f'./maps/{beatmapset["id"]}/{name}'
    # data = open(path, 'r', encoding='utf-8').read()
    # bg_name = data.split('//Background and Video events\n0,0,"')[1].split('"')[0]
    # background_path = f'./maps/{beatmapset["id"]}/{bg_name}'
    pfp_path = f'./pfps/{username}.png'
    download_img(user['avatar_url'], pfp_path)

    return (username, song_name, song_artist, difficulty_name, bpm, star_rating, accuracy, misses, modifiers, performance, max_combo, combo_limit, score_rank, rank, background_path, pfp_path, flag_png_file_path)
# ----------------------------------------------------------------------------------------------------------------------

# VALID RANKS:
# A, B, C, D
#  S = S
# SH = S+
#  X = SS
# XH = SS+

# Custom Data ----------------------------------------------------------------------------------------------------------
game_mode:            str   = 'mania'
username:             str   = 'Anto_Crasher555'
song_name:            str   = 'Kawaki o Ameku (TV Size)'
song_artist:          str   = 'Minami'
difficulty_name:      str   = 'Applequestria'
bpm:                  int   = 129
star_rating:          float = 4.85
accuracy:             float = 100.00
misses:               int   = 0
modifiers:            list  = ['HT', 'PF']
performance:          int   = 0
max_combo:            int   = 1044
combo_limit:          int   = 1044
score_rank:           int   = -1
rank:                 str   = 'X'
background_path:      str   = './backgrounds/Kawaki_o_Ameku.jpg'
pfp_path:             str   = './pfps/Anto_Crasher555.png'
flag_path:            str   = './flags/TH.png'
# ----------------------------------------------------------------------------------------------------------------------

type = 'mania'
score_id = 543698110

generate_thumbnail = True
print_title = True
use_score = True
data = []

# ----------------------------------------------------------------------------------------------------------------------
if generate_thumbnail:
    if use_score:
        data = get_score_data(type, score_id)
        thumbnail = create_thumbnail(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8],
                                     data[9], data[10], data[11], data[12], data[13], data[14], data[15], data[16])
        thumbnail.save(f'./thumbnails/{type}/{score_id}.png')
    else:
        thumbnail = create_thumbnail(username, song_name, song_artist, difficulty_name, bpm, star_rating, accuracy,
                                     misses, modifiers, performance, max_combo, combo_limit, score_rank, rank,
                                     background_path, pfp_path, flag_path)
        thumbnail.save(f'./thumbnails/{game_mode}/{username.replace(" ", "_")}_{song_name.replace(" ", "_")}_{difficulty_name.replace(" ", "_")}_{score_rank}.png')
# ----------------------------------------------------------------------------------------------------------------------
if print_title:
    title = ''
    if use_score:
        mods = ''
        if len(data[8]) > 0:
            mods = " ".join(data[8]) + " "
        song_artist_name = f'{data[2]} - {data[1]}'
        if len(song_artist_name) > 50:
            song_artist_name = f'{song_artist_name[:50-3]}...'
        title = f'{format(data[5], ".2f")}⭐ | {song_artist_name} [{data[3]}] {format(data[6], ".2f")}% {mods}(#{data[12]} {data[9]}pp {data[7]}❌)'
    else:
        if score_rank == -1:
            score_rank = 'N/A'
        else:
            score_rank = f'#{score_rank}'
        mods = ''
        if len(modifiers)  > 0:
            mods = " ".join(modifiers) + " "
        title = f'{format(star_rating, ".2f")}⭐ | {song_artist} - {song_name} [{difficulty_name}] {format(accuracy, ".2f")}% {mods}({score_rank} {performance}pp {misses}❌)'
    print(title)
# ----------------------------------------------------------------------------------------------------------------------
