from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver

from typing import List, Optional, Tuple

from .scraper import WebScraper

from dotenv import load_dotenv
import os 

from packages.utils.string import extract_instagram_id_and_index
from packages.utils.string import encode_to_base62
from packages.utils.files import delete_local_file
from packages.utils.files  import download_image_by_url

from packages.api.aws import save_file_to_s3

load_dotenv()
S3_CDN_DOMAIN = os.environ.get('S3_CDN_DOMAIN')


class InstagramExtractor:     
    def __init__(self, instagram_url): 
        self.influencer_name: str = ""
        self.shot_url: str = ""
        self.media_id: str = ""
        self.influencer_profile: str = ""
        self.upload_date: str = ""
        
        media_id , index = extract_instagram_id_and_index(instagram_url)
        self.media_id = media_id
        
        self.scraper = WebScraper(instagram_url)
        self.extract_img_info(index)
        self.save_instagram_img()
        
        
    #일반상황 li 2 전사진 li3 진짜
    #첫번째 사진일 때 / list2 진짜 li3 후사진
    #한장밖에 없는 사진일 때 / 아예 logic이 다른 듯함
    def extract_img_info(self, index: int):
        driver = self.scraper.get_webdriver()
        
        if not driver:
            return None

        ##profile 아래에 주소 적힌 것 때문에 차이 존재        
        try:
            _ = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div._aagv > img")))
            ##profile img

            profile_img_candi = [ "header._aaqw > div > div > span > img" , "header._aaqw > div > div > a > img"]
            for profile_img_ele in profile_img_candi:
                try:
                    profile_img_element = driver.find_element(By.CSS_SELECTOR, profile_img_ele)
                    break
                except:
                    continue
            self.influencer_profile = profile_img_element.get_attribute("src")
            
            
            ##name
            influencer_name_candi = [ "div._aaqt > div > span > a" , "h2._a9zc >div >a"]
            for influencer_name_ele in influencer_name_candi:
                try:
                    self.influencer_name = driver.find_element(By.CSS_SELECTOR, influencer_name_ele).text
                    break
                except:
                    continue
            

            ##image
            if index == 1:
                shot_image_candi = [
                "ul._acay > li:nth-child(2) > div > div > div > div > div._aagu._aa20._aato > div._aagv > img" , 
                "ul._acay > li:nth-child(2) > div > div > div > div > div._aagv > img"]
            elif index == 0:
                shot_image_candi = ["div._aagv > img"]
            else:
                shot_image_candi = [
                "ul._acay > li:nth-child(3) > div > div > div > div > div._aagu._aa20._aato > div._aagv > img" , 
                "ul._acay > li:nth-child(3) > div > div > div > div > div._aagv > img"]
            
            

            for shot_image_ele in shot_image_candi:
                try:
                    image_element = driver.find_element(By.CSS_SELECTOR, shot_image_ele)
                    srcset = image_element.get_attribute('srcset')
                    break
                except:
                    continue
            

            # 1080x1080 해상도 URL 찾기
            image_url = None
            for src in srcset.split(','):
                if '1080w' in src:
                    image_url = src.split(' ')[0]  # URL 부분만 추출
                    self.shot_url = image_url
                    break
            ##date
            date_element = driver.find_element(By.CSS_SELECTOR, "time._a9ze")
            datetime = date_element.get_attribute("datetime")
            self.upload_date = datetime
        
            
        except:
            return None
            
    
    def valid(self):
        return self.shot_url and self.influencer_name and self.media_id and self.influencer_profile and self.upload_date
    
    def save_instagram_img(self):
        assert isinstance(S3_CDN_DOMAIN, str), "S3_CDN_DOMAIN must be a string"
        
        if not self.valid():
            raise ValueError("instagram url error")
        
        encoded_name = encode_to_base62(self.influencer_name)
        shot_url = self.shot_url
        media_id = self.media_id
        file_name = f"{media_id}.webp"
        
        if download_image_by_url(shot_url, media_id):
            s3location = f"{encoded_name}/{file_name}"
            save_file_to_s3(file_name, s3location, True)
            delete_local_file(file_name, is_img=True)
            s3_shot_url = S3_CDN_DOMAIN + s3location
            self.shot_url = s3_shot_url
        else:
            raise ValueError("download image error")
        
    ##TODO: DB에 없으면 profile img도 s3에 저장