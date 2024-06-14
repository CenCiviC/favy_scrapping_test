from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import certifi
import time
from typing import List, Optional

from utils.string import extract_shoppingmall_name, check_common_substring, encode_to_base62
from utils.number import extract_price, is_currency
from utils.files import delete_local_file
from utils.files  import download_image_by_url

from api.gpt import categorize_image
from api.aws import save_file_to_s3

class ProductInfo:
    def __init__(self) -> None:
        self.siteName: Optional[str] = None
        self.siteUrl: Optional[str] = None
        self.productName: Optional[str] = None
        self.price: Optional[int] = None
        self.sale_price: Optional[int] = None
        self.imageUrl: Optional[str] = None
        self.category: Optional[str] = None
        self.brand: Optional[str] = None
        self.color: Optional[str] = None
        self.logoUrl: Optional[str] = None
        self.haveRelatedProduct: bool = True
    
    def decompose_info(self):
        return self.productName, self.brand, self.imageUrl, self.sale_price, self.price, self.category, self.color,self.siteName, self.siteUrl, self.logoUrl, self.haveRelatedProduct
        

class ShoppingMallInfoExtractor: 
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
    

    def __init__(self, url): 
        self.info = ProductInfo()
        
        if url == None:
            return
        
        if not self.consider_shoppingmall(url):
            print(f"Error {url}")
            return

        if self.valid_product() == False:
            if self.info.siteUrl:
                self.lazy_extract_dynamic_shoppingmall_info()
            
        if self.valid_product():
            self.info.category = "보류"
            self.info.color = "보류"
            
            # 할인된 가격이 없거나(None 이거나 False이면) 또는 정가만 있을 때 할인가격을 정가로 설정
            if self.info.sale_price is None:
                self.info.sale_price = self.info.price
                self.info.price = None


    def consider_shoppingmall(self, url):
        try:
            session = requests.Session()  # 세션을 시작합니다
            redirectUrl = session.head(url, allow_redirects=True, timeout=10).url
            
            
            response = requests.get(redirectUrl, headers=self.headers, verify=certifi.where(), allow_redirects=True, timeout=10)        
            content_type = response.headers['content-type']

            if not 'charset' in content_type:
                response.encoding = response.apparent_encoding
     
        except:
            return None
        if response.status_code == 200:  
            self.info.siteUrl = response.url
            if self.info.siteUrl.find('zigzag') != -1:
                self.extract_zigag_info(response)
            elif self.info.siteUrl.find('a-bly') != -1:
                self.extract_ably_info(response)
            elif self.info.siteUrl.find('wconcept') != -1:
                self.extract_wconcept_info(response)
            elif self.info.siteUrl.find('musinsa') != -1:
                self.extract_musinsa_info(response)
            elif self.info.siteUrl.find('29cm') != -1:
                self.extract_29cm_info(response)
            elif self.info.siteUrl.find('kream') != -1:
                self.extract_kream_info(response)
            # error 나는 오류 case들
            elif self.info.siteUrl.find('threetimes') != -1:
                self.extract_threetimes_info(response)
            else:
                self.extract_shoppingmall_info(response)
                
            return True
        else:
            print(f"Error : {url}")
            return None
         
         
         
    # extract information from shopping mall     
         
    ## static page
    def extract_zigag_info(self,response):
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
        
            # 이미지
            meta_tags = soup.find_all('meta', property="og:image")
            if meta_tags:
                for tag in meta_tags:
                    content = tag.get('content', None)
                    if content:
                        self.info.imageUrl = content
                        
            #사이트 이름
            self.info.siteName = '지그재그'
            
            #브랜드
            try:
                self.info.brand = soup.select_one("#__next > div.zds-themes.light-theme > div > div > div.pdp_shop_info_row > div > button > span").get_text()
            except:
                self.info.brand = None
            
            #로고 url
            self.info.logoUrl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAMAAAAJbSJIAAAAmVBMVEX5buMAAAD/cOjXYcOhSZTgY8z/cuxIH0D2atv5buL/cun7beP4buT/cOlNI0jaYMn/c+/tadibRo5uMmXKWbg6GzJdKla/VKwRBg2OQ4XmZs5YKFC4VKgiDR6GPnvybN5+OG0yFSutTp9UJkgABgAjCyCYR4oYDBwpFiphKVsxFzAYDBZvMGQ3GTh9N3AeDRobCw9CID3LWbU3fk36AAADr0lEQVR4nO2d21IbMRBEhbDXrHbXd7DBgDEJBMIlgf//uBR54CE41aI8KU07fb5gT0lujaTZdQhCCCGEEEIIIYQQQgghhBBCCCGEEEIIIYQQQgjxnxJNSaV1PjKZ9iyZrtvSRn/SP7Al7bthL5YW+oCx4aS0z0dsDWf+htDYcF5aZwumhsd1aZ0tmBpOHU5SW8OzprTOFiwNT7p9n6WLrrTNNgwNl1Vpma0YGp66HEJLwzN3Jelv7AxXPofQ0PDc42IYDA0v1qVV/oKZ4aXTSWpnOHI6Sc0Mh9FjxfaGlaHXnDEzXHrNGTPDK58V2xtGhiOvv0Irw02174bXbnPGytDhIeI7JoZXDq8r3ukfDwDDC2h46HiShlAhxlBwUNphN9ICGjq8rPgM1Rck+NVzzmSAo+jebz2TQ3cKDefR5wFNHvX6DgneVB7PgbPpcM7cet3c5xFPoOGEeY6GMIGCK+qcabtbaDj3XLFh6m9I8O6o9DPuRDOHQ3jLPYTVPTQclX7G3TiDgiuXl6LZpCk0XFDXM6H5jgQfqEcwRJwzbi8r8qgeoWGfegwbXM8MxqUfcicycsbvZUUW9RM05K5nEs6ZZ+qiO1QzaDiiTtJmDQWHNXWSdj1o6PmyIoN4jASX3IeIGfXMjHrfVGfUM74vKxDdZIkEN9xLRcQ5Q35ZEQfQkDxnDqHgjHq1D90zNJwH6s19DQVdvlmRT7yGhuSXFQnvm/qln3EnWpwzJ9SLYZ1wziyoK7aw/oEEL7hzpjuHQ3hKfgK1gobc9UwzgoLDMfUsTZfQkDxnWrhv+kk9gjlNXpfUQ1iP8b7JccdzBg1u8lolasOMJi/yQ8QW1jMP3IthxDnz7O/bHp+hw/WM2ze4ssjImSfqpSIk3ORFnjM1bL448PsGVwZtzqVox50zuJl0xH2IiJsvXko/4m50uPmiR52kbYLNpF4/m5BHTs48crflJ5wzr9STNOPlmA23YMQ5M+U2rF+g4aQ+Anj+mWbkTAaeL2wSbr4gN8T1DLlhws0X5Ibjmz03TPhSlNxwjJtJyQ1tcsaxoVHO+DVsM5q8uA3Tq5GgX0PcfMFt2FrljFfDNuEmL27DUOF9E7dhRjMpuWFGMym5IX45htww4SYvbsM2DffcMOImL3LDDjd5cRs2a/ytMm7DjC/ssBvCL3mxGxr/CYs/Q9uc8WgYbQX9GbbrQ1vc9aK0re1/knF3EwkhhBBCCCGEEEIIIYQQQgghhBBCCCGEEEIIIf4hvwBDyjkTw12CjgAAAABJRU5ErkJggg=="
            
            #상품명
            meta_tags = soup.find_all('meta', property="og:title")
            if meta_tags:
                for tag in meta_tags:
                    content = tag.get('content', None)
                    if content:
                        self.info.productName = content
                        
                        
            
            
            #가격 
            price_info_candidate = ["#__next > div.zds-themes.light-theme > div > div > div.css-nahvnd.e1ttpfby0 > div > div.css-oex5wl.e8ltq9r1 > span", "span.BODY_14.MEDIUM.css-1f02a3.e8ltq9r0"]
            for info_candidate in price_info_candidate: 
                try:         
                    self.info.price =  extract_price(soup.select_one(info_candidate).get_text())
                    break                
                except:
                    self.info.price = None
                
            try:
                self.info.sale_price = extract_price(soup.select_one("#__next > div.zds-themes.light-theme > div > div > div.css-nahvnd.e1ttpfby0 > div > div.HEAD_22.BOLD.css-1tthc24.emblu742 > span.css-l6qvuk.emblu740 > span").get_text())
            except:
                self.info.sale_price = None
            
            
        else:
            print(f'웹 페이지를 불러오는 데 문제가 발생했습니다.')


    def extract_wconcept_info(self, response):
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
        
            # 이미지
            meta_tags = soup.find_all('meta', property="og:image")
            if meta_tags:
                for tag in meta_tags:
                    content = tag.get('content', None)
                    if content:
                        self.info.imageUrl = content
                        
            #사이트 이름
            self.info.siteName = 'W컨셉'
            
            
            #브랜드
            try:
                self.info.brand = soup.select_one("h2.brand >a").text
            except:
                self.info.brand = None
            
            #로고 url
            self.info.logoUrl = "data:image/png;base64,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"
            
            #상품명
            try:
                self.info.productName = soup.select_one("h3.product.cottonusa").get_text()  
            except:
                self.info.productName =  None
                
            
                
            #가격
            price_info_candidate = ["dd.sale em", "dd.normal em"]
            for info_candidate in price_info_candidate: 
                try:         
                    self.info.price = extract_price(soup.select_one(info_candidate).get_text())
                    break                
                except:
                    self.info.price = None
                
            try:
                self.info.sale_price = extract_price(soup.select_one("dd.cupon em").get_text())
            except:
                self.info.sale_price = None
            
            
        else:
            print(f'웹 페이지를 불러오는 데 문제가 발생했습니다.')

    ## dynamic page
    def extract_ably_info(self, response):
        if response.status_code == 200:
            #static part
            soup = BeautifulSoup(response.text, 'html.parser')
    
            # 이미지
            meta_tags = soup.find_all('meta', property="og:image")
            if meta_tags:
                for tag in meta_tags:
                    content = tag.get('content', None)
                    if content:
                        self.info.imageUrl = content
            
            #site name
            self.info.siteName = "에이블리"
            
            ##dynamic part  
            options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(options=options)
            driver.get(self.info.siteUrl)
            time.sleep(2)
        
            #product
            try:
                self.info.productName =  driver.find_element(By.CSS_SELECTOR, "div > div.sc-49a6472c-0.cSkDBD > p").text
            except:
                self.info.productName = None
                

            #브랜드
            try:
                self.info.brand = driver.find_element(By.CSS_SELECTOR, "div > div.sc-bc435950-0.iqSBYF > div.sc-bc435950-1.lbXtVW > p.Typography__Tag-sc-lpjd4z-0.QRWYk.typography.typography__subtitle2.color__gray70").text
            except:
                self.info.brand = None
            
            #로고 url
            self.info.logoUrl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAL0AAAEKCAMAAABwsaR7AAAAdVBMVEX///8fHx8AAACdnZ0cHBzu7u4YGBje3t4UFBQEBAQaGhpmZmZiYmJISEgRERHn5+c0NDRVVVWWlpY9PT3BwcHIyMitra1BQUFSUlJMTEz39/fY2Nh/f39sbGzR0dExMTEqKiqSkpKzs7OGhoZ0dHSlpaUmJiargEW1AAAC80lEQVR4nO3X23qiMBSGYRK2oYJWbLXaWttq7/8SuxJ3SbD2BJ6Zg+89mFEW0B9YSTBJAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgIuPZdN0097mvHm82H/G1XLWNMvX/skWsr1ZXb6u5NtsMWzewFpXRaG/ettzu72onFbvossrdVGYhxune2nlbPPTl7ns1TaDR/Y8a6VUVq/j7bndrmqRyf+VCncopVrdSr+xh+njtU61HKo3o8Q+6WqbUj/H24/pl123fHeB5kH11/TJq1GqnbiPk1Ypc6O9hvPkQqpiGRds+vq49UkC1bug+nv6tbE3fHE6ddb2HuqQ3uT+2NbQ26jg0nfHz6+ykw6qv6d3rVi/y4ddfeuZDmlq78+skChvUcVPPzcqM0H1TvqkK1yjzWWXohs+sufD2Mc8qeTfPKz46We1qiZB9V76rW1GY9ut/0SHJV2TqWQhf8+Ew9Klz96fxaGzF/cUVO+lT/a2G237t/txUp982tgfSZLJRRRhyc05mRam7l/b3fR5m7mpIIuf58Ca4tgyroHCBfU4Y54UqzI88G76JD0eq9NRQp/ZpcUNVxu1eAlqQXoVr8b309uBIqNmNkbmK9ug5rDdbjerOl4Vr52jddVbrv5I71aRaKgMbe1ur7H5pINUGyyLbtR2U2v7WNkL8dedP9K72aAdKfZJGjRHNMj8GTOpz+vn2X+Q/lsyZWfxKAvSuwXh4FX/fXo7y2ffsxPpnWznVYP09mUiWPRLfWN59oyf3nazvsyEX23YHF7fl/ZlMRyEpVvLHiZn8bI0enp3+67rv33jqa6/inpzjizJ0cEqq87a+H1m9PTuxdG7n+5RXH9C5fGQDua/MqzW8Qv22OlzeQXQO2/DQhuj917dXMntD3+dln5V6vHCZOTkOhnPZp6maXA/U+vybT1Prw7xL+vcr9odonp4LgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOAHVmIdLTliqP8AAAAASUVORK5CYII="
                
            
            #price
            price_info_candidate = ["#root > div > div.sc-49a6472c-0.cSkDBD > div > div.sc-d8a0b042-0.eVmIiV > div > div > p.Typography__Tag-sc-lpjd4z-0.QRWYk.typography.typography__body1.color__gray30.sc-7dc5a431-0.hdOcgx", 
                                    "div > div.sc-49a6472c-0.cSkDBD > div > div.sc-d8a0b042-0.eVmIiV > div > div > p.Typography__Tag-sc-lpjd4z-0.QRWYk.typography.typography__body1.color__gray30.sc-7dc5a431-0.hdOcgx"]
            

            for info_candidate in price_info_candidate:                    
                try:
                    self.info.price = extract_price(driver.find_element(By.CSS_SELECTOR, info_candidate).text)
                    break
                except:
                    self.info.price = None
                
            #real price
            sale_price_info_candidate = [" #root > div > div.sc-49a6472c-0.cSkDBD > div > div.sc-d8a0b042-0.eVmIiV > div > div > p.Typography__Tag-sc-lpjd4z-0.QRWYk.typography.typography__h5.color__gray70",
                                         "#root > div > div.sc-49a6472c-0.cSkDBD > div > div.sc-d8a0b042-0.eVmIiV > div > div > p.Typography__Tag-sc-lpjd4z-0.Typography___StyledTag-sc-lpjd4z-1.QRWYk.AWxjJ.typography.typography__h5",
                                         "div > div.sc-49a6472c-0.cSkDBD > div > div.sc-d8a0b042-0.eVmIiV > div > div > p.Typography__Tag-sc-lpjd4z-0.QRWYk.typography.typography__h5.color__gray70"]
                                        
            for info_candidate in sale_price_info_candidate: 
                try:                    
                    self.info.sale_price = extract_price(driver.find_element(By.CSS_SELECTOR, info_candidate).text)
                    break
                except:
                    self.info.sale_price = None

                   
        else:
            print(f'웹 페이지를 불러오는 데 문제가 발생했습니다.')


    def extract_musinsa_info(self, response):
        if response.status_code == 200:
            #static part
            soup = BeautifulSoup(response.text, 'html.parser')
    
            # 이미지
            meta_tags = soup.find_all('meta', property="og:image")
            if meta_tags:
                for tag in meta_tags:
                    content = tag.get('content', None)
                    if content:
                        self.info.imageUrl = content
            
            #site name
            self.info.siteName = "무신사"
            

            
            
            
            ##dynamic part  
            options = webdriver.ChromeOptions()
        
            driver = webdriver.Chrome(options=options)
            driver.get(self.info.siteUrl)
            time.sleep(2)
            
                        

            #브랜드
            try:
                self.info.brand = driver.find_element(By.CSS_SELECTOR, "#root > div.sc-18j0po5-0.gpwaIb > div:nth-child(2) > dl:nth-child(1) > dd > a").text
            except:
                self.info.brand = None
            
            #로고 url
            self.info.logoUrl = "data:image/png;base64,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"
            
            
            product_info_candidate = ["#root > div.sc-1pxf5ii-0.ixVbGB > h2",

]

            for info_candidate in product_info_candidate:           
                try:
                    self.info.productName =  driver.find_element(By.CSS_SELECTOR, info_candidate).text
                    break
                except:
                    self.info.productName = None
                    

            price_info_candidate = ["#root > div.sc-f0xecg-0.glimmV > div > div.sc-f0xecg-4.jKJERj.gtm-catch-click > span",
                                    "#root > div.sc-f0xecg-0.glimmV > div > div > span",
]

            #price
            for info_candidate in price_info_candidate:
                try:
                    price_range = driver.find_element(By.CSS_SELECTOR, info_candidate).text          
                    self.info.price = extract_price(price_range.split("~")[-1].strip().replace("원", "").replace(",", ""))
                    break
                except:
                    self.info.price = None

            #sale price
            sale_price_info_candidate = ["#root > div.sc-f0xecg-0.glimmV > span",
                                         
]
            

            for info_candidate in sale_price_info_candidate:       
                try:                    
                    price_range = driver.find_element(By.CSS_SELECTOR, info_candidate).text          
                    self.info.sale_price = extract_price(price_range.split("~")[-1].strip().replace("원", "").replace(",", ""))
                    break
                except:
                    self.info.sale_price = None
                
           

                   
        else:
            print(f'웹 페이지를 불러오는 데 문제가 발생했습니다.')


    def extract_29cm_info(self, response):
        if response.status_code == 200:
            #static part
            soup = BeautifulSoup(response.text, 'html.parser')
    
            # 이미지
            meta_tags = soup.find_all('meta', property="og:image")
            if meta_tags:
                for tag in meta_tags:
                    content = tag.get('content', None)
                    if content:
                        self.info.imageUrl = content
            
            #site name
            self.info.siteName = "29cm"
            
            ##dynamic part  
            options = webdriver.ChromeOptions()
        
            driver = webdriver.Chrome(options=options)
            driver.get(self.info.siteUrl)
            time.sleep(2)
            
            #브랜드
            try:
                self.info.brand = driver.find_element(By.CSS_SELECTOR, "#__next > div.css-uio8sw.e1uo4o521 > div.css-1ux6qe5.e1uo4o525 > div > a > div > h3").text
            except:
                self.info.brand = None
            
            #로고 url
            self.info.logoUrl = "data:image/jpeg;base64,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"
            
            #product
            try:
                self.info.productName =  driver.find_element(By.ID, "pdp_product_name").text
            except:
                self.info.productName =  None
                
                
            #price 
            price_info_candidate = ["#__next > div.css-uio8sw.e1uo4o521 > div.css-1y47rmj.e18uevlq0 > div.css-3eeht.e18uevlq1 > div.css-uz7uc7.ek83fdm0 > div > div.css-lcoy4n.ek83fdm7 > div > p.css-1bci2fm.ejuizc31",
                                  "#__next > div.css-uio8sw.efamvvy1 > div.css-1y47rmj.e1muz2ce0 > div.css-3eeht.e1muz2ce1 > div.css-uz7uc7.e1k8yytz0 > div > div.css-lcoy4n.e1k8yytz7 > div > p.css-1bci2fm.e6x3p711"]
          
            for info_candidate in price_info_candidate:
                try:
                    self.info.price =  extract_price(driver.find_element(By.CSS_SELECTOR, info_candidate).text)
                    break
                except:
                    self.info.price = None
                
            #real price
            try:                    
                self.info.sale_price = extract_price(driver.find_element(By.CSS_SELECTOR, "#pdp_product_price").text)
            except:
                self.info.sale_price = None

                   
        else:
            print(f'웹 페이지를 불러오는 데 문제가 발생했습니다.')

    def extract_kream_info(self, response):
        if response.status_code == 200:
            #static part
            soup = BeautifulSoup(response.text, 'html.parser')
    
            # 이미지
            meta_tags = soup.find_all('meta', property="og:image")
            if meta_tags:
                for tag in meta_tags:
                    content = tag.get('content', None)
                    if content:
                        self.info.imageUrl = content
            
            #site name
            self.info.siteName = "kream"
            
            ##dynamic part  
            options = webdriver.ChromeOptions()
        
            driver = webdriver.Chrome(options=options)
            driver.get(self.info.siteUrl)
            time.sleep(2)
            
            #브랜드
            try:
                self.info.brand = driver.find_element(By.CSS_SELECTOR, "#wrap > div.layout__main--without-search.container.detail.lg > div.content > div.column_bind > div:nth-child(2) > div > div.product-branding-feed-container > div > div.left-container > div.title-wrap > div.title > p").text
            except:
                self.info.brand = None
            
            #로고 url
            self.info.logoUrl = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQcqK334S50ShFVvamwjbft_QF3_8hm-vqGU3etVrBf7w&s"
            
            
            
            
            #product
            
            product_info_candidate = ["#wrap > div.layout__main--without-search.container.detail.lg > div.content.brand > div.column_bind > div:nth-child(2) > div > div.column_top > div.main-title-container > p.title",
                                      "#wrap > div.layout__main--without-search.container.detail.lg > div.content > div.column_bind > div:nth-child(2) > div > div.column_top > div.main-title-container > p.title"]
            

            for info_candidate in product_info_candidate:           
                try:
                    self.info.productName =  driver.find_element(By.CSS_SELECTOR, info_candidate).text
                    break
                except:
                    self.info.productName = None

            #kream은 할인 전 가격 없는 걸로 가정
            self.info.price = None
                
            #real price
            try:                    
                self.info.sale_price = extract_price(driver.find_element(By.CSS_SELECTOR, "#wrap > div.layout__main--without-search.container.detail.lg > div.content > div.column_bind > div:nth-child(2) > div > div.column_top > div.product_info_wrap > div > dl > div:nth-child(2) > div.product_info").text)
            except:
                self.info.sale_price = None

                   
        else:
            print(f'웹 페이지를 불러오는 데 문제가 발생했습니다.')

    def extract_threetimes_info(self, response):
        if response.status_code == 200:
            #static part
            soup = BeautifulSoup(response.text, 'html.parser')
    
            # 이미지
            meta_tags = soup.find_all('meta', property="og:image")
            if meta_tags:
                for tag in meta_tags:
                    content = tag.get('content', None)
                    if content:
                        self.info.imageUrl = content
            
            #site name
            self.info.siteName = "threetimes"
            self.info.brand = "threetimes"
            
            ##dynamic part  
            options = webdriver.ChromeOptions()
        
            driver = webdriver.Chrome(options=options)
            driver.get(self.info.siteUrl)
            time.sleep(2)
            
            body_text = driver.find_element(By.TAG_NAME, "body").text
            if body_text == '':
                time.sleep(5)
                body_text = driver.find_element(By.TAG_NAME, "body").text
            
            #product
            product_info_candidate = ["#contents > div.xans-element-.xans-product.xans-product-detail.product_detail > div > div.infoArea > div.headingArea > h2",
                                      "#contents > div:nth-child(1) > div.headingArea > h1"]
            
            for info_candidate in product_info_candidate:           
                try:
                    self.info.productName =  driver.find_element(By.CSS_SELECTOR, info_candidate).text
                    break
                except:
                    self.info.productName = None
            #price
            try:
                self.info.price =  extract_price(driver.find_element(By.CSS_SELECTOR, "#span_product_price_text").text)
            except:
                self.info.price = None
                
            #sale price
            self.info.sale_price = None

                   
        else:
            print(f'웹 페이지를 불러오는 데 문제가 발생했습니다.')



    ## extra page   
    def extract_shoppingmall_info(self, response):
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            all_text = soup.get_text()
            cleaned_text = [line.strip() for line in all_text.split('\n') if line.strip()]
            properties = ['og:url', 'og:site_name', 'og:title', 'og:image', 'product:price:amount']

            # Dictionary
            found_properties = {prop: [] for prop in properties}

            for prop in properties:
                meta_tags = soup.find_all('meta', property=prop)
                if meta_tags:
                    for tag in meta_tags:
                        content = tag.get('content', None)
                        if content:
                            found_properties[prop].append(content)

            #site
            for site in found_properties['og:site_name']:
                if self.info.siteName == None:
                    self.info.siteName = site
                ##제일 짧은 애 선정
                if len(self.info.siteName) > len(site):
                    self.info.siteName = site
            ## 없으면 그냥 사이트 주소
            if self.info.siteName == None:
                self.info.siteName = extract_shoppingmall_name(self.info.siteUrl)
                
            self.info.brand = self.info.siteName
               
            
            #image
            for image in found_properties['og:image']:
                if not self.info.imageUrl:
                    self.info.imageUrl = image
                
                elif len(self.info.imageUrl) < len(image):
                    self.info.imageUrl = image


            ##price candidate
            price_line = ''
            #if price amount exist
            #cleaned text에서 처음으로 나온 애 line 저장 및 price 저장
            
            if found_properties['product:price:amount']:
                self.info.price = extract_price(found_properties['product:price:amount'][0])
            
                for idx, line in enumerate(cleaned_text):
                    if extract_price(line) == self.info.price:
                        price_line = line
                        break
        
                    
            ##없으면
            ##cleaned text에서 0인 애 뽑는데 특정표시 있으면 당첨
            else:
                price_candidate = None
                line_candidate = None
                for idx, line in enumerate(cleaned_text):
                    extract_line_price = extract_price(line)
                    
                    if extract_line_price == None:
                        continue
                    
                    if price_candidate == None:
                        price_candidate = extract_line_price
                        line_candidate = line
                    if is_currency(line):
                        self.info.price = extract_line_price
                        price_line = line
                        break
                #None이면 그냥 candidate로 
                if not self.info.price:
                    self.info.price = price_candidate
                    price_line = line_candidate
                            

            ##title candidate
            title_candidate = []
            
            for idx, line in enumerate(cleaned_text):
                if line == price_line:
                    for i in range(idx):
                        title_candidate.append(cleaned_text[idx-(i+1)])
                    break
                    ## para에 있으면 굿 없으면 제일 긴 거
                    
            def find_product_title(candidiate: List[str]):               
                for line in candidiate:
                    if len(line) > 50:
                        continue
                    
                    if self.info.productName == None:
                        self.info.productName = line
                    
                    if len(line) > len(self.info.productName):
                        self.info.productName = line
                    for title in found_properties['og:title']:
                        if check_common_substring(line, title):
                            self.info.productName = line                
                            return

                # print_result()       

            find_product_title(title_candidate)
            if self.valid_product() == False:
                self.extract_dynamic_shoppingmall_info(response)


    def extract_dynamic_shoppingmall_info(self, response):
        if response.status_code == 200:          
            ##dynamic part  
            options = webdriver.ChromeOptions()
        
            driver = webdriver.Chrome(options=options)
            driver.get(self.info.siteUrl)
            
            #존재하지 않는 주소입니다 alert뜰 때
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
            except:
                return
            if body_text == '':
                time.sleep(5)
                body_text = driver.find_element(By.TAG_NAME, "body").text
            
            cleaned_text = [line.strip() for line in body_text.split('\n') if line.strip()]
            properties = ['og:url', 'og:site_name', 'og:title', 'og:image', 'product:price:amount']

            # Dictionary
            found_properties = {prop: [] for prop in properties}


            for prop in properties:
                try:
                    # 해당 property를 가진 meta 태그 찾기
                    tag = driver.find_element(By.XPATH, f"//meta[@property='{prop}']")
                    
                    # 해당 태그의 content 속성 값 출력
                    content = tag.get_attribute('content')
                    found_properties[prop].append(content)
                except Exception as e:
                    continue


            #site
            for site in found_properties['og:site_name']:
                if self.info.siteName == None:
                    self.info.siteName = site
                ##제일 짧은 애 선정
                if len(self.info.siteName) >= len(site):
                    self.info.siteName = site
            ## 없으면 그냥 사이트 주소
            if self.info.siteName == None:
                self.info.siteName = extract_shoppingmall_name(self.info.siteUrl)
                
            self.info.brand = self.info.siteName
            
            #image
            for image in found_properties['og:image']:
                if not self.info.imageUrl:
                    self.info.imageUrl = image
                
                elif len(self.info.imageUrl) < len(image):
                    self.info.imageUrl = image


            ##price candidate
            price_line = ''
            #if price amount exist
            #cleaned text에서 처음으로 나온 애 line 저장 및 price 저장
            

            if found_properties['product:price:amount']:
                self.info.price = extract_price(found_properties['product:price:amount'][0])
            
                for idx, line in enumerate(cleaned_text):
                    if extract_price(line) == self.info.price:
                        price_line = line
                        break
                        
            
                    
            ##없으면
            ##cleaned text에서 0인 애 뽑는데 특정표시 있으면 당첨
            else:
                price_candidate = None
                line_candidate = None
                for idx, line in enumerate(cleaned_text):
                    extract_line_price = extract_price(line)
                    
                    if extract_line_price == None:
                        continue
                    
                    if price_candidate == None:
                        price_candidate = extract_line_price
                        line_candidate = line
                    if is_currency(line):
                        self.info.price = extract_line_price
                        price_line = line
                        break
                #None이면 그냥 candidate로 
                if not self.info.price:
                    self.info.price = price_candidate
                    price_line = line_candidate
                            

            ##title candidate
            title_candidate = []
            
            for idx, line in enumerate(cleaned_text):
                if line == price_line:
                    ## 위에 모든 줄 확인
                    for i in range(idx):
                        title_candidate.append(cleaned_text[idx-(i+1)])
                    break
                    ## para에 있으면 굿 없으면 제일 긴 거
                    
                        
            def find_product_title(candidiate: List[str]):               
                for line in candidiate:
                    if len(line) > 50:
                        continue
                    ##가격이나 사이트 이름??인 경우는 continue
                    if extract_price(line):
                        continue
                    
                    
                    
                    if self.info.productName == None:
                        self.info.productName = line
                    
                    if len(line) > len(self.info.productName):
                        self.info.productName = line
                    for title in found_properties['og:title']:

                        
                        if check_common_substring(line, title):
                            self.info.productName = line                
                            return

                # print_result()       

            find_product_title(title_candidate)

    def lazy_extract_dynamic_shoppingmall_info(self):
        response = requests.get(self.info.siteUrl, headers=self.headers)

        if response.status_code == 200:          
            ##dynamic part  
            options = webdriver.ChromeOptions()
        
            driver = webdriver.Chrome(options=options)
            driver.get(self.info.siteUrl)
          
            time.sleep(3)
            
            #존재하지 않는 주소입니다 alert뜰 때
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text
            except:
                return
          
            
            cleaned_text = [line.strip() for line in body_text.split('\n') if line.strip()]
            properties = ['og:url', 'og:site_name', 'og:title', 'og:image', 'product:price:amount']

            # Dictionary
            found_properties = {prop: [] for prop in properties}


            for prop in properties:
                try:
                    # 해당 property를 가진 meta 태그 찾기
                    tag = driver.find_element(By.XPATH, f"//meta[@property='{prop}']")
                    
                    # 해당 태그의 content 속성 값 출력
                    content = tag.get_attribute('content')
                    found_properties[prop].append(content)
                except Exception as e:
                    continue


            #site
            for site in found_properties['og:site_name']:
                if self.info.siteName == None:
                    self.info.siteName = site
                ##제일 짧은 애 선정
                if len(self.info.siteName) >= len(site):
                    self.info.siteName = site
            ## 없으면 그냥 사이트 주소
            if self.info.siteName == None:
                self.info.siteName = extract_shoppingmall_name(self.info.siteUrl)
                
            #brand
            self.info.brand = self.info.siteName
            
            #image
            for image in found_properties['og:image']:
                if len(self.info.siteName) < len(image):
                    self.info.imageUrl = image


            ##price candidate
            price_line = ''
            #if price amount exist
            #cleaned text에서 처음으로 나온 애 line 저장 및 price 저장
            
            if found_properties['product:price:amount']:
                self.info.price = extract_price(found_properties['product:price:amount'][0])
            
                for idx, line in enumerate(cleaned_text):
                    if extract_price(line) == self.info.price:
                        price_line = line
                        break
                        
            
                    
            ##없으면
            ##cleaned text에서 0인 애 뽑는데 특정표시 있으면 당첨
            else:
                price_candidate = None
                line_candidate = None
                for idx, line in enumerate(cleaned_text):
                    extract_line_price = extract_price(line)
                    
                    if extract_line_price == None:
                        continue
                    
                    if price_candidate == None:
                        price_candidate = extract_line_price
                        line_candidate = line
                    if is_currency(line):
                        self.info.price = extract_line_price
                        price_line = line
                        break
                #None이면 그냥 candidate로 
                if not self.info.price:
                    self.info.price = price_candidate
                    price_line = line_candidate
                            

            ##title candidate
            title_candidate = []
            
            for idx, line in enumerate(cleaned_text):
                if line == price_line:
                    ## 위에 모든 줄 확인
                    for i in range(idx):
                        title_candidate.append(cleaned_text[idx-(i+1)])
                    break
                    ## para에 있으면 굿 없으면 제일 긴 거
                    
            def find_product_title(candidiate: List[str]):               
                for line in candidiate:
                    if len(line) > 50:
                        continue
                    
                    if self.info.productName == None:
                        self.info.productName = line
                    
                    if len(line) > len(self.info.productName):
                        self.info.productName = line
                    for title in found_properties['og:title']:
                        if check_common_substring(line, title):
                            self.info.productName = line                
                            return

                # print_result()       

            find_product_title(title_candidate)

    
    def valid_product(self):
        if self.info.productName == None:
            return False
        if self.info.siteUrl == None:
            return False
        if self.info.imageUrl == None:
            return False
        if self.info.price == None and self.info.sale_price == None:
            return False
        
        return True
    
    def getter_result(self):
        return self.info

