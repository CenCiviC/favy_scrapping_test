import os
from .file_path import public_img_abspath
from .file_path import public_video_abspath

def delete_local_file(file_name:str, is_img: bool):
    file_path = ""
    if is_img:
        file_path = public_img_abspath(file_name)
    else:
        file_path = public_video_abspath(file_name)
    
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(file_path,"해당 파일이 존재하지 않습니다.")