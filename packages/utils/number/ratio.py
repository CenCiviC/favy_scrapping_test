# 가로와 세로 길이의 비율을 계산
def cal_rectangle_ratio(x1:int, y1:int, x2:int, y2:int) -> float:
    width = abs(x1 - x2)
    height = abs(y1 - y2)

    ratio = height / width if width != 0 else 0

    return ratio