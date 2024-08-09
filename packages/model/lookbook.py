from pytube import YouTube
import cv2
import torch
import numpy as np
import os
from typing import List, Optional, Tuple
from utils.files import clip_video, public_img_abspath
from utils.number import cal_rectangle_ratio
from .pose import is_full_body_image
from scenedetect import detect, ContentDetector


FILE_PATH = 'video.mp4'
YOUTUBE_LINK = "https://www.youtube.com/watch?v=" 

def download_video(url, path:str, timeList: List[float])-> Optional[str]:
    yt = YouTube(url)
    #FIXME: pytube HTTP Error 400: Bad Request가 뜸 수정 필요
    #TODO: lookbook model utils오류 
    try:
        #최고 해상도 선택
        video = yt.streams.filter(adaptive=True, file_extension='mp4').first()
        if video:
            video.download(filename=path)
            #영상 길이 추가
            timeList.append(yt.length)
            print(f"Downloaded video: {path}")
            return path
        else:
            return None
    except:
        return None

def find_least_shaky_frame(video_path:str, start_time: float, duration: float) -> Tuple[Optional[np.ndarray], float]:
    """영상에서 가장 흔들림이 적은 프레임을 찾아서 해당 프레임과 시간을 반환합니다.

    Args:
        video_path (str): 비디오 파일의 경로입니다.
        start_time (float): 시작 시간(초)입니다.
        duration (float): 지속 시간(초)입니다.

    Returns:
        Tuple[Optional[np.ndarray], float]: 가장 흔들림이 적은 프레임의 이미지(numpy 배열)와 그 프레임의 시간(초)입니다.
    """
    cap = cv2.VideoCapture(video_path)

    # CAP_PROP_FPS를 이용하여 프레임 속도를 가져옴
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    
    # Calculate start frame and end frame based on the given time and duration
    start_frame = int(start_time * frame_rate)
    end_frame = start_frame + int(duration * frame_rate)

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    last_frame = None
    min_shake_score = np.inf
    least_shaky_frame = None
    current_frame_index = start_frame
    least_shaky_frame_time = start_time

    while current_frame_index <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to grayscale for analysis 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if last_frame is not None:
            # Calculate frame difference
            diff = cv2.absdiff(last_frame, gray)
            shake_score = np.sum(diff)  # Basic shake score

            if shake_score < min_shake_score:
                min_shake_score = shake_score
                least_shaky_frame = frame.copy()
                least_shaky_frame_time = current_frame_index / frame_rate

        last_frame = gray
        current_frame_index += 1

    cap.release()
    return least_shaky_frame, least_shaky_frame_time

def extract_bounding_box(image: np.ndarray, time: float, model)-> Optional[List[int | float]]:
    """이미지에서 사람의 bounding box 정보를 가져옵니다.

    Args:
        image (np.ndarray): _description_
        time (float): _description_
        model (_type_): default : yolov5 model

    Returns:
        Optional[List[int | float]]: x1, y1, x2, y2, confidence, ratio 
    """
    newImg = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model(newImg)

    # 'person' 클래스 필터링 (클래스 0)
    person_results = results.xyxy[0][results.xyxy[0][:, -1] == 0]
    maxRatio = 0
    boxResult = []
            
    for box in person_results:
        confidence = int(box[4].item() * 100)  # 신뢰도를 백분율로 표시
        box = [int(i) for i in box[:4]]
        ratio = cal_rectangle_ratio(box[0], box[1], box[2], box[3])
        if maxRatio < ratio:
            maxRatio = ratio
            boxResult = box + [confidence] + [ratio]                
    

        #cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 3)  # 빨간색 직사각형, 두껍게
        #cv2.putText(image, f"{confidence}%  b{box[0]} {box[1]}  a{box[2]} {box[3]}", (box[0]+10, box[1] + 20), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 255), 1)  # 빨간색 글자
        
        # 이미지 저장
    #cv2.imwrite(f'img/test-img-{time}.jpg', image)
    
    # 결과 표시
    #torch.Size([member, 6 value])
    #no person in list
    if(person_results.size()[0] == 0):
        return None
    
    return boxResult

