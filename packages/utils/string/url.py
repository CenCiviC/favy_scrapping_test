from urllib.parse import urlparse
import re
from typing import Tuple, List

def extract_shoppingmall_name(url:str) -> str:
    parsed_url = urlparse(url)
    netloc = re.sub(r'^(www\.|m\.)', '', parsed_url.netloc)
    
    return netloc.split('.')[0]

def change_link_to_variable(comment: str) -> Tuple[str, List[str]]:
    """
    주어진 문자열에서 URL을 찾아 "LINK"와 그 인덱스로 대체하고, 수정된 문자열과 원래 URL 목록을 반환합니다.

    Args:
        comment (str): 입력 문자열.

    Returns:
        Tuple[str, List[str]]: 수정된 문자열과 대체된 URL의 목록.
    """

    # Improved regex pattern to accurately capture full URLs
    url_pattern_improved = r'\b(?:https?://|www\.|m\.)\S+'

    # Find all URLs in the text using the improved pattern
    urls_improved = re.findall(url_pattern_improved, comment)

    # Initialize a list to store replaced URLs
    replaced_urls = []

    # Replace URLs with "LINK" followed by their index, correctly capturing full URLs
    for index, url in enumerate(urls_improved, start=1):
        comment = re.sub(re.escape(url), f"LINK{index}.com", comment, 1)
        replaced_urls.append(url)

    # Show the modified comment and the list of replaced URLs
    modified_comment = comment
    
    return modified_comment, replaced_urls


def get_youtube_video_id(url:str) -> str:
    """youtube url로 부터 video id를 구합니다.

    Args:
        url (str): youtube link includes "v="

    Returns:
        str: 문자열의 video id
    """
    # url에서 'v=' 이후의 문자열을 추출합니다.
    start_index = url.find('v=') + 2  # 'v=' 다음의 인덱스를 찾습니다.
    if start_index == 1:  # 'v='이 없는 경우
        raise ValueError("Invalid youtube link format")

    # 'v=' 다음 '&' 문자를 찾습니다.
    end_index = url.find('&', start_index)
    if end_index == -1:  # '&' 문자가 없는 경우, url의 끝까지가 video ID입니다.
        video_id = url[start_index:]
    else:
        video_id = url[start_index:end_index]  # '&' 이전까지의 문자열이 video ID입니다.

    return video_id
