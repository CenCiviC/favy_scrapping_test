def download_product_img_by_local(productName:str):
    convert_image_to_webp(f"img/{productName}.png", f"img/{productName}.webp")
    imgLocation = encodeByBase62(productName)
    s3location = f"product/{imgLocation}.webp"
    save_file_to_s3( f"{productName}.webp", s3location, True)
    deleteLocalFile(f"img/{productName}.png")
    deleteLocalFile(f"img/{productName}.webp")
    return s3location

def download_product_img_by_url(productName:str, url):
    imgLocation = encodeByBase62(productName)
    if download_image_by_url(url, imgLocation):
        s3location = f"product/{imgLocation}.webp"
        save_file_to_s3( f"{imgLocation}.webp", s3location, True)
        deleteLocalFile(f"img/{imgLocation}.webp")
        return s3location