def find_best_frames(extract_frames: List[np.ndarray | float], timeline_list: List[float], time_range_list: List[Tuple[float,float]],fileName:str):
    # 각 시간 구간에 대해 최적의 프레임을 찾습니다.
    results = []
    
    # timeline_list의 마지막 요소는 구간의 끝을 정의하지 않으므로, 제외합니다.
    for i in range(len(timeline_list) - 1):
        #먼저 타임라인 안에 들어가는 Scene을 선정
        start_time = timeline_list[i]
        end_time = timeline_list[i + 1]
        
        scene_in_timeline = []
        for startSecond, endSecond in time_range_list:
            if start_time <= startSecond and endSecond <= end_time:
                scene_in_timeline.append([startSecond, endSecond])
                
        
        frames_in_interval = []
        #scene에 있는 best cut 담기
        for start, end in scene_in_timeline:
            for frame in extract_frames:
                if start <= frame[1] <= end:
                    frames_in_interval.append(frame)
            

            
            # 이 구간의 프레임 중에서 ratio가 가장 높은 프레임을 찾습니다.
        if frames_in_interval:                
            for frame in frames_in_interval:
                temp_file_path = public_img_abspath("temp.jpg")
                cv2.imwrite(temp_file_path, frame[0])
                score = is_full_body_image(temp_file_path)
      
                frame.append(score)  # 프레임 목록에 점수 추가
            
                    
            
            #isfullbodyimage 점수 설정
            #그 점수로 frames_in_intervale sort
            if any(score for score in frames_in_interval):
                sorted_frames = sorted(frames_in_interval, key=lambda x: x[3], reverse=True)
            else:
                #점수가 없으면 ratio로 정렬
                sorted_frames = sorted(frames_in_interval, key=lambda x: x[2], reverse=True)

            # 가장 큰 값을 best_frame으로 선택
            best_frame = sorted_frames[0]

            # best_frame을 기준으로 time range 앞과 뒤를 나누고, 기본적인 클리핑 수행
            def clip_based_on_best_frame(best_frame):
                for start, end in scene_in_timeline:
                    if start <= best_frame[1] <= end:                  
                        if end-start <= 5 and len(sorted_frames) > 1:
                            second_best_frame = sorted_frames[1]
                            # 두 번째로 큰 값에 대해서도 비슷한 처리 수행
                            
                            for secondStart, SecondEnd in scene_in_timeline:       
                                if secondStart <= second_best_frame[1] <= SecondEnd:                 
                                    clip_video(FILE_PATH, [(start, end), (secondStart, SecondEnd)], f"{fileName}_{i}")   
                        else:
                            #clipVideo(FILE_PATH, [(best_frame[1], end), (start, best_frame[1])])          
                            clip_video(FILE_PATH, [(start, end)], f"{fileName}_{i}")                         
                                        
                                                

                
            clip_based_on_best_frame(best_frame)
            img_path = public_img_abspath(f'{fileName}_{i}.webp')
            cv2.imwrite(img_path, best_frame[0])             
            
            # best_frame = max(frames_in_interval, key=lambda x: x[2])
            # #best frame을 기준으로 time range 앞과 뒤를 나눕니다
            # for start, end in scene_in_timeline:
            #     if start<= best_frame[1] <= end:
            #         clipVideo(FILE_PATH, [(best_frame[1], end), (start, best_frame[1])])
            
            results.append(i)
        
    return results


def download_coordi_video_image(videoId: str, timeList : List[float],fileName: str):
    LINK = YOUTUBE_LINK + videoId

    if not download_video(LINK, FILE_PATH, timeList):
        return
        
################################################################            
    ##scene에 따라 구분하는 함수 time range 에는 시작, 종료 second 저장
    time_range = []
    
    scene_list = detect(FILE_PATH, ContentDetector(threshold=15, min_scene_len=60))
    for i, scene in enumerate(scene_list): 
        start_sec = scene[0].get_seconds()
        end_sec = scene[1].get_seconds()
        time_range.append((start_sec, end_sec))

################################################################   
    ##흔들림 적은 프레임 (frame, second)
    least_shaky_frames = []

    for start, end in time_range:
        if end-start > 2:
            start = start + 0.5
            end = end - 0.5
            least_shaky_frame, frame_time = find_least_shaky_frame(FILE_PATH, start, end-start)
            if least_shaky_frame is not None and least_shaky_frame.size != 0:
                ##cv2.imwrite(f'img/ver{LOCATION}/img-{frame_time}.jpg', least_shaky_frame)
                least_shaky_frames.append((least_shaky_frame, frame_time))
            else:
                print("Frame is empty or not captured properly.", str(frame_time))

################################################################   
    MODEL = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    box_result = [extract_bounding_box(frame,time, model=MODEL) for frame, time in least_shaky_frames]

    extract_frames = []
    for index, box in enumerate(box_result):
        if not box:
            continue
        
        center_of_x = (box[0] + box[2])/2
        distance_y = abs(box[1] - box[3])
        
        if center_of_x> 1000 or center_of_x < 300:
            continue
        
        if distance_y < 550:
            continue
        
        if box[4] > 70:
            extract_frames.append([least_shaky_frames[index][0], least_shaky_frames[index][1], box[5]])
            #cv2.imwrite(f'img/ver{LOCATION}/img-{least_shaky_frames[index][1]}-ratio-{box[5]}.jpg', least_shaky_frames[index][0])


    
################################################################   
    best_frames = find_best_frames(extract_frames, timeList, time_range,fileName)

    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
    else:
        print("해당 파일이 존재하지 않습니다.")
        
    return best_frames

