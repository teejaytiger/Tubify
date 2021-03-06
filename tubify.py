from genericpath import exists
import os, subprocess, sys
from posixpath import splitext
import spotipy
import yaml
from spotipy.oauth2 import SpotifyOAuth
from youtube_search import YoutubeSearch
from difflib import SequenceMatcher
from subprocess import Popen, PIPE


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
    scope="playlist-read-private playlist-read-collaborative")
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
    folder_titles = []
    #playlists = sp.user_playlists(username)
    playlists = sp.user_playlists(username)
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            if s.show_playlists: print (playlist['name'])
            ytdlpl = []
            # determine if the playlist is specified in the config file
            similarity = []
            for pl in s.playlists:
                similarity.append(SequenceMatcher(None, pl, playlist['name']).ratio())
            # only grab playlists in the config file if they're 90% similar or higher
            if (max(similarity) >= s.pl_similarity) and (not s.show_playlists):
                print("%4d %s" % (i + 1 + playlists['offset'],  playlist['name']))
                pluri = playlist['uri'].split(":")[2]
                tracks = get_playlist_tracks(username, pluri)
                for track in tracks:
                    title = track["track"]["album"]["artists"][0]["name"]+" - "+track["track"]["name"]
                    if s.assert_music:
                        title += " "+s.assert_music_string
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
if not s.show_playlists:
    for i in range(len(folder_titles)):
        title = "".join([c for c in folder_titles[i] if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        # create the music folder path

        # case for named playlist folders
        if s.playlist_folders:
            p = os.path.join(os.path.normpath(s.output_path), title)
            p3 = title
            p2 = os.path.join(p, p3+".ytdl")
            if not os.path.isdir(p):
                os.mkdir(p)

        # case for aggregated download
        else:
            p = os.path.normpath(s.output_path)
            p3 = "playlist"
            p2 = os.path.join(p, p3+".ytdl")
            if not os.path.isdir(p):
                os.mkdir(p)

        # append untracked songs
        with open(p2, 'a+') as f:
            f.seek(0)
            songs = [i.rstrip() for i in f.readlines()]
            for k, uri in enumerate(uris[i]):
                if not uri in songs:
                    f.write('%s\n' % uri)

        # download!
        # case for numbering tracks to preserve order
        if s.download:
            if s.number_tracks:
                r = subprocess.Popen(
                    [
                        s.youtube_dl_path,
                        "-ciw",
                        "--download-archive", os.path.join(p, p3+".txt"), 
                        "--batch-file", p2, 
                        "--restrict-filenames", 
                        "--format", "140", 
                        "-o", p+"//"+"%(autonumber)s-%(title)s.%(ext)s"
                    ], 
                    stdout=subprocess.PIPE)
            # case for not numbering tracks
            else:
                r = subprocess.Popen(
                    [
                        s.youtube_dl_path,
                        "-ciw",
                        "--download-archive", os.path.join(p, p3+".txt"),
                        "--batch-file", p2, 
                        "--restrict-filenames", 
                        "--format", "140", 
                        "-o", p+"//"+"%(title)s.%(ext)s"
                    ], 
                    stdout=subprocess.PIPE)

            for line in iter(r.stdout.readline, b''):
                print(line.decode('cp1252'), end="\r", file=sys.stdout, flush=True)
    print ("[DONE]\n")

if s.convert_to_mp3:
    print("[POST] Converting files to mp3. See dirname/dirname for converted files.")
    count = 0
    cmds = []
    convert_p = os.path.join(s.output_path,"CONVERTED")
    if not os.path.exists(convert_p): os.mkdir(convert_p)
    for subdir, dirs, files in os.walk(s.output_path):
        for d in dirs[1:]:
            p = os.path.join(convert_p, d)
            if not os.path.exists(p): os.mkdir(p)
        for file in files:
            parent_folder = os.path.split(subdir)[1]
            bname, ext = os.path.splitext(file)
            if "m4a" in ext:
                fname = bname+".mp3"
                cmds.append( [
                    s.ffmpeg_install_location,
                    '-i', "\""+os.path.join(subdir, file)+"\"",
                    '-acodec', 'libmp3lame',
                    '-ac', '2',
                    '-q:a', '2',
                    "\""+os.path.join(convert_p, parent_folder, fname)+"\""] )
                count+=1
    i = 1
    for command in cmds:
        print("converting {0}/{1} - {2}".format(i, count, os.path.split(command[2])[1]))
        #print(" ".join(command)) # debug
        ffmpeg = subprocess.Popen(" ".join(command), stderr=subprocess.PIPE, stdout = subprocess.PIPE )
        stdout, stderr = ffmpeg.communicate()
        i+=1