import requests as r
import pandas as pd
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
### advanced-data-analytics-servic@practice-for-class-453600.iam.gserviceaccount.com
### API Key: AIzaSyBPvLJOBUpGHfsVD9A2kHMlFbBvQ3gUV0s
import json
from gspread_dataframe import set_with_dataframe
import os

### Scope for google sheets

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"
        ]



# If running in GitHub Actions, retrieve the secret and write it to a temp file
if 'GCP_SERVICE_ACCOUNT_KEY' in os.environ:
    # Write the secret (the content of the JSON file) to a temp file
    json_keyfile = '/tmp/gcp-key.json'
    with open(json_keyfile, 'w') as json_file:
        json_file.write(os.environ['GCP_SERVICE_ACCOUNT_KEY'])

    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
else:
    # Default behavior for local development (if you want to use a local file for testing)
    creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)

if 'APIKEY' in os.environ:
    # Write the secret (the content of the JSON file) to a temp file
    APIKEY = os.environ['APIKEY']
else:
    # Default behavior for local development (if you want to use a local file for testing)
    APIKEY = 'nothing to see here'

def get_transcript(video_id):
    #yt = YouTube(video_url)
    #video_id = yt.video_id

    #video_url = 'https://www.youtube.com/watch?v=' + video_id

    # Get the transcript
    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # Extract text from the transcript
    text = ''
    for entry in transcript:
        text += entry['text'] + ' '
    return text



channels = [
    {'name': 'The Late Show with Stephen Colbert', 'handle': 'ColbertLateShow', 'id': 'UCMtFAi84ehTSYSE9XoHefig', 'playlist_id': 'UUMtFAi84ehTSYSE9XoHefig'},
    {'name': 'Late Night with Seth Meyers', 'handle': 'LateNightSeth', 'id': 'UCVTyTA7-g9nopHeHbeuvpRA', 'playlist_id': 'UUVTyTA7-g9nopHeHbeuvpRA'}
    ]

### Fetch the videos

all_videos = []

for channel in channels:
    channel_videos = []
    video_url = f"https://www.googleapis.com/youtube/v3/playlistItems?"
    params = {'part':['snippet','contentDetails'], 'maxResults':50, 'playlistId':channel['playlist_id'], 'key': APIKEY}
    videos_call = r.get(video_url, params=params)
    print  (videos_call)
    print (videos_call.json())
    for video_item in videos_call.json()['items']:
        video_info_metal = {'title': video_item['snippet']['title'],
                            'description': video_item['snippet']['description'],
                            'author': video_item['snippet']['videoOwnerChannelTitle'],
                            'date': video_item['snippet']['publishedAt'][:-1],
                            'url': 'https://www.youtube.com/watch?v=' +video_item['contentDetails']['videoId'],
                            'video_id': video_item['contentDetails']['videoId']
                           }
        channel_videos.append(video_info_metal)
        ### Fetch the metrics for the video
    all_videos.extend(channel_videos)

    
### Get the current date, so we can only keep the most recent videos (last day)

yesterdays_date = datetime.today() - timedelta(days=1)
target_date = yesterdays_date.strftime("%Y-%m-%d")

target_videos = [x for x in all_videos if x['date'][0:10] == target_date]


# Fetch the video engagement metrics and transcript

for video in target_videos:
    video_info_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {'part':'statistics', 'id':video['video_id'], 'key': APIKEY}
    video_info_call =  r.get(video_info_url, params=params)
    metrics = {'yt_views': video_info_call.json()['items'][0]['statistics']['viewCount'] if 'viewCount' in video_info_call.json()['items'][0]['statistics'].keys() else 'Not available',
               'yt_likes': video_info_call.json()['items'][0]['statistics']['likeCount'] if 'likeCount' in video_info_call.json()['items'][0]['statistics'].keys() else 'Not available',
               'yt_favorites': video_info_call.json()['items'][0]['statistics']['favoriteCount'] if 'favoriteCount' in video_info_call.json()['items'][0]['statistics'].keys() else 'Not available',
               'yt_comments': video_info_call.json()['items'][0]['statistics']['commentCount'] if 'commentCount' in video_info_call.json()['items'][0]['statistics'].keys() else 'Not available'
              }
    video.update(metrics)
    try:
        transcript = get_transcript(video['video_id'])
        video.update({'transcript': transcript})
    except:
        transcript = 'no transcript available'
        video.update({'transcript': transcript})




print ('test')

### Enrich with mentions of your query


target_videos_df = pd.DataFrame(target_videos)

target_videos_df = target_videos_df.sort_values(by = 'date', ascending=True)


### write to google sheets



client = gspread.authorize(creds)

spreadsheet = client.open("talk show")

worksheet = spreadsheet.worksheet("Historical")  # Use Historical or use sheet's name like: spreadsheet.worksheet("Sheet1")


last_row = len(worksheet.col_values(1))
set_with_dataframe(worksheet, target_videos_df,
        row=last_row + 1,
        include_column_header=False,
    )

#set_with_dataframe(worksheet, all_videos_df)#, row=1, col=1)

print ('test')

print ('break here')