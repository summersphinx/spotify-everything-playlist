import spotipy
from spotipy.oauth2 import SpotifyOAuth
import PySimpleGUI as sg
from random import choice
import os
import SEP
import time

sg.theme(choice(sg.theme_list()))
os.makedirs(f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP', exist_ok=True)
os.chdir(f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP')
if sg.user_settings_file_exists():
    sg.user_settings_load()
else:
    sg.user_settings_set_entry('id', '')
    sg.user_settings_set_entry('exclude', [])
icon = 'https://raw.githubusercontent.com/summersphinx/spotify-everything-playlist/master/Spotify.ico'


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


def run(sp, include: list, to):
    print(sp)
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
        if 'local' in each:
            res.remove(each)
    failed = []

    def divide_chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    res = list(divide_chunks(res, 100))
    sp.playlist_replace_items(to, [])
    for chunk in res:
        pass
        sp.playlist_add_items(to, chunk)

    sg.cprint('Finished!')
    sg.cprint('\n\nFailed songs:')
    for i in failed:
        sg.cprint(i)


connect_layout = [
    [
        sg.Column([[sg.Text('Playlist URL')]]),
        sg.Column([[sg.Input('', s=(33, 1), k='to')]])
    ],
    [sg.Button('Connect')]
]

exclude_left = [
    [sg.Listbox([], select_mode='LISTBOX_SELECT_MODE_SINGLE', k='playlists', s=(40, 10))]
]
exclude_center = [
    [sg.Button('Add', expand_x=True)],
    [sg.Button('Remove', expand_x=True)],
    [sg.Button('Clear', expand_x=True)]
]
exclude_right = [
    [sg.Listbox(sg.user_settings_get_entry('exclude'), select_mode='LISTBOX_SELECT_MODE_SINGLE', k='exclude',
                s=(40, 10))]
]
exclude_layout = [
    [sg.Column(exclude_left), sg.Column(exclude_center, element_justification='c', vertical_alignment='c'),
     sg.Column(exclude_right)]
]

lay3_layout = [
    [sg.Button('Run', s=(80, 1))],
    [sg.Multiline('', disabled=True, size=(90, 13), k='log')]
]

emoji = SEP.Emoji()
layout = [
    [sg.Text('Everything Playlist Maker', font='Arial 18 bold')],
    [sg.Text(
            'Create a spotify playlist with every song in your library! ( Without local songs or playlists you do not want :) )')],
    [sg.Frame('Connect', connect_layout, expand_x=True)],
    [sg.Frame('Exclude', exclude_layout, expand_x=True)],
    [sg.Frame('Log', lay3_layout)],
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
        sg.user_settings_save()
        break

    if sp is not None:
        wn['playlists'].Update(get_playlists_readable(sp, sg.user_settings_get_entry('exclude')))

    if event == 'Connect':
        wn['emoji'].Update(emoji.thinking)
        try:
            sp = SEP.Spotify(sg.user_settings_get_entry('to')).sp
            wn['playlists'].Update(get_playlists_readable(sp))

        except:
            sp = None
        if sp is not None:
            wn['emoji'].Update(emoji.alive)
        print('Balkghswoigh')

    if event == 'Add':
        if len(values['playlists']) == 1:
            sg.user_settings_set_entry('exclude', sg.user_settings_get_entry('exclude').append(values['playlists'][0]))

    if event == 'Remove':
        if len(values['exclude']) == 1:
            sg.user_settings_set_entry('exclude', sg.user_settings_get_entry('exclude').remove(values['exclude'][0]))

    if event == 'Clear':
        sg.user_settings_set_entry('exclude', [])

    if event in ['Add', 'Remove', 'Clear']:
        # print(sg.user_settings_get_entry('exclude'))
        wn['exclude'].Update(sg.user_settings_get_entry('exclude'))
        wn['playlists'].Update(get_playlists_readable(sp, sg.user_settings_get_entry('exclude')))

    if event == 'Run':
        print(sp)
        if sp is None:
            sg.popup_error("You haven't connected to Spotify yet! Connect in the first tab, then run!")
        else:
            try:
                with open('to.txt', 'w') as fh:
                    fh.write(values['to'])
            except:
                sg.popup_error(
                        'Something went wrong! Most likely, the playlist you have added does not exist. Try again or edit the value!')
            sg.cprint('Starting! It will take a moment to start. Please be patient . . .')
            time.sleep(2)
            run(sp, get_playlists_readable(sp, sg.user_settings_get_entry('exclude')), values['to'])

wn.close()
