# from scraper.instagram import InstagramExtractor


# url = "https://www.instagram.com/p/C72-1KXJmFJ/?img_index=1"

# extractor = InstagramExtractor(url)
# if extractor.valid():
#     print(extractor.save_instagram_img())



# 상품 테스트
# from content.product import Product

# musinsa = "https://www.musinsa.com/app/goods/3800080?loc=goods_rank"
# zigzag = "https://zigzag.kr/catalog/products/111606898"
# wconcept = "https://www.wconcept.co.kr/Product/305692911"
# ably = "https://m.a-bly.com/goods/10669116"
# twentynine = "https://product.29cm.co.kr/catalog/2416498"
# threetimes = "https://threetimes.kr/product/1st-pre-order-tht-pendant-tee/4747/category/1/display/3/"
# staticsite = "https://m.loulouseoul.com/product/made-dory-maxi-dress/3121/category/42/display/1/"
# dynamicsite = "https://angelie.co.kr/product/puppy-bag-large-ivory/259/category/101/display/1/"
# kream = "https://kream.co.kr/products/106894"

# url="https://www.musinsa.com/app/goods/4240688"

# product= Product(url)
# product.print_result()
# product.save_product_info()


##### 코디 -> 상품찾기
# 1. 사진을 좌표로 자르기
# from google.cloud import vision
# import cv2
# from utils.files import download_image_by_url, public_img_abspath
# from api.aws import save_file_to_s3
# from api.googleapi import search_related_product

# def localize_objects_uri(uri):
#     """Localize objects in the image on Google Cloud Storage and return bounding boxes for clothing items.

#     Args:
#     uri: The path to the file in Google Cloud Storage
#     Returns:
#     List of bounding boxes for clothing items.
#     """
#     client = vision.ImageAnnotatorClient()

#     image = vision.Image()
#     image.source.image_uri = uri

#     objects = client.object_localization(image=image).localized_object_annotations

#     # 의류 관련 객체만 필터링
#     clothing_labels = ["Shirt", "Pants", "Dress", "Skirt", "Jeans", "T-Shirt", "Blouse", "Jacket", "Coat", "Shoe", "Footwear", "Outerwear", "Handbag", "Boot"]
#     clothing_objects = [obj for obj in objects if obj.name in clothing_labels]

#     bounding_boxes = []
#     for object_ in objects:
#         vertices = [(vertex.x, vertex.y) for vertex in object_.bounding_poly.normalized_vertices]
#         bounding_boxes.append((object_.name, vertices))
    
#     return bounding_boxes

# def crop_image_by_bounding_boxes(image_path, file_name, bounding_box):
#     """Crop the image based on bounding boxes.

#     Args:
#     image_path: The path to the image to be cropped.
#     bounding_boxes: List of bounding boxes to crop the image.
#     """
    
#     image = cv2.imread(image_path)
#     height, width, _ = image.shape


#     # Convert normalized coordinates to absolute coordinates
#     x1 = int(bounding_box[0][0] * width)
#     y1 = int(bounding_box[0][1] * height)
#     x2 = int(bounding_box[2][0] * width)
#     y2 = int(bounding_box[2][1] * height)

#     # Crop the image
#     cropped_image = image[y1:y2, x1:x2]
#     cropped_image_path = public_img_abspath(file_name)
#     cv2.imwrite(cropped_image_path, cropped_image)
#     save_file_to_s3(file_name, f"trash/{file_name}", True)
#     return f"https://d1wa6tg9pd3mhn.cloudfront.net/trash/{file_name}"

# # Example usage

# #https://d1wa6tg9pd3mhn.cloudfront.net/2u7V3iabdXInLmAQRZ/C9W8ewHJvIW.webp
# # Assuming the image has been downloaded locally using your existing logic
# #url 받기

# p_name = "C9CcUmYPK5D"
# url = "https://d1wa6tg9pd3mhn.cloudfront.net/" + f"2Fq6y29pqe/C9CcUmYPK5D.webp"

# #url로 이름, 박스로 추출
# bounding_boxes = localize_objects_uri(url)


# download_image_by_url(url, p_name)
# for classified_name, bounding_box in bounding_boxes:
#     file_name = f"{p_name}_{classified_name}"
#     image_path = public_img_abspath(p_name+".webp")
#     url = crop_image_by_bounding_boxes(image_path,file_name+".webp", bounding_box)
    
#     #여기서 이미지 검색 후 urls 등록
#     page_token, similiar_product_urls = search_related_product(url)
#     print(similiar_product_urls)
from service.product import service_sales

url = "https://d1wa6tg9pd3mhn.cloudfront.net/product/1WrbkTpV7EyUgMCU0.webp"
name = "밀레니오"

service_sales(url)