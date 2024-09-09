import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os



def is_full_body_image(img_location):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'pose_landmarker.task')

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker
    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.IMAGE)


    with PoseLandmarker.create_from_options(options) as landmarker:
        mp_image = mp.Image.create_from_file(img_location)
        pose_landmarker = landmarker.detect(mp_image)
        
        try: 
            # Check all necessary landmarks are visible
            pose_landmarker_result = pose_landmarker.pose_landmarks[0]

            # Calculate if 50% of the necessary landmarks are visible
            count_visible = sum(lm.visibility > 0.5 for lm in pose_landmarker_result)
            return count_visible

        except:
            return 0