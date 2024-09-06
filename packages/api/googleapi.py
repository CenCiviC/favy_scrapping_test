import serpapi
from utils.string import normalize_string
from dotenv import load_dotenv
import os 
from typing import Optional, List, Tuple
from utils.variables import MAJOR_SITES, EXCEPTION_SITES

load_dotenv()
SERPAPI_API_KEY = os.environ.get('SERPAPI_API_KEY')

#TODO: raise api error

def search_product_link(brandName: str, productName: str) -> Optional[str]:
    """상품 링크를 검색하여 반환합니다.

    Args:
        brandName (str): 검색할 상품의 브랜드 이름입니다.
        productName (str): 검색할 상품의 이름입니다.

    Returns:
        Optional[str]: 검색된 상품의 링크를 반환하거나, 적합한 링크를 찾지 못하면 None을 반환합니다.
    """
    if productName:
        searchQuery = productName
        if brandName:
            searchQuery += " " + brandName
        
        client = serpapi.Client(api_key=SERPAPI_API_KEY)
        results = client.search({
            "engine": "google_images",
            "q": searchQuery,
            "gl": "kr",
            "hl": "ko",
        })
        
        candidate_link = []
        try:
            candidate_link = results.data["images_results"][0:2]
        except:
            candidate_link = None

        try:
            for link_response in candidate_link:
                keywords = EXCEPTION_SITES
                if any(keyword in link_response['source'] for keyword in keywords):
                    continue

                link = link_response['link']
                return link
        except:
            return None

    return None


def search_related_product(url: str) -> Tuple[Optional[str], List[str]]:
    """주어진 URL에 관련된 상품 링크를 검색하여 반환합니다. 이미지가 없을 경우 오류 발생

    Args:
        url (str): 상품 이미지의 URL입니다.

    Returns:
        Tuple[Optional[str], List[str]]: 검색된 관련 상품 링크의 목록과 다음 페이지 토큰을 반환합니다.
        이미지가 없을 경우 None을 반환합니다.
    """
    try:
        client = serpapi.Client(api_key=SERPAPI_API_KEY)
        results = client.search({
            "engine": "google_lens",
            "url": url,
            "hl": "ko",
            "country": "kr",
        })

        relevant_results = []

        # 검색 결과가 있는지 확인
        if "visual_matches" not in results or not results["visual_matches"]:
            raise ValueError("이미지와 관련된 검색 결과가 없습니다.")

        for result in results["visual_matches"]:
            processed_source = normalize_string(result["source"])
            for site in MAJOR_SITES:
                processed_site = normalize_string(site)
                if processed_source == processed_site:
                    link = result["link"]
                    relevant_results.append(link)
                    break
            
            if len(relevant_results) > 5:
                break
        
        page_token = results.get("image_sources_search", {}).get("page_token")

        return page_token, relevant_results
    

    except ValueError as e:
        print(f"오류 발생: {e}")
        return None, []
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")
        return None, []



#같은 이미지의 판매처를 찾는 함수
# https://serpapi.com/google-lens-image-sources-api 문서 확인
# example page token : MDRjZDM1N2YtZGZlZS00MGZiLWE1YmUtN2E2NDU4ZGUwMGEw
def search_same_product(page_token:str):
    client = serpapi.Client(api_key=SERPAPI_API_KEY)
    results = client.search({
        "engine": "google_lens_image_sources",
        "hl": "ko",
        "country": "kr",
        "page_token": {page_token},
    })
    
    #TODO: major site의 정보 가져오기 
    relevant_results = []
    
    for result in results["image_sources"]:
        processed_source = normalize_string(result["source"])
        for site in MAJOR_SITES:
            processed_site = normalize_string(site)
            if processed_source == processed_site:
                link = result["link"]
                relevant_results.append(link)
                break
        
        if len(relevant_results) >=10:
            break

    return relevant_results