class Product: 
    def __init__(self, url):
        extractor = ShoppingMallInfoExtractor(url)
        self.productInformation = extractor.getter_result()
        self.valid = extractor.valid_product()
        
        
    def print_result(self):
        info = self.productInformation
        if self.valid:
            print(f"site: {info.siteName} product: {info.productName} brand: {info.brand} price: {info.price} sale_price: {info.sale_price} category: {info.category} url: {info.siteUrl}")
        else:
            print(f"Error in {info.siteName}")
            
    def return_info(self):
        info = self.productInformation
        if self.valid:
            return info.decompose_info()
        else:
            print(f"Error in {info.siteName}")
            return None
    
    def categorize_product(self):
        try:
            self.productInformation.category, self.productInformation.color = categorize_image(self.productInformation.imageUrl, self.productInformation.productName)
        except:
            self.productInformation.category, self.productInformation.color = "ERROR", "ERROR"
    
    def save_product_info(self):
        if not self.valid:
            return
        self.categorize_product()
        productName, brand,imageUrl, sale_price, price, category, color,siteName, siteUrl, logoUrl, haveRelatedProduct = self.productInformation.decompose_info()

        productNo = encode_to_base62(productName)
        s3location = imageUrl
        if download_image_by_url(imageUrl, productNo):
            s3location = f"product/{productNo}.webp"
            save_file_to_s3( f"{productNo}.webp", s3location, True)
            delete_local_file(f"{productNo}.webp", is_img=True)

        data = [productName, productNo, brand, s3location, sale_price, price, category, color,siteName, siteUrl, logoUrl]
        return data
        #save_product_data_to_sheet(data)
        

# musinsa = "https://www.musinsa.com/app/goods/3800080?loc=goods_rank"
# zigzag = "https://zigzag.kr/catalog/products/111606898"
# wconcept = "https://www.wconcept.co.kr/Product/305692911"
# ably = "https://m.a-bly.com/goods/10669116"
# twentynine = "https://product.29cm.co.kr/catalog/2416498"
# threetimes = "https://threetimes.kr/product/1st-pre-order-tht-pendant-tee/4747/category/1/display/3/"
# staticsite = "https://m.loulouseoul.com/product/made-dory-maxi-dress/3121/category/42/display/1/"
# dynamicsite = "https://angelie.co.kr/product/puppy-bag-large-ivory/259/category/101/display/1/"
#kream = "https://kream.co.kr/products/106894"

# url="https://www.adidas.co.kr/%EC%98%A4%EB%A6%AC%EC%A7%80%EB%84%90%EC%8A%A4-%EC%82%BC%EB%B0%94/ID2047.html"

# product= Product(url)
# product.save_product_info()