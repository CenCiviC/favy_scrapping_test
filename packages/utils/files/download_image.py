import requests
import certifi
from PIL import Image
from io import BytesIO
import urllib.request
from .file_path import public_img_abspath


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



def download_image_by_url(imgUrl:str, imgName: str) -> bool:
    try:
        # 이미지 다운로드
        response = requests.get(imgUrl, headers=headers, verify=certifi.where())  
        img = Image.open(BytesIO(response.content))

        # 이미지를 webp 형식으로 변환 및 저장
        img_path = public_img_abspath(imgName + ".webp")
        img.save(img_path, "WEBP")
        print(f"Image {imgName} saved as webp format.")
        return True
    except Exception as e:
        print(f"Error downloading or converting image {imgUrl}: {e}")
        return False
    
    
def convert_image_to_webp(input_path, img_name):
    # 이미지를 열고
    img = Image.open(input_path)
    # WEBP 형식으로 저장
    output_path = public_img_abspath(img_name + ".webp")
    img.save(output_path, 'WEBP')