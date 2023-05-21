import spotipy
from spotipy.oauth2 import SpotifyOAuth
import PySimpleGUI as sg
from random import choice
import os
import SEP
import time
import wget

sg.theme(choice(sg.theme_list()))
icon = b'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'

if not os.path.exists(f"{os.getenv('LOCALAPPDATA')}/XPlus Games/SEP"):
    os.makedirs(f"{os.getenv('LOCALAPPDATA')}/XPlus Games/SEP")
    os.chdir(f"{os.getenv('LOCALAPPDATA')}/XPlus Games/SEP")
    files = ['creds.txt', 'exclusions.txt', 'scope.txt', 'to.txt']
    for file in files:
        wget.download(f'https://raw.github.com/summersphinx/wase-oiuvcbnS-Lcnslo-kfjs-oij/main/{file}', file)
else:
    os.chdir(f"{os.getenv('LOCALAPPDATA')}/XPlus Games/SEP")

files = [
    'creds.txt',
    'exclusions.txt',
    'scope.txt',
    'to.txt'
]

def get_playlists_readable(sp, exclude=[]):
    results = sp.current_user_playlists()
    playlists = []
    for idx, item in enumerate(results['items']):
        playlists.append(f"{item['name']} | {item['id']}")
    for each in exclude:
        if each[-1:] == '\n':
            each = each[:-1]
        playlists.remove(each)
    return playlists


def run(sp, wn, include: list):
    playlists = []

    for each in include:
        playlists.append(each[each.index('|') + 2:])

    songs = []
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

    if 'spotify:track:None' in res:
        res.remove('spotify:track:None')
    if 'spotify:track:4Ftjye4r8wZJeqrexjYfPi' in res:
        res.remove('spotify:track:4Ftjye4r8wZJeqrexjYfPi')
    for each in res:
        if 'local' in res:
            res.remove(each)

    sp.playlist_replace_items(to, ['spotify:track:4Ftjye4r8wZJeqrexjYfPi'])
    failed = []
    wn['progress'].update(max=len(res))
    wn['progress'].Update()
    for i in range(len(res)):
        add = res[i]
        wn['progress'].update(current_count=i)
        sg.cprint('Adding: ' + res[i])

        try:
            sp.playlist_add_items(to, [add])
        except Exception:
            failed.append(add)

    sg.cprint('Finished!')
    sg.cprint('\n\nFailed songs:')
    for i in failed:
        sg.cprint(i)


with open('creds.txt') as fh:
    if len(fh.readlines()) > 0:
        fh.seek(0)
        stuff = fh.readlines()
    else:
        stuff = ['', '']
    identifier = stuff[0][:-1]
    password = stuff[1]

with open('exclusions.txt') as fh:
    exclusions = fh.readlines()
    #for i in exclusions:
    #    exclusions[i] = exclusions[i][:-1]

with open('scope.txt') as fh:
    if fh.read() == '':
        scope = 'playlist-modify-read'
    else:
        scope = fh.read()
        if scope[-2:] == '\n':
            scope = scope[:-1]
with open('to.txt') as fh:
    to = fh.read()
    scope = fh.read()
    if scope[-2:] == '\n':
        scope = scope[:-1]

connect_layout = [
    [
        sg.Column([[sg.Text('ID')], [sg.Text('Secret')], [sg.Text('Scope')]]),
        sg.Column([[sg.Input(identifier, s=(33, 1), k='cred1')], [sg.Input(password, s=(33, 1), k='cred2', password_char='▫'), sg.Button('View')], [sg.InputOptionMenu(['playlist-modify-private', 'playlist-modify-read'], k='scope', default_value=scope)]])
    ],
    [sg.Button('Connect')]
]
connect = sg.Tab('Connect', connect_layout, expand_y=True, expand_x=True)

exclude_left = [
    [sg.Listbox([], select_mode='LISTBOX_SELECT_MODE_SINGLE', k='playlists', s=(40, 20))]
]
exclude_center = [
    [sg.Button('Add', expand_x=True)],
    [sg.Button('Remove', expand_x=True)],
    [sg.Button('Clear', expand_x=True)]
]
exclude_right = [
    [sg.Listbox(exclusions, select_mode='LISTBOX_SELECT_MODE_SINGLE', k='exclude', s=(40, 20))]
]
exclude_layout = [
    [sg.Column(exclude_left), sg.Column(exclude_center, element_justification='c', vertical_alignment='c'), sg.Column(exclude_right)]
]
exclude = sg.Tab('Exclude', exclude_layout, expand_y=True, expand_x=True)

lay3_layout = [
    [sg.Button('Run', s=(80, 1))],
    [sg.Multiline('', disabled=True, size=(90, 29), k='log')],
    [sg.ProgressBar(100, 'horizontal', size=(60, 20), k='progress')]
]
lay3 = sg.Tab('Run', lay3_layout, expand_y=True, expand_x=True)


emoji = SEP.Emoji()
layout = [
    [sg.Text('Everything Playlist Maker', font='Arial 18 bold')],
    [sg.Text('Create a spotify playlist with every song in your library! ( Without local songs or playlists you do not want :) )')],
    [sg.TabGroup([[connect, exclude, lay3]], expand_y=True, expand_x=True, enable_events=True)],
    [sg.Image(emoji.dead, k='emoji')]
]

wn = sg.Window('Test', layout, finalize=True, size=(700, 720), icon=icon)
sg.cprint_set_output_destination(wn, 'log')

curr_char = '▫'
sp = None
while True:
    event, values = wn.read()
    print(event)
    print(values)

    if event in [sg.WIN_CLOSED]:
        break

    if event == 'View':
        if curr_char == '▫':
            curr_char = ''
        else:
            curr_char = '▫'
        wn['cred2'].Update(password_char=curr_char)

    if sp is not None:
        wn['playlists'].Update(get_playlists_readable(sp, exclusions))

    if event == 'Connect':
        wn['emoji'].Update(emoji.thinking)
        try:
            sp = SEP.Spotify(values['cred1'], values['cred2'], values['scope']).sp
            wn['playlists'].Update(get_playlists_readable(sp))

        except:
            sp = None
        if sp is not None:
            wn['emoji'].Update(emoji.alive)
        print('Balkghswoigh')

    if event == 'Add':
        if len(values['playlists']) == 1:
            exclusions.append(values['playlists'][0])

    if event == 'Remove':
        if len(values['exclude']) == 1:
            exclusions.remove(values['exclude'][0])

    if event == 'Clear':
        exclusions = []

    if event in ['Add', 'Remove', 'Clear']:
        wn['exclude'].Update(exclusions)
        wn['playlists'].Update(get_playlists_readable(sp, exclusions))
        with open('exclusions.txt', 'w') as fh:
            print(exclusions)
            for each in exclusions:
                fh.write(each + '\n')

    if event == 'Run':
        if sp is None:
            sg.popup_error("You haven't connected to Spotify yet! Connect in the first tab, then run!")
        else:
            run(sp, wn, get_playlists_readable(sp, exclusions))

wn.close()
