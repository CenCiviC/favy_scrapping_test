from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import requests
import certifi

class WebScraper:
    def __init__(self, url):
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*; q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.8,en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Charset": "UTF-8,*;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        }
        
        session = requests.Session()
        redirectUrl = session.head(url, allow_redirects=True, timeout=10).url
                    
        self.response = requests.get(redirectUrl, headers=headers, verify=certifi.where(), allow_redirects=True, timeout=10)        
        self.url = self.response.url
        content_type = self.response.headers['content-type']
        

        if not 'charset' in content_type:
            self.response.encoding = self.response.apparent_encoding
        
        
    
    def get_beautifulSoup(self):
        soup = BeautifulSoup(self.response.text, 'html.parser')
    
        return soup

    
    def get_webdriver(self):
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.get(self.url)
    
        return driver

    def check_response_status(self) -> bool:
        return self.response.status_code == 200