from googleapiclient.discovery import build
from datetime import datetime
from typing import Optional, List, Tuple
from dotenv import load_dotenv
import os 

# load .env
load_dotenv()
api_key = os.environ.get('YOUTUBE_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)

def get_channel_id(url: str) -> Optional[str]:
    """youtube link로부터 채널 ID를 가져옵니다.

    Args:
        url (str): youtube link.

    Returns:
        Optional[str]: channel id. 
    """
    videoId = url.split("v=")[-1]
    request = youtube.videos().list(
        part="snippet",
        id=videoId,
    )
    response = request.execute()
    
    if response['items']:
        return response['items'][0]['snippet']['channelId']
    else:
        return None

def get_video_ids_from_channel(channel_id: str) -> List[str]:
    total_video_count = 20
    video_count = 15
    recent_video_count = total_video_count - video_count
    video_details = []
    next_page_token = None
    
    prev_video_details = []
    for videoDuration in ["medium", "long"]:
        # 초기 페이지 토큰 설정
        next_page_token = None
        
        summerStart = datetime(2023, 5, 1).isoformat() + 'Z'
        summerEnd = datetime(2023, 9, 1).isoformat() + 'Z'
        
        #옛날 영상
        for _ in range(1):  # 각 비디오 길이 유형당 한 번의 요청을 수행
            request = youtube.search().list(
                channelId=channel_id,
                part='snippet', 
                maxResults=50,  
                pageToken=next_page_token,
                type='video',
                videoDuration=videoDuration,
                publishedAfter= summerStart,
                publishedBefore = summerEnd,
                order='date',
            )
            response = request.execute()
            
            # videoId와 publishTime 추출
            prev_video_details += [(item['id']['videoId'], item['snippet']['publishedAt']) for item in response['items']]
            
            # 다음 페이지 토큰 업데이트 (여기서는 사용하지 않음)
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
            
    #예전 영상 시간순으로 15개
    prev_video_details.sort(key=lambda x: datetime.strptime(x[1], '%Y-%m-%dT%H:%M:%SZ'), reverse=False)
    prev_top_video_details = prev_video_details[:video_count]
    
    recent_video_details = []
    for videoDuration in ["medium", "long"]:    
        #최근 영상
        for _ in range(1):  # 각 비디오 길이 유형당 한 번의 요청을 수행
            request = youtube.search().list(
                channelId=channel_id,
                part='snippet', 
                maxResults=recent_video_count,  
                pageToken=next_page_token,
                type='video',
                videoDuration=videoDuration,
                publishedAfter= summerEnd,
                order='date',
            )
            response = request.execute() 
            
            
            
            # videoId와 publishTime 추출
            recent_video_details += [(item['id']['videoId'], item['snippet']['publishedAt']) for item in response['items']]
            
            # 다음 페이지 토큰 업데이트 (여기서는 사용하지 않음)
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
    
    recent_video_details.sort(key=lambda x: datetime.strptime(x[1], '%Y-%m-%dT%H:%M:%SZ'), reverse=True)
    recent_top_video_details = recent_video_details[:recent_video_count]
    
    video_details += recent_top_video_details
    video_details += prev_top_video_details
    
    # 발행 시간에 따라 비디오 정렬
    video_details.sort(key=lambda x: datetime.strptime(x[1], '%Y-%m-%dT%H:%M:%SZ'), reverse=True)
    
    # 상위의 비디오 ID 선택
    top_video_ids = [video[0] for video in video_details][:total_video_count]
    
    return list(set(top_video_ids)) 

def get_full_video_description(video_id: str)-> str:
    """영상 id로 caption 가져오기

    Args:
        video_id (str): _description_

    Returns:
        str: _description_
    """
    request = youtube.videos().list(part='snippet', id=video_id)
    response = request.execute()
    return response['items'][0]['snippet']['description']

def get_youtube_channel_info(channel_id: str) -> Tuple[str,str,str,str,str,str,str]:
    """channel id로 채널 정보 가져옵니다.

    Args:
        channel_id (str): _description_

    Returns:
        Tuple[str,str,str,str,str,str,str]: name,profileImg,youtubeId,youtubelink,channelId,subscriberCnt, videoCount
    """
    request = youtube.channels().list(
        part='snippet',
        id=channel_id
    )
    response = request.execute()
    name= response['items'][0]['snippet']['title']
    profileImg= response['items'][0]['snippet']['thumbnails']["medium"]["url"]
    youtubeId =  response['items'][0]['snippet']['customUrl']
    youtubelink =  "youtube.com/" + response['items'][0]['snippet']['customUrl']
    channelId =   response['items'][0]['id']
    
    
    request = youtube.channels().list(
        part='statistics',
        id=channel_id
    )
    response = request.execute()
    subscriberCnt = response['items'][0]['statistics']['subscriberCount']
    videoCount = response['items'][0]['statistics']['videoCount']


    return (name,profileImg,youtubeId,youtubelink,channelId,subscriberCnt, videoCount)

def get_youtube_video_info(video_id: str) -> Tuple[str,str,str,str,str]:
    """video id로부터 video 정보를 가져옵니다.

    Args:
        video_id (str): _description_

    Returns:
        Tuple[str,str,str,str,str]: channelId, title,date,link,thumbnailImg
    """
    request = youtube.videos().list(part='snippet', id=video_id)
    response = request.execute()
    
    name = response['items'][0]['snippet']['channelTitle']
    date = response['items'][0]['snippet']['publishedAt']
    title = response['items'][0]['snippet']['title']
    thumbnailImg = response['items'][0]['snippet']['thumbnails']["maxres"]["url"]
    link = f"https://www.youtube.com/watch?v={video_id}"
    channelId = response['items'][0]['snippet']['channelId']
    return (channelId, title,date,link,thumbnailImg)