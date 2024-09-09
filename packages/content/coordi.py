from enum import Enum
from typing import List
from .product import Product
from packages.api.googleapi import search_product_link


class CaptionInfo(Enum):
    BRAND = 0
    PRODUCT = 1
    URL = 2


class Coordi:
    #start, end time 받기
    def __init__(self, cody_id: str, imgUrl, filmUrl,products: List[List[str]], timeline: str) -> None:
        self.cody_id = cody_id
        self.filmImg = imgUrl
        self.filmUrl = filmUrl
        self.products: List[Product]  = []
        self.timeline =  timeline
        self.addProducts(products)
        
    def addProducts(self, products: List[List[str]]):
        for productInfoList in products: 
            productUrl = productInfoList[CaptionInfo.URL.value]
            productName = productInfoList[CaptionInfo.PRODUCT.value]
            brandName = productInfoList[CaptionInfo.BRAND.value]
                
            #du
            tempProduct = Product(productUrl)
            
        
            #링크가 제대로 있으면
            if tempProduct.valid:
                newProduct = tempProduct
                self.products.append(newProduct)
            else:
                newProduct = Product(search_product_link(brandName, productName))
                if not newProduct.valid:
                    continue
                self.products.append(newProduct)
                
            #newProduct.save_product_info()
            
        