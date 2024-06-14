import boto3
from dotenv import load_dotenv
from utils.files import public_img_abspath
from utils.files import public_video_abspath
import os 

load_dotenv()
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')


def save_file_to_s3(fileName: str, s3location: str, isImage: bool):
    local_file_name = ""
    if isImage:
        local_file_name = public_img_abspath(fileName) # Path for image files
    else:
        local_file_name = public_video_abspath(fileName)   # Path for video files

    bucket = 'linkive-bucket'  # S3 bucket name
    key = s3location  # Key within the bucket for the file

    # Initialize S3 client
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="ap-northeast-2"
    )

    # Upload the file to S3
    res = s3.upload_file(local_file_name, bucket, key)
    return res