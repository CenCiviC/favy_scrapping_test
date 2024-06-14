import re
def extract_timeline_from_video(description: str):
    ##무슨 함수야 이건 
    pattern = r"\b\d{1,2}:\d{2}\b"

    timeline = re.findall(pattern, description)
    return timeline

def timeline_to_second(timeline: str) -> int:
    """ 00:00:00 or 00:00 형식의 타임라인을 second로 바꿈

    Args:
        timeline (str): _description_

    Raises:
        ValueError: 형식 오류

    Returns:
        int: second
    """
    try:
        parts = list(map(int, timeline.split(':')))
    except:
        raise ValueError("Invalid timeline format")
    if len(parts) == 3: 
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    else:
        raise ValueError("Invalid timeline format")
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    
    return total_seconds

def second_to_timeline(seconds: int) -> str:
    """second to timeline 00:00:00 format

    Args:
        seconds (int): second

    Returns:
        str: 00:00:00 format
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    
    return f"{hours:02}:{minutes:02}:{seconds:02}"