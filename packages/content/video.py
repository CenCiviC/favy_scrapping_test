from enum import Enum
from typing import List



from .coordi import Coordi
from packages.model.lookbook import download_coordi_video_image
from packages.api.youtubeapi import get_full_video_description
from packages.api.gpt import summarize_caption
from packages.utils.number import timeline_to_second
from packages.utils.files import delete_local_file
from packages.api.aws import save_file_to_s3

class CaptionInfo(Enum):
    TIMELINE = 0
    BRAND = 1
    PRODUCT = 2
    URL = 3

FILE_PATH = 'video.mp4'
YOUTUBE_LINK = "https://www.youtube.com/watch?v=" 

class Video:
    def __init__(self, channelName:str, videoId:str) -> None:
        self.videoId = videoId
        self.channel_id = channelName
        print(f"{videoId} scrapping 시작")
        self.coordis: List[Coordi] = []
        
        description = get_full_video_description(videoId)
        self.addCoordis(description)
        
        # if os.path.exists(FILE_PATH):
        #     os.remove(FILE_PATH)
        # else:
        #     print("해당 파일이 존재하지 않습니다.")
        
    def addCoordis(self, description: str):
        productInformations = summarize_caption(description)
        
        productDict = {}
        timeList = []
        if not productInformations:
            return

        for productInfoList in productInformations: 
            timeline = productInfoList[CaptionInfo.TIMELINE.value]
            brandName = productInfoList[CaptionInfo.BRAND.value]
            productName = productInfoList[CaptionInfo.PRODUCT.value]
            productUrl = productInfoList[CaptionInfo.URL.value]
            
            if not timeline:
                continue
            
            if not productDict.get(timeline):
                productDict[timeline] = [[ brandName,productName,productUrl]]
            else:
                productDict[timeline].append([brandName,productName,productUrl])
    
        # timeline not exist
        if(len(productDict) <= 1):
            print(f"no timeline in {self.videoId}")
            return

        #for loop time range 만들고 
        for key in productDict.keys():
            if timeline_to_second(key):
                timeList.append(timeline_to_second(key))
        #time range index 접근해서 lookbook.py에 넣기
        try:
            ableCoordiIdxes =   download_coordi_video_image(self.videoId, timeList, f"{self.videoId}")
        except Exception as ex:
            print('에러가 발생 했습니다', ex)
            return 

        if not ableCoordiIdxes:
            return
        
        for idx in ableCoordiIdxes:
            cody_id = f"{self.videoId}_{idx}"
            s3location = f"{self.channel_id}/{cody_id}"
            imgLocation = s3location + ".webp"
            videoLocation = s3location + ".mp4"
            
            newCoordi = Coordi(cody_id, imgLocation,videoLocation, list(productDict.values())[idx], list(productDict.keys())[idx])
            if len(newCoordi.products) == 0:
                continue
                 
            

            save_file_to_s3(f"{cody_id}.webp", imgLocation, True)
            save_file_to_s3(f"{cody_id}.mp4", videoLocation, False)
            delete_local_file(f"img/{cody_id}.webp")
            delete_local_file(f"video/{cody_id}.mp4")
            
            self.coordis.append(newCoordi)

            #상품들을 돌면서 저장
            for product in newCoordi.products:
                data = [imgLocation, videoLocation, newCoordi.timeline, product.productInformation.productName]
                #save_coordi_data_to_sheet(data)
                
        
                    
            
    
    def haveCoordi(self):
        if self.coordis == []:
            return None
        return self.coordis
    
    def return_coordis(self):
        if not self.haveCoordi:
            return None
            
        return self.coordis    

