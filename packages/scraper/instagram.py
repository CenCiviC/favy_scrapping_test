from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver

from typing import List, Optional, Tuple

from .scraper import WebScraper

from dotenv import load_dotenv
import os 

from utils.string import extract_instagram_id_and_index
from  utils.string import encode_to_base62
from utils.files import delete_local_file
from utils.files  import download_image_by_url

from api.aws import save_file_to_s3

load_dotenv()
S3_CDN_DOMAIN = os.environ.get('S3_CDN_DOMAIN')


class InstagramExtractor:     
    def __init__(self, instagram_url): 
        self.influencer_name: str = ""
        self.shot_url: str = ""
        self.media_id: str = ""
        self.influencer_profile: str = ""
        
        media_id , index = extract_instagram_id_and_index(instagram_url)
        self.media_id = media_id
        
        scrape_url = "https://snapinsta.app/"
        self.scraper = WebScraper(scrape_url)
        self.extract_img_info(instagram_url, index)
        
        
    def extract_img_info(self, instagram_url, index):
        driver = self.scraper.get_webdriver()
        
        if not driver:
            return None
        
        try:    
            input_field = driver.find_element(By.NAME, "url")
            input_field.send_keys(instagram_url)
            submit_button = driver.find_element(By.ID, 'btn-submit')  # 예시로 ID를 사용
            # 제출 버튼 클릭
            submit_button.click()

            #페이지 전환
            element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'download')))
            
            #instagram id
            self.influencer_name = driver.find_element(By.XPATH, '//*[@id="download"]/div[1]/div[1]/div/div[1]/div').text

            #img url 
            # img_elements = driver.find_elements(By.CSS_SELECTOR, '.media-box > img')
            # self.shot_url = img_elements[index-1].get_attribute("src")
            
            img_element = driver.find_element(By.CSS_SELECTOR, '.download > div.row > div:nth-child(1) > div > div.media-box > div > a')
            self.shot_url = img_element.get_attribute("href")        
            
            #profile image url
            profile_img_element = driver.find_element(By.XPATH, '//*[@id="download"]/div[1]/div/div/div[1]/div/img')
            self.influencer_profile = profile_img_element.get_attribute("src")
            
        except:
            return None
            
    
    def valid(self):
        return self.shot_url and self.influencer_name and self.media_id and self.influencer_profile
    
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