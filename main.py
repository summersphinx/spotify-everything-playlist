import io
import os
import threading
import urllib.request

import PySimpleGUI as sg
import imageio.v3 as iio
import requests
from PIL import Image

import SEP

sg.theme("Dark")
emoji = SEP.Emoji()
os.makedirs(f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP', exist_ok=True)
os.chdir(f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP')
# sg.user_settings_delete_filename(filename='settings.json', path=f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP')
sg.user_settings_filename(path=f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP', filename='settings.json')

if sg.user_settings_file_exists(filename='settings.json'):
    sg.user_settings_load(filename='settings.json')
else:
    sg.user_settings_set_entry('id', '')
    sg.user_settings_set_entry('exclude', [])
    sg.user_settings_set_entry('filter_songs', True)
    sg.user_settings_save(filename='settings.json')

icon = None
if requests.get('https://www.google.com').status_code == 200:
    with urllib.request.urlopen(
            'https://raw.githubusercontent.com/summersphinx/spotify-everything-playlist/master/Spotify.png') as url:
        icon = io.BytesIO(url.read()).read()
        print('hi')
        print(icon)
        print('bye')

settings = sg.UserSettings(path=f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP', filename='settings.json')


def playlist_pic(sp, wn, playlist):
    print('hi2')
    print(playlist)
    print(sp)
    print(wn)
    temp = sp.playlist(playlist)
    iio.imwrite("img.png", iio.imread(temp['images'][0]['url'], index=None), extension='.png')
    Image.open('img.png', 'r').resize((80, 80)).save('img.png')
    wn['playlist_image'].Update(source='img.png')


def get_playlists_readable(sp, exclude=None):
    if exclude is None:
        exclude = []
    results = sp.current_user_playlists()
    playlists = []
    for idx, item in enumerate(results['items']):
        playlists.append(f"{item['name']} | {item['id']}")
    for each in exclude:
        if each[-1:] == '\n':
            each = each[:-1]
        playlists.remove(each)
        playlists = playlists.sort()
    return playlists


def run(sp, include: list, to, sc, filter):
    sg.cprint('Starting! It will take a moment to start. Please be patient . . .')
    settings['id'] = to
    playlists = []

    for each in include:
        playlists.append(each[each.index('|') + 2:])

    songs = []
    sg.cprint('Getting every song . . .')
    for playlist in playlists:
        results = sp.playlist_items(playlist)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        for i in tracks:
            try:
                track = i['track']['uri']
                songs.append(track)
            except TypeError:
                continue

    res = list(dict.fromkeys(songs))
    sg.cprint(f'Found {len(res)} songs!')
    sg.cprint('Removing spotify:track:None . . .')

    if 'spotify:track:None' in res:
        res.remove('spotify:track:None')
    sg.cprint('Removing local songs . . .')
    for each in res:
        if 'local' in each:
            res.remove(each)
    if filter:
        sg.cprint('Removing non songs . . .')
        for each in res:
            if 'episode' in each:
                res.remove(each)
    failed = []
    res.sort()
    print(res[0])

    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    res = list(divide_chunks(res, 100))
    sg.cprint('Resetting playlist . . .')
    sp.playlist_replace_items(to, [])
    for chunk in res:
        sp.playlist_add_items(to, chunk)
        sg.cprint(f'Added {len(chunk)} songs . . .')

    sg.cprint('Finished!')
    sg.cprint('\n\nFailed songs:')
    for i in failed:
        sg.cprint(i)


connect_layout_left = [
    [
        sg.Column([[sg.Text('Playlist URL')]]),
        sg.Column([[sg.Input(settings['id'], s=(33, 1), k='to'), sg.Text('', k='playlist_name')]])
    ],
    [sg.Button('Connect')]
]

connect_layout = [
    [sg.Column(connect_layout_left, expand_x=True), sg.Image(None, k='to_image', expand_x=True),
     sg.Image(emoji.dead, k='emoji')]
]

exclude_left = [
    [sg.Listbox([], k='playlists', s=(40, 10), enable_events=True)]
]
exclude_center = [
    [sg.Button('Add', expand_x=True)],
    [sg.Button('Remove', expand_x=True)],
    [sg.Button('Clear', expand_x=True)],
    [sg.Image(None, key='playlist_image')]
]
exclude_right = [
    [sg.Listbox(settings['exclude'], k='exclude',
                s=(40, 10))]
]
exclude_layout = [
    [sg.Column(exclude_left), sg.Column(exclude_center, element_justification='c', vertical_alignment='c'),
     sg.Column(exclude_right)],
    [sg.Checkbox('Filter just songs', k='filter songs', default=settings['filter_songs'])]
]

lay3_layout = [
    [sg.Button('Run', s=(80, 1))],
    [sg.Multiline('', disabled=True, size=(90, 13), k='log')]
]

layout = [
    [sg.Text('Everything Playlist Maker', font='Arial 18 bold')],
    [sg.Text(
            'Create a spotify playlist with every song in your library! ( Without local songs or playlists you do not want :) )')],
    [sg.Frame('Connect', connect_layout, expand_x=True)],
    [sg.Frame('Exclude', exclude_layout, expand_x=True)],
    [sg.Frame('Log', lay3_layout)]
]

wn = sg.Window('Test', layout, finalize=True, size=(700, 700), icon=icon)
sg.cprint_set_output_destination(wn, 'log')
lb1 = wn['playlists']
sp = None
while True:
    event, values = wn.read()

    if values is not None:
        settings['filter_songs'] = values['filter songs']
    settings = sg.UserSettings(filename='settings.json', path=f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP')

    if event in [sg.WIN_CLOSED]:
        break

    if event == 'playlists':
        playlist = values['playlists'][0].split(' | ')[1]
        print('hi4')
        print(playlist)
        # SEP.playlist_pic(sp, wn, playlist)
        b = threading.Thread(target=playlist_pic, args=(sp, wn, playlist))
        b.run()

    if sp is not None:
        wn['playlists'].Update(get_playlists_readable(sp, settings['exclude']))

    if event == 'Connect':
        wn['emoji'].Update(emoji.thinking)
        sp = SEP.Spotify(settings['to']).sp
        temp = sp.playlist(values['to'])
        image = iio.imread(temp['images'][0]['url'], index=None)
        image = iio.imwrite("temp.png", image, extension='.png')
        image = Image.open('temp.png', 'r').resize((80, 80)).save('temp.png')
        wn['to_image'].Update(source='temp.png')
        wn['to'].Update(value=temp['id'])
        wn['playlist_name'].Update(value=temp['name'])
        sp = SEP.Spotify(settings['to']).sp
        wn['playlists'].Update(get_playlists_readable(sp, settings['exclude']))

        wn['emoji'].Update(emoji.alive)

    if event == 'Add':
        if len(values['playlists']) == 1:
            temp = settings['exclude']
            temp.append(values['playlists'][0])
            settings['exclude'] = temp

    if event == 'Remove':
        if len(values['exclude']) == 1:
            temp = settings['exclude']
            temp.remove(values['exclude'][0])
            settings['exclude'] = temp

    if event == 'Clear':
        settings['exclude'] = []

    if event in ['Add', 'Remove', 'Clear']:
        temp = settings['exclude']
        wn['exclude'].Update(temp)
        wn['playlists'].Update(get_playlists_readable(sp, temp))

    if event == 'playlists':
        print('hi3')
        print(values['playlists'])
        if values['playlists'] is not []:
            lb1.update(scroll_to_index=wn['playlists'].get_list_values().index(values['playlists'][0]))
            lb1.update(set_to_index=wn['playlists'].get_list_values().index(values['playlists'][0]))

    if event == 'Run':
        if sp is None:
            sg.popup_error("You haven't connected to Spotify yet! Connect in the first tab, then run!")
        else:
            try:
                settings['id'] = values['to']
            except:
                sg.popup_error(
                        'Something went wrong! Most likely, the playlist you have added does not exist. Try again or edit the value!')
            temp = settings['exclude']
            x = threading.Thread(target=run,
                                 args=(sp, get_playlists_readable(sp, temp), values['to'], wn, values['filter songs']))
            # run(sp, get_playlists_readable(sp, temp), values['to'], wn)
            x.start()

wn.close()
