def normalize_string(input_str: str):
    """공백을 제거하고, 영어를 대문자로 변환합니다. 한글은 그대로 유지됩니다.

    Args:
        input_str (str): 변환할 문자열.

    Returns:
        str: 변환된 문자열.
    """
    processed_str = ""
    for char in input_str:
        if char != ' ':
            # 영어인 경우 대문자로 변환
            if 'A' <= char <= 'Z' or 'a' <= char <= 'z':
                processed_str += char.upper()
            else:
                processed_str += char
    return processed_str