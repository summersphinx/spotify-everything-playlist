import os
import time
from random import choice

import PySimpleGUI as sg

import SEP

sg.theme(choice(sg.theme_list()))
os.makedirs(f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP', exist_ok=True)
# os.chdir(f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP')
# sg.user_settings_delete_filename(filename='settings.json', path=f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP')
sg.user_settings_filename(path=f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP', filename='settings.json')

if sg.user_settings_file_exists(filename='settings.json'):
    sg.user_settings_load(filename='settings.json')
else:
    sg.user_settings_set_entry('id', '')
    sg.user_settings_set_entry('exclude', [])
    sg.user_settings_save(filename='settings.json')

icon = 'https://raw.githubusercontent.com/summersphinx/spotify-everything-playlist/master/Spotify.ico'

settings = sg.UserSettings(path=f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP', filename='settings.json')


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
    return playlists


def run(sp, include: list, to):
    settings['id'] = to
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
    for each in res:
        if 'local' in each:
            res.remove(each)
    print(len(res))
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

print(settings)
connect_layout = [
    [
        sg.Column([[sg.Text('Playlist URL')]]),
        sg.Column([[sg.Input(settings['id'], s=(33, 1), k='to'), sg.Text('', k='playlist_name')]])
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
    [sg.Listbox(settings['exclude'], select_mode='LISTBOX_SELECT_MODE_SINGLE', k='exclude',
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

sp = None
while True:
    event, values = wn.read()
    settings = sg.UserSettings(filename='settings.json', path=f'{os.getenv("LOCALAPPDATA")}/XPlus Games/SEP')

    if event in [sg.WIN_CLOSED]:
        break

    if sp is not None:
        wn['playlists'].Update(get_playlists_readable(sp, settings['exclude']))

    if event == 'Connect':

        wn['emoji'].Update(emoji.thinking)
        sp = SEP.Spotify(settings['to']).sp
        print(sp)
        temp = sp.playlist(values['to'])
        wn['to'].Update(value=temp['id'])
        wn['playlist_name'].Update(value=temp['name'])
        sp = SEP.Spotify(settings['to']).sp
        sp.user_playlist()
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
            print(values['exclude'])
            temp.remove(values['exclude'][0])
            settings['exclude'] = temp

    if event == 'Clear':
        settings['exclude'] = []

    if event in ['Add', 'Remove', 'Clear']:
        temp = settings['exclude']
        wn['exclude'].Update(temp)
        wn['playlists'].Update(get_playlists_readable(sp, temp))

    if event == 'Run':
        if sp is None:
            sg.popup_error("You haven't connected to Spotify yet! Connect in the first tab, then run!")
        else:
            try:
                settings['id'] = values['to']
            except:
                sg.popup_error(
                        'Something went wrong! Most likely, the playlist you have added does not exist. Try again or edit the value!')
            sg.cprint('Starting! It will take a moment to start. Please be patient . . .')
            time.sleep(2)
            temp = settings['exclude']
            run(sp, get_playlists_readable(sp, temp), values['to'])

wn.close()
