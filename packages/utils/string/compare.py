from .normalize import normalize_string

from typing import List
from utils.variables import CLOTHES_COLOR, CLOTHES_CATEGORY

#쇼핑몰 제목과 상품명 비슷한지 확인하는 함수
def check_common_substring(s1:str, s2:str, length = 4) ->bool:
    """문자열 중 똑같은 부분이 있는지 확인하는 함수

    Args:
        s1 (str): first str
        s2 (str): second str
        length (int, optional): 같은 부분의 최소 길이 Defaults to 4.

    Returns:
        bool: return true if exist
    """
    
    s1_cleaned = normalize_string(s1)
    s2_cleaned = normalize_string(s2)

    # Create a set of substrings for the first string
    substrings_s1 = set()
    for i in range(len(s1_cleaned)):
        for j in range(i + length, len(s1_cleaned) + 1):
            substrings_s1.add(s1_cleaned[i:j])

    # Check if any substring of s1_cleaned is also a substring of s2_cleaned
    for substring in substrings_s1:
        if substring in s2_cleaned:
            return True

    return False


def find_most_similar_string(target_string: str, string_list: List[str]) -> str:
    """
    주어진 문자열과 문자열 리스트에서 가장 유사한 문자열을 찾습니다.
    
    Args:
        target_string (str): 비교 대상 문자열
        string_list (list): 비교할 문자열 리스트
    
    Returns:
        str: 가장 유사한 문자열. 리스트에서 유사한 것을 찾지 못하면 빈 문자열 반환.
    """
    max_similarity = 0
    most_similar_string = ""
    target = set(normalize_string(target_string))

    for candidate in string_list:
        # 두 문자열 간 공통 문자 계산
        common_characters = target & set(candidate)
        similarity = len(common_characters)

        # 최대 유사도 업데이트
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_string = candidate

    return most_similar_string


