# from scraper.instagram import InstagramExtractor


# url = "https://www.instagram.com/p/C72-1KXJmFJ/?img_index=1"

# extractor = InstagramExtractor(url)
# if extractor.valid():
#     print(extractor.save_instagram_img())



#######################상품 테스트
# from content.product import Product

# musinsa = "https://www.musinsa.com/app/goods/3800080?loc=goods_rank"
# zigzag = "https://zigzag.kr/catalog/products/141989576"
# wconcept = "https://www.wconcept.co.kr/Product/305692911"
# ably = "https://m.a-bly.com/goods/10669116"
# twentynine = "https://product.29cm.co.kr/catalog/2416498"
# threetimes = "https://threetimes.kr/product/1st-pre-order-tht-pendant-tee/4747/category/1/display/3/"
# staticsite = "https://m.loulouseoul.com/product/made-dory-maxi-dress/3121/category/42/display/1/"
# dynamicsite = "https://angelie.co.kr/product/puppy-bag-large-ivory/259/category/101/display/1/"
# kream = "https://kream.co.kr/products/106894"

# url="https://www.musinsa.com/mz/magazine/view/61484"

# product= Product(url)
# product.print_result()

##############cody test

# from service import service_instagrm_shot_info
# import math
# import time

# start = time.time()

# # #### 코디 -> 상품찾기
# instagram_url = "https://www.instagram.com/p/C1ElVaOSltb/"
# ig_shot_info_json = service_instagrm_shot_info(instagram_url)

# end = time.time()

# print("###################################")
# print(ig_shot_info_json)
# print(f"{end - start:.5f} sec")

#######################sales
# from service.product import service_sales

# url = "https://d1wa6tg9pd3mhn.cloudfront.net/product/1WrbkTpV7EyUgMCU0.webp"
# name = "밀레니오"

# service_sales(url)

# from scraper.insta import InstagramExtractor

# url = "https://www.instagram.com/p/C7wB9lGRPtI/?img_index=1"

# InstagramExtractor(url).save_instagram_img()
# print("hel")