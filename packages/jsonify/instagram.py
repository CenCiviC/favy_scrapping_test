#json
from typing import Tuple, Optional, List

def jsonify_instagram_shot(influencer_name, influencer_profile, shot_url):
    return ({
        "id" : influencer_name,
        "profileImg" : influencer_profile,
        "shotImg" : shot_url,
    })
