#json
from typing import Tuple, Optional, List

def jsonify_instagram_info(influencer_name, influencer_profile, shot_url, date):
    return {
        "influencer": {
            "id": influencer_name,
            "profileImg": influencer_profile
        },
        "shot": {
            "shotImg": shot_url,
            "date": date
        }
    }

    
    
def jsonify_instagram_shot_info(influencer_name, influencer_profile, shot_url, date, datas):
    basic_info = jsonify_instagram_info(influencer_name, influencer_profile, shot_url, date)
    return {
        **basic_info,
        "product": datas
    }
