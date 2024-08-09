#service
from scraper.instagram import InstagramExtractor
from typing import Tuple, Optional, List
from jsonify import *

def service_instagram_shot_info(url:str):
    extractor = InstagramExtractor(url)
    if not extractor.valid():
        return None
    extractor.save_instagram_img()
    
    #TODO: 현재 db에 해당 인플루언서가 저장되어있는지 확인
    return jsonify_instagram_shot(extractor.influencer_name, extractor.influencer_profile, extractor.shot_url)
