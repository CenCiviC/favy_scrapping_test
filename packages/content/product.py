from utils.string import encode_to_base62
from utils.files import delete_local_file
from utils.files  import download_image_by_url

from api.gpt import categorize_image
from api.aws import save_file_to_s3

from scraper.mall import ShoppingMallInfoExtractor

from dotenv import load_dotenv
import os 

load_dotenv()
S3_CDN_DOMAIN = os.environ.get('S3_CDN_DOMAIN')

class Product: 
    def __init__(self, url):
        extractor = ShoppingMallInfoExtractor(url)
        self.productInformation = extractor.getter_result()
        self.valid = extractor.valid_product()
        
        if self.valid:
            self.categorize_product()
        
        
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

        data = [productName, productNo, brand, S3_CDN_DOMAIN+ s3location, sale_price, price, category, color,siteName, siteUrl, logoUrl]
        return data
        #save_product_data_to_sheet(data)