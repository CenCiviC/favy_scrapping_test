from api.youtubeapi import get_channel_id, get_youtube_channel_info
from api.aws import save_file_to_s3
from api.gpt import categorize_image
from api.googleapi import search_related_product, search_same_product

from utils.files import download_image_by_url, convert_image_to_webp, delete_local_file
from utils.string import encode_to_base62
from utils.date import calculate_season_by_date

from content.product import Product
from content.video import Video


LINK = "https://d1wa6tg9pd3mhn.cloudfront.net/"


def controller_video(video_id):    
    channelId, title,date,link, s3location = controller_codies(video_id)
    thumbnailLocation = LINK + s3location
    video = Video(channelId,video_id)
    
    
    if not video:
        return None
    
    
    codies = video.return_coordis()
    if not codies:
        return None
    
    # codyList 및 productList를 미리 초기화
    codyList = []
    season = get_season(date) 

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
                "productImg": LINK + s3location,
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
            "filmImg": LINK + filmImg,
            "filmUrl": LINK + filmUrl,
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
        
def controller_product(url):
    product= Product(url)
    productName, productNo,brand, s3location, sale_price, price, category, color,siteName, siteUrl, logoUrl = product.save_product_info()
    
    data = {
        "brand": brand,
        "category": category,
        "color": color,
        "productImg": LINK + s3location,
        "productName": productName,
        "productNo": productNo,
        "season": "보류",
        "status": "b",

        "price": sale_price,

        "regularPrice": price,
        "salesImg": logoUrl,
        "salesName": siteName,
        "salesUrl": siteUrl,
    }
    
    return data

def controller_product_detail(image_url, product_name):
    category, color = categorize_image(image_url, product_name)
    
    data = {
        "brand": category,
        "category": color,
    }
    
    return data
    
def controller_related_product(image_url, product_name):
    page_token, realted_product_links = search_related_product(image_url)
    
    related_product_list = []
    rank = 1

    for link in realted_product_links:
        product= Product(link)
        if not product.valid:
            continue
        
        if product.productInformation.productName == product_name:
            continue
        productName, productNo,brand, s3location, sale_price, price, category, color,siteName, siteUrl, logoUrl = product.save_product_info()
        product_info = {
            "similarityRank" : rank,
            "brand": brand,
            "category": category,
            "color": color,
            "productImg": LINK + s3location,
            "productName": productName,
            "productNo": productNo,
            "status": "b",

            "price": sale_price,
            "regularPrice": price,
            "salesImg": logoUrl,
            "salesName": siteName,
            "salesUrl": siteUrl,
        }
        related_product_list.append(product_info)
        rank+=1
        
    
    data = {
        "relatedProductList": related_product_list
    }
    
    return data

def controller_same_product(page_token):
    #page token을 했을 때 image_sources가 있는지 없는지로 확인함
    same_product_links = search_same_product(page_token)
    
    related_product_list = []
    rank = 1

    for link in same_product_links:
        product= Product(link)
        if not product.valid:
            continue

        productName, productNo,brand, s3location, sale_price, price, category, color,siteName, siteUrl, logoUrl = product.save_product_info()
        product_info = {
            "similarityRank" : rank,
            "brand": brand,
            "category": category,
            "color": color,
            "productImg": LINK + s3location,
            "productName": productName,
            "productNo": productNo,
            "status": "b",

            "price": sale_price,
            "regularPrice": price,
            "salesImg": logoUrl,
            "salesName": siteName,
            "salesUrl": siteUrl,
        }
        related_product_list.append(product_info)
        rank+=1
        
    
    data = {
        "relatedProductList": related_product_list
    }
    
    return data
   

#############download image by manual / url or local

# url = "https://bohemseo.com/web/product/extra/small/202311/868905f3319d84db550e72fdcc55f60e.jpg"
# name = "[ 15TH REORDER ] LAYERED CHAIN NECKLACE"
# location = download_product_img_by_url(name, url)
# print(location)



#####################
# name = "[ 15TH REORDER ] LAYERED CHAIN NECKLACE"
# imgLocation = encodeByBase62(name)
# print(f"product/{imgLocation}.webp")


##############
# urls = [
# "https://www.youtube.com/watch?v=fDuR9oXB8ys",
    
# ]

    

# for url in urls:
#     channelId = controller_celeb(url)
#     if not channelId:
#         continue

#     vidoes = get_videos_from_channel(channelId)

#     for video in vidoes:
#         controller_codies(video)
        
######################contorl video

# newVideo = control_video("윤비누YOONSOAP","5KtYkJzax0I")
# start_time = time.time()
# video_ids = get_videoId_from_codies(30,35)
# for id in video_ids:
#     try:
#         newVideo = control_video("해수haesu",id)
#     except:
#         print(f"video {id} occurs error")
#         continue

# video_ids = get_videoId_from_codies(20,23)
# for id in video_ids:

#     newVideo = control_video("해수haesu",id)

    

# end_time = time.time()

# print(f"spend time : {end_time - start_time:.5f} sec")

# #update_categories_and_colors(101,260)

