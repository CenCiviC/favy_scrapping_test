from google.cloud import vision
from dotenv import load_dotenv
import cv2
import os

from utils.files import download_image_by_url, public_img_abspath, delete_local_file
from api.aws import save_file_to_s3

load_dotenv()
S3_CDN_DOMAIN = os.environ.get('S3_CDN_DOMAIN')


#이름 + bounding box list의 list로 구성
def localize_objects_uri(uri):
    """Localize objects in the image on Google Cloud Storage and return bounding boxes for clothing items.

    Args:
    uri: The path to the file in Google Cloud Storage
    Returns:
    List of bounding boxes for clothing items.
    """

    client = vision.ImageAnnotatorClient()

    image = vision.Image()
    image.source.image_uri = uri

    objects = client.object_localization(image=image).localized_object_annotations

    # 의류 관련 객체만 필터링 및 대분류 설정ㅈ
    category_map = {
        "Outerwear": ["Outerwear", "Jacket", "Coat"],
        "Top": ["Top","Shirt", "Dress", "T-Shirt", "Blouse"],
        "Pants": ["Pants", "Bottom", "Jeans", "Shorts"],
        "Skirt" : ["Skirt", "Miniskirt"],
        "Shoes": ["Footwear", "Shoe","Shoes", "Boot", "Sandal", "High heels"],
        "Bag": ["Bag","Handbag"]
    }

    # 대분류별로 탐지된 객체를 기록
    detected_categories = set()
    bounding_boxes = []

    for object_ in objects:
        for category, labels in category_map.items():
            if object_.name in labels and category not in detected_categories:
                # 대분류에서 첫 번째 객체를 발견하면 추가
                vertices = [(vertex.x, vertex.y) for vertex in object_.bounding_poly.normalized_vertices]
                bounding_boxes.append((object_.name, vertices))
                detected_categories.add(category)
                break  # 대분류 중 하나만 추가되도록 브레이크

    return bounding_boxes


#mediaID_분류이름.webp
#crop하기 위해서는 자체로 다운 받아야됨


def crop_image_by_bounding_boxes(path, file_name, bounding_box):
    """Crop the image based on bounding boxes.

    Args:
    image_url: The path to the image to be cropped.
    bounding_boxes: List of bounding boxes to crop the image.
    """
    #image controller    

    
    image = cv2.imread(path)
    height, width, _ = image.shape


    # Convert normalized coordinates to absolute coordinates
    x1 = int(bounding_box[0][0] * width)
    y1 = int(bounding_box[0][1] * height)
    x2 = int(bounding_box[2][0] * width)
    y2 = int(bounding_box[2][1] * height)

    # Crop the image
    cropped_image = image[y1:y2, x1:x2]
    cropped_image_path = public_img_abspath(file_name)
    cv2.imwrite(cropped_image_path, cropped_image)
    save_file_to_s3(file_name, f"trash/{file_name}", True)
    delete_local_file(file_name, True)

    return f"{S3_CDN_DOMAIN}trash/{file_name}"

def crop_images_by_instagram_url(media_id, uri):
    bounding_boxes = localize_objects_uri(uri)
    urls = []
    
    path = download_image_by_url(uri, media_id + "_origin")
    if path is None:
        return None
    for classified_name, bounding_box in bounding_boxes:
        url = crop_image_by_bounding_boxes(path,media_id +"_" +classified_name+".webp", bounding_box)
        urls.append(url)
        
    delete_local_file(media_id +"_origin.webp", True)
        
    return urls