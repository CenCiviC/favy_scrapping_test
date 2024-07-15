def controller_celeb(url: str):
    try:
        id = get_channel_id(url)
        name,profileImg,youtubeId,youtubelink,channelId,subscriberCnt,videoCnt = get_youtube_channel_info(id)

        imgLocation = f"{name}_profile"
        download_image_by_url(profileImg, imgLocation)
        s3location = f"{name}/{imgLocation}.webp"
        save_file_to_s3( f"{imgLocation}.webp", s3location, True)

        data = [name, youtubeId, channelId, videoCnt,subscriberCnt, youtubelink, s3location]
        #save_celeb_data_to_sheet(data)
    except:
        return None
    return channelId

def controller_codies(video_id):
    channelId, title,date,link,thumbnailImg = get_youtube_codies_info(video_id)

    imgLocation = f"{video_id}"
    download_image_by_url(thumbnailImg, imgLocation)
    

    
    s3location = f"{channelId}/{imgLocation}.webp"
    save_file_to_s3(f"{imgLocation}.webp", s3location, True)
    
    deleteLocalFile(f"img/{imgLocation}.webp")

    data = [channelId, title,date,link, s3location]
    return data

