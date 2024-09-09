#service
from typing import Tuple, Optional, List
from packages.jsonify.product import *
from packages.api.googleapi import search_related_product, search_same_product
from packages.content.product import Product

def service_product_info(url:str):
    product = Product(url)
    if not product.valid:
        return None
    
    product_info  = product.save_product_info()
    return json_product_info(product_info)



def service_related_product_info(product_image_url: str, product_name:str):
    #연관 상품들 링크 가져오기
    _, realted_product_links = search_related_product(product_image_url)
    
    related_product_list = []
    rank = 1
    
    #그 링크들 확인하면서 list에 하나씩 추가
    for link in realted_product_links:
        #상품 유효성 확인
        product= Product(link)
        if not product.valid:
            continue
        
        if product.productInformation.productName == product_name:
            continue
        
        product_info = product.save_product_info()
        #productName, productNo,brand, s3location, sale_price, price, category, color,siteName, siteUrl, logoUrl = product.save_product_info()
        
        product_info = json_product_info(product_info, rank)
        related_product_list.append(product_info)
        rank+=1
    
    data = json_related_product_info(related_product_list)
    
    return data 

def service_sales(product_image_url):
    #page token을 했을 때 image_sources가 있는지 없는지로 확인함
    page_token, _ = search_related_product(product_image_url)
    same_product_links = search_same_product(page_token)
    
    same_product_list = []

    for link in same_product_links:
        product= Product(link)
        if not product.valid:
            continue
        product_info = product.save_product_info()
        sales_data = json_sales(product_info)
    
        same_product_list.append(sales_data)
        
    data = {
        "salesList": same_product_list
    }
    
    return data