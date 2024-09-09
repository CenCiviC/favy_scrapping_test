#####gpt api
import os
from openai import OpenAI
import re
from dotenv import load_dotenv
from typing import Optional, Tuple, List

from packages.utils.string import change_link_to_variable, find_most_similar_string
from packages.utils.variables import CLOTHES_COLORS, CLOTHES_CATEGORIES


load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def filter_category_color(category_script: str)-> Optional[Tuple[str, str]]:

    def normalize_text(text):
      try:
        category = re.split('--', text)[1]
        color = re.split('--', text)[2]
        
        return (category, color)
      except:
        return None

    normalized_result = normalize_text(category_script)

    if not normalized_result:
        return None  # 결과가 없으면 None 반환

    unnormalized_category, unnormalized_color = normalized_result
    
    if not unnormalized_category and unnormalized_color:
      return None

    # 최대 유사도 및 가장 유사한 카테고리 초기화
    most_similar_category = find_most_similar_string(unnormalized_category, CLOTHES_CATEGORIES)
    most_similar_color = find_most_similar_string(unnormalized_color, CLOTHES_COLORS)

    # 가장 유사한 카테고리 반환
    return most_similar_category, most_similar_color

def categorize_image(image_url: str, product_name: str)-> Tuple[str, str]:
    client = OpenAI(
        api_key= OPENAI_API_KEY ,
    )

    try:
      response = client.chat.completions.create(
        model="gpt-4o",
          messages=[
              {
              "role": "system",
              "content": """너는 의류 업계 종사자야. 너가 할 일은 사진과 제품명을 보고 어떤 의류 카테고리인지 와 의류의 색상을 판단하는 거야. 카테고리는 제품명을 우선으로 판단해줘\n의류 카테고리와 색상은 하나만 지정할 수 있어\n의류 카테고리는 대분류와 소분류가 있으며 카테고리를 지정할 때 소분류가 존재하는 대분류면 무조건 소분류까지 써야 돼\n만약 카테고리에 해당 안 되는 사진이면 패션잡화/기타에 넣어줘.\n 형식은 --대분류/소분류--색상 으로 해줘 \n카테고리는 아래와 같아 

              -아우터
              패딩, 코트, 집업/점퍼, 자켓, 플리스, 바람막이, 가디건, 야상

              -상의
              후드, 맨투맨, 니트, 셔츠, 긴소매티셔츠, 블라우스, 조끼, 반소매티셔츠, 민소매

              -팬츠
              롱팬츠, 슬랙스, 데님, 숏팬츠, 치마바지

              -원피스/세트
              롱원피스, 투피스, 점프수트, 미니원피스

              -스커트
              미디/롱스커트, 미니 스커트

              -신발
              스니커즈, 워커부츠, 블랫/로퍼, 힐, 샌들, 슬리퍼/쪼리, 블로퍼/뮬

              -가방
              크로스백, 숄더백, 토트백, 클러치,에코백, 백팩

              -트레이닝
              트레이닝 세트, 트레이닝 상의, 트레이닝 하의, 레깅스
              
              -이너웨어
              
              -홈웨어

              -비치웨어

              -패션잡화
              모자, 양말, 기타

              -악세사리
              헤어 악세서리, 목걸이, 팔찌, 발찌, 반지, 귀걸이

색상은 다음 중에서 가장 가까운 색상을 선정해줘
    "블랙", "화이트", "그레이", "레드", "핑크", "오렌지", "베이지", "브라운",
    "옐로우", "그린", "카키", "민트", "블루", "네이비", "스카이블루",
    "퍼플", "라벤더", "와인", "네온", "골드", "실버"
"""
              },
              {
              "role": "user",
              "content": [
                  {
                      "type": "text",
                      "text": product_name        
                  },
                  {
                  "type": "image_url",
                  "image_url": {
                      "url": image_url
                  },
                  },
              ],
              },
              # {
              # "role": "assistant",
              # "content": "--아우터/자켓--"
              # },
              # {
              # "role": "assistant",
              # "content": "--신발/슬리퍼/쪼리--"
              # },
              # {
              # "role": "assistant",
              # "content": "--패션잡화/기타--"
              # }
          ],
          max_tokens=300,
      )
      
      result =  filter_category_color(response.choices[0].message.content)
      if result:
        return result
      else:
        raise ValueError("gpt error")
    except:
      raise ValueError(f"ERROR image {product_name}")


def gpt_summarize_description(description: str) -> Optional[str]:
  """지정된 형식으로 상품 정보를 정리합니다.

  Args:
      description (str): 변환할 설명란.

  Returns:
      Optional[str]: brand--productName--link 형식으로 변환된 문자열.
  """
  client = OpenAI(
    api_key= OPENAI_API_KEY ,
  )
  try:
    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {
          "role": "system",
          "content": "다음 글은 유튜브에서 자신이 입은 옷을 정리한 거야. 글을 보고 각 코디 별로 분류를 해야 돼. 링크만 알려줄 때도 있고  제품 정보를 적는 경우도 있어. 보통 글 형식이 일정한 곳에 입은 옷을 적어. 정리할 때는 아래 규칙을 지켜야 해. 1. 형식은 '타임라인--브랜드--제품명--링크' 이고 글에 없으면 X를 쓴다 2. 같은 옷이 여러 번 나와도 쓴다.  3. 항목은 적힌 그대로 정리한다. 4. 글에 의류가 아예 없는 경우 ‘not clothing'을 적는다. 제품명에는 실제 상품명을 적어야 해. 예를 들어, Top. bymood example.com인 경우 01:21--bymood--X--example.com이 돼 Top은 상품명이 아닌 카테고리니까" 
        },
        {
          "role": "user",
          "content": description,
        },
        # {
        #   "role": "assistant",
        #   "content": "not clothing"
        # }
        # {
        #   "role": "assistant",
        #   "content": "- 지그재그--안개꽃 원피스--X\\n쓰리타임즈--타이다이 시스루 반팔 크롭t--LINK2.com\\nbymood--X--X"
        # }
      ],
      temperature=0,
      max_tokens=1000,
      top_p=0,
      frequency_penalty=0,
      presence_penalty=0
    )
    
    content = response.choices[0].message.content
    if content =="not clothing":
      return None
    else:
      return response.choices[0].message.content
  except:
    return None

def summarize_caption(description: str) -> Optional[list[list[str]]]:
  """지정된 형식으로 설명란을 정리합니다.

  Args:
      description (str): 변환할 설명란.

  Returns:
      Optional[list[list[str]]]: brand,productName,link의 리스트.
  """
  #arrange links
  caption, links = change_link_to_variable(description)
  
  #gpt summarize
  summarized_caption = gpt_summarize_description(caption)
  if not summarized_caption:
    return None
  
  def check_format(s):
      parts = s.split("--")
      return len(parts) == 4
  
  #brand, product, url
  product_info_lists = [re.split('--', line) for line in re.split('\n', summarized_caption) if check_format(line)]
  
  for product_index, product_info in enumerate(product_info_lists):
      # 각 정보 항목을 순회
      for infoIndex, information in enumerate(product_info):
          if information == 'X':
              # 현재 항목을 None으로 설정
              product_info_lists[product_index][infoIndex] = None
              continue

          # "LINK" 뒤에 오는 숫자 추출
          match = re.search(r'LINK(\d+)', information)
          if match:
              # 추출된 숫자를 인덱스로 사용
              index = int(match.group(1)) - 1
              # 인덱스가 유효한지 확인 후 링크 업데이트
              if 0 <= index < len(links):
                  product_info_lists[product_index][infoIndex] = links[index]

  return product_info_lists