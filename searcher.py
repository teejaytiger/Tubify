from youtube_search import YoutubeSearch
import yaml

prefix = "https://www.youtube.com/watch?v="
results = YoutubeSearch('Macklemore - And We Danced (feat. Ziggy Stardust)', max_results=1).to_dict()
suffix = results[0]["id"]
uri = prefix+suffix