import os
import pyperclip
import time
import requests
current_path = os.path.abspath(__file__)
script_directory = os.path.dirname(current_path)
def download(id):
    path = f'./maps/{id}.osz'
    resp = requests.get(f'https://beatconnect.io/b/{id}')
    with open(path, 'wb') as f:
        for buff in resp:
            f.write(buff)
previous_clipboard_content = pyperclip.paste()
while True:
    curr_clip = str(pyperclip.paste())
    if curr_clip != previous_clipboard_content:
        if (curr_clip.find('https://osu.ppy.sh/beatmapsets/') > -1):
            print('downloading:', curr_clip)
            id = int(curr_clip.split('/beatmapsets/')[1].split('#')[0])
            download(id)
            print('Opening map')
            os.system(f'{script_directory}/maps/{id}.osz')
            print('Opened')
        previous_clipboard_content = str(curr_clip)
    time.sleep(0.1)