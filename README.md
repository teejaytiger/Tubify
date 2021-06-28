# Tubify
Finds your favorite Spotify songs on YouTube

## Installation Instructions
### Windows
After installing Python 3.9, extract the files to the desired location and run `python -m pip install requirements.txt`  
This will install all the prerequisites.

If you encounter issues, consult the [official installation instructions for youtube-dl](https://ytdl-org.github.io/youtube-dl/download.html) or check [the documentation](https://github.com/ytdl-org/youtube-dl/blob/master/README.md#readme)

### Linux
Install youtube-dl with `sudo apt-get install youtube-dl` and modify `youtube_dl_path` in the config.yaml file to reflect the path to the executable.

> you can also follow [the official instructions](https://ytdl-org.github.io/youtube-dl/download.html)

### OSX
Follow the instructions at [the official youtube-dl documentation](https://ytdl-org.github.io/youtube-dl/download.html)

## Installation continued (All OS)

### Configuration

After installing Tubify, open `config.yaml` in the text editor of your choice and change `uname` to your own Spotify username (can be found in your Spotify account settings) and change `output_folder` to the folder you'd like to store any downloads the software might make in.  

> HINT: Use `spotify` as the username if you'd like to match YoutTube links to a public spotify playlist.  

Multiple playlists can be downloaded to the same folder or as separate subfolders by changing the `playlist_folders` setting. `playlists` is a list indicating which playlists you'd like to download by name. By default, account playlist names with at least 90% similarity to what's indicated will be downloaded. To change this threshold, modify `pl_similarity` in the config file. Change the value to a 1 to enforce downloading perfectly matched playlist names only. This setting is intended to allow wiggle room for some special characters that may be irreproduceable by a basic user.  

> By default, tubify will show you playlists without downloading or matching YouTube links. You can use this opportunity to copy playlist titles accurately into the configuration file. Just be sure to check out [the documentation](https://www.yaml.info/learn/quote.html) if you're unsure how to format yaml scalars (text strings) that contain special characters.  

When you run for the first time, tubify will connect your Spotify account. After you're logged in and authorize tubify on your account, copy the URL in the address bar of your browser and paste it into the cmd window field to continue running the software.  

After getting the configuration set, simply run `python tubify.py` to match your Spotify playlists to YouTube URLs! Please note that tubify uses the first relevant match on YouTube. It's not going to get it right every time, especially with rarer tracks, but it will most of the time!  

> NOTE: Do not use this software to Download tracks you do not have the rights for. This software is experimental and intended to match YouTube links to Spotify playlist contents in bulk. It is not intended as a piracy tool. Please consult your local laws and regulations before configuring the software to do anything it is unintended for. 