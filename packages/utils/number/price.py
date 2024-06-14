import re

#문장에서 가격만 extract하는 함수, 가격과 관련 없는 단어가 있는 경우 0출력
def extract_price(s: str) -> int:
    # 숫자, 쉼표, 마침표를 포함한 패턴을 찾기 위한 정규 표현식
    pattern = r'(\d+(?:,\d{3})*(?:\.\d+)?)(?:\s*(원|krw|KRW|₩|won|\$)|\s*$)'

    
    # 정규 표현식을 사용하여 조건에 맞는 가격 찾기
    match = re.search(pattern, s, re.IGNORECASE)
    
    # 조건에 맞는 가격이 있다면 추출 및 반환
    if match:
        price = match.group(1)
        # 쉼표를 제거하고 반환
        number_str = price.replace(',', '').split('.')[0]
    else:
        # 조건에 맞는 가격이 없다면 None 반환
        return 0
    
    if number_str =='':
        return 0
    
    extracted_number = int(number_str)
    
    #너무 적은 금액은 탈락(일단은 1000원 기준)
    if extracted_number <= 1000:
        return 0
    
    #달러 환율 계산
    if '$' in s:
        return extracted_number * 1350
    else:
        return extracted_number
    
    
#쇼핑몰에서 가격이 맞는지 확인하는 함수
def is_currency(s: str) -> bool:
    s_lower = s.lower().replace(' ', '') # 공백 제거
    # 숫자와 함께 오는 통화 기호를 찾는 정규표현식 패턴
    pattern = r'(\d+([,.]\d+)?(원|krw|₩|won|\$))|((원|krw|₩|won|\$)\d+([,.]\d+)?)'

    matches = re.search(pattern, s_lower)

    
    if matches:
        # 숫자 부분만 추출하여 검사
        if extract_price(s_lower):
            return True
    return False
