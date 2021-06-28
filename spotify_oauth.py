import os
import spotipy
import yaml
from spotipy.oauth2 import SpotifyOAuth
from youtube_search import YoutubeSearch
from difflib import SequenceMatcher
import subprocess


## configuration 
class config:
    def __init__(self, **entries):
        self.__dict__.update(entries)

## import the config file as config properties
with open("config.yaml", 'r') as stream:
    data_loaded = yaml.safe_load(stream)
s = config(**data_loaded)

# configure Spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="d18509bdbb4d498e89dc2f56a6b7e8e6",
    client_secret="84db0e51115e483398e237961a12bbbb",
    redirect_uri="https://spotify.com",
    scope="playlist-read-private")
    )

# capture the top result for a song title
def get_youtube_uri(title):
    prefix = "https://www.youtube.com/watch?v="
    results = YoutubeSearch(title, max_results=1).to_dict()
    if results:
        suffix = results[0]["id"]
        return prefix+suffix
    return None

# get the tracks of a specific spotify playlist by id
def get_playlist_tracks(username,playlist_id):
    results = sp.user_playlist_tracks(username,playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

# collect a users playlists
def get_playlists(username):
    result = []
    ytdl = []
    ytdlpl = []
    folder_titles = []
    playlists = sp.user_playlists(username)
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            # determine if the playlist is specified in the config file
            similarity = []
            for pl in s.playlists:
                similarity.append(SequenceMatcher(None, pl, playlist['name']).ratio())
            # only grab playlists in the config file if they're 90% similar or higher
            if max(similarity) > .90:
                print("%4d %s" % (i + 1 + playlists['offset'],  playlist['name']))
                pluri = playlist['uri'].split(":")[2]
                tracks = get_playlist_tracks(username, pluri)
                for track in tracks:
                    title = track["track"]["album"]["artists"][0]["name"]+" - "+track["track"]["name"]
                    yturi = get_youtube_uri(title)
                    result.append([track, yturi])
                    if yturi:
                        ytdlpl.append(yturi)
                    print( "    {1} :: {0}".format(title, yturi))
                ytdl.append(ytdlpl)
                folder_titles.append(playlist['name'])
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return result, ytdl, folder_titles

# collect everything up for youtube-dl
tracks, uris, folder_titles = get_playlists(s.uname)

# create folders to store playlist items and download music
for i in range(len(folder_titles)):
    title = "".join([c for c in folder_titles[i] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    p = os.path.join(os.path.normpath(s.output_path), title)
    os.mkdir(p)
    p2 = os.path.join(p, title+".ytdl")
    with open(p2, 'w') as f:
        for listitem in uris[i]:
            f.write('%s\n' % listitem)
    # download!
    r = subprocess.Popen(["youtube-dl.exe","--batch-file", p2, "--format", "140", "-o", s.output_path+"//"+title+"//"+"%(title)s.%(ext)s"], stdout=subprocess.PIPE)
    #r = subprocess.Popen(["youtube-dl.exe","--batch-file", p2, "-f", "140"], stdout=subprocess.PIPE)
    for i in r.stdout: 
        print(i.rstrip().decode('UTF-8'))
    