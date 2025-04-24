import requests as r
import pandas as pd

### Fetch channel ID

apikey = 'enter key here'

url = 'https://www.googleapis.com/youtube/v3/channels'
params = {'part': 'id', 'forHandle': 'LateNightSeth', 'key': apikey}
call = r.get(url, params=params)
channel_id = call.json()['items'][0]['id']

call.json()

channel_id

playlist_url = "https://www.googleapis.com/youtube/v3/channels"
params = {'part': 'contentDetails', 'id': channel_id, 'key':apikey}
playlist_call = r.get(playlist_url, params=params)

playlist_call.json()

UPLOADS_PLAYLIST_ID = playlist_call.json()['items'][0]['contentDetails']['relatedPlaylists']['uploads']

UPLOADS_PLAYLIST_ID

### End here

playlist_call.json()

video_url = f"https://www.googleapis.com/youtube/v3/playlistItems?"
params = {'part':['snippet','contentDetails'], 'maxResults':50, 'playlistId':UPLOADS_PLAYLIST_ID, 'key': apikey}
videos_call = r.get(video_url, params=params)

video_info = videos_call.json()['items']

video_ids = [x['contentDetails']['videoId'] for x in video_info]

len(video_ids)

video_info_url = "https://www.googleapis.com/youtube/v3/videos"
params = {'part':'statistics', 'id':video_ids[1], 'key': apikey}
video_info_call =  r.get(video_info_url, params=params)

video_info_call.json()

video_ids[-1]

video_info[0]

