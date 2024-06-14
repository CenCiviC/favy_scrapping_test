import os
        
def public_img_abspath(img_location: str):
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..','public', 'img', img_location)
    return img_path

def public_video_abspath(video_location: str):
    img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..','public', 'img', video_location)
    return img_path