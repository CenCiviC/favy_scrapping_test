from datetime import datetime

# 입력된 문자열을 계절로 변환
def calculate_season_by_date(date_str):   
    date = datetime.fromisoformat(date_str)
    
    #TODO: 계절이 끝나는 시기를 말일이 아닌 1-2주 정도 당겨야 함(유튜브 업로드 일자 때문에)
    # 봄: 3월 1일부터 5월 31일까지
    # 여름: 6월 1일부터 8월 31일까지
    # 가을: 9월 1일부터 11월 30일까지
    # 겨울: 12월 1일부터 2월 28일까지

    month = date.month
    day = date.day

    if month == 3 or (month == 4 and day <= 30) or (month == 5 and day <= 31):
        return "sp"
    elif month == 6 or (month == 7 and day <= 31) or (month == 8 and day <= 31):
        return "su"
    elif month == 9 or (month == 10 and day <= 31) or (month == 11 and day <= 30):
        return "fa"
    else:
        return "wi"