#service
def service_video(video_id:str):
    data = video_id
    return data



#데이터 scrape or sort with api and s3에 저장  한 class에서 다루자-> json 형태로 변환 -> api 쏴주기
# service / json.py/ app.py


from api.youtubeapi import get_channel_id, get_youtube_channel_info,get_youtube_video_info
from api.aws import save_file_to_s3
from api.gpt import categorize_image
from api.googleapi import search_related_product, search_same_product

from utils.files import download_image_by_url, convert_image_to_webp, delete_local_file
from utils.string import encode_to_base62
from utils.date import calculate_season_by_date

from content.product import Product
from content.video import Video

from dotenv import load_dotenv
import os 

load_dotenv()
S3_CDN_DOMAIN = os.environ.get('S3_CDN_DOMAIN')

def controller_celeb(url: str):
    #TODO: location 수정 필요
    try:
        id = get_channel_id(url)
        name,profileImg,youtubeId,youtubelink,channelId,subscriberCnt,videoCnt = get_youtube_channel_info(id)

        imgLocation = f"{name}_profile"
        download_image_by_url(profileImg, imgLocation)
        s3location = f"{name}/{imgLocation}.webp"
        save_file_to_s3( f"{imgLocation}.webp", s3location, True)

        data = [name, youtubeId, channelId, videoCnt,subscriberCnt, youtubelink, s3location]
        #save_celeb_data_to_sheet(data)
    except:
        return None
    return channelId

def controller_codies(video_id):
    channelId, title,date,link,thumbnailImg = get_youtube_video_info(video_id)

    imgLocation = f"{video_id}"
    download_image_by_url(thumbnailImg, imgLocation)
    

    
    s3location = f"{channelId}/{imgLocation}.webp"
    save_file_to_s3(f"{imgLocation}.webp", s3location, True)
    
    delete_local_file(f"{imgLocation}.webp", is_img=True)

    data = [channelId, title,date,link, s3location]
    return data


def controller_video(video_id):    
    channelId, title,date,link, s3location = controller_codies(video_id)
    thumbnailLocation = S3_CDN_DOMAIN + s3location
    video = Video(channelId,video_id)
    
    
    if not video:
        return None
    
    
    codies = video.return_coordis()
    if not codies:
        return None
    
    # codyList 및 productList를 미리 초기화
    codyList = []
    season = calculate_season_by_date(date) 

    for cody in codies:
        # 각 cody에서 필요한 정보 추출
        codyId = cody.cody_id 
        filmImg = cody.filmImg
        filmUrl = cody.filmUrl
        timeLine = cody.timeline
        
        # cody의 products에 대한 정보 처리
        productList = []
        for product in cody.products:
            productName, productNo,brand, s3location, sale_price, price, category, color,siteName, siteUrl, logoUrl = product.save_product_info()
            # product 정보를 JSON 형식의 딕셔너리로 변환
            product_info = {
                "brand": brand,
                "category": category,
                "color": color,
                "productImg": S3_CDN_DOMAIN + s3location,
                "productName": productName,
                "productNo": productNo,
                "season": season,
                "status": "b",

                "price": sale_price,
                "regularPrice": price,
                "salesImg": logoUrl,
                "salesName": siteName,
                "salesUrl": siteUrl,
            }
            productList.append(product_info)
        
        # cody 정보를 JSON 형식의 딕셔너리로 변환
        cody_info = {
            "codyId": codyId,
            "filmImg": S3_CDN_DOMAIN + filmImg,
            "filmUrl": S3_CDN_DOMAIN + filmUrl,
            "timeLine": timeLine,
            "productList": productList  # products 정보 추가
        }
        codyList.append(cody_info)

    # 최종 JSON 데이터 구성
    data = {
        "channelId": channelId,
        "codiesId": video_id,
        "date": date,
        "filmImg": link,
        "filmUrl": thumbnailLocation,
        "title": title,
        "codyList": codyList  # codies 정보 추가
    }  
    
    return data