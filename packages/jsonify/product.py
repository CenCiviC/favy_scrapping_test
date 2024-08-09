#json
from typing import Tuple, Optional, List

def json_product_info(product_info, rank: Optional[int] = None):
    productName, productNo,brand, s3location, sale_price, price, category, color,siteName, siteUrl, logoUrl = product_info
    
    data = {
        "brand": brand,
        "category": category,
        "color": color,
        "productImg": s3location,
        "productName": productName,
        "productNo": productNo,
        "season": "fa",
        "status": "b",

        "price": sale_price,
        "regularPrice": price,
        "salesImg": logoUrl,
        "salesName": siteName,
        "salesUrl": siteUrl,
    }
    
    if rank is not None:
        data["similarityRank"] = rank
    
    return data


def json_related_product_info(related_product_list):
    data = {
        "relatedProductList": related_product_list
    }
    
    return data


def json_sales(product_info):
    productName, productNo,brand, s3location, sale_price, price, category, color,siteName, siteUrl, logoUrl = product_info
    data = {
        "salesName": siteName,
        "salesUrl": siteUrl,
        "salesImg": logoUrl,
        "price": sale_price,
        "regularPrice": price
    }
    
    return data