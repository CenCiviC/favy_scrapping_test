#service
from scraper.insta import InstagramExtractor
from model.shot import crop_images_by_instagram_url
from api.googleapi import search_related_product
from jsonify import *
from content.product import Product

from typing import Tuple, Optional, List

def service_instagram_info(url:str):
    extractor = InstagramExtractor(url)
    if not extractor.valid():
        return None
    
    #TODO: 현재 db에 해당 인플루언서가 저장되어있는지 확인
    return jsonify_instagram_info(extractor.influencer_name, extractor.influencer_profile, extractor.shot_url,extractor.upload_date)

def service_instagrm_shot_info(instagram_url: str):
    extractor = InstagramExtractor(instagram_url)

    media_id = extractor.media_id
    shot_url = extractor.shot_url

    urls = crop_images_by_instagram_url(media_id, shot_url)

    json_datas = []
    seen = []  # 중복 확인을 위한 리스트 생성
    
    for url in urls:
        _, related_product_links = search_related_product(url)
        
        for link in related_product_links:
            # 상품 유효성 확인
            product = Product(link)
            if not product.valid:
                continue
            
            product_info = product.save_product_info()
            
            # 이미 처리된 항목인지 확인
            if product_info in seen:
                continue
            
            seen.append(product_info)  # 중복을 방지하기 위해 리스트에 추가
            
            product_info = json_product_info(product_info)
            json_datas.append(product_info)
        
    return jsonify_instagram_shot_info(
        extractor.influencer_name, 
        extractor.influencer_profile, 
        extractor.shot_url, 
        extractor.upload_date, 
        json_datas
    )
