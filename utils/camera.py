import time
import numpy as np
import cv2 as cv
from utils.base_camera import BaseCamera
import sys
import os
from PIL import Image
import math
from yolov5.yolo import YOLO
from config import IS_REALTIME


yolo = YOLO()



# global_manager.set_value("real_time_type", "None")


runtime_path = sys.path[0]

class Camera(BaseCamera):

    def __init__(self):
        super(Camera, self).__init__()

    @staticmethod
    def frames(): # 重写BaseCamera的frames类
        global IS_REALTIME
        if IS_REALTIME:
            print("realtime mode")
            cap = cv.VideoCapture(0) # get local machine camera.
            
            if not cap.isOpened():
                return RuntimeError("can't open local camera!")
            
            while True:
                if not IS_REALTIME:
                    break

                res, frame = cap.read() # read.

                if res: # is have image. 
                    start_time = time.time()
                    img = Image.fromarray(np.uint8(frame))
                    img, result = yolo.detect_image(img)
                    detection_img = np.array(img)
                    end_time = time.time()
                    seconds = end_time - start_time
                    fps = 1 / seconds
                    

                    result_image = np.full_like(img, 255)

                    if result:
                        format_result = "" # reset
                        # print(result)

                        for index, line in enumerate(zip(*result)):
                            label = yolo.class_names[int(line[0])]
                            conf = round(line[1], 2)
                            top, left, bottom, right = line[2]
                            top     = max(0, np.floor(top).astype('int32'))
                            left    = max(0, np.floor(left).astype('int32'))
                            bottom  = min(img.size[1], np.floor(bottom).astype('int32'))
                            right   = min(img.size[0], np.floor(right).astype('int32'))
                            centre_x = (bottom - top) / 2
                            centre_y = (right - left) / 2
                            coordinate = tuple((centre_x, centre_y))

                            format_result = label.__str__()+" "+conf.__str__()+" "+coordinate.__str__()
                            cv.putText(result_image, f"{format_result}", (1, 20*(index+1)), cv.FONT_ITALIC, 0.7, (0, 0, 0), 1)

                        print(format_result)
                        # cv.putText(result_image, f"{format_result}", (1, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
                    


                    frame = np.hstack([frame, detection_img])
                    
                    cv.putText(frame, f"FPS:{fps.__str__():4.4}", (5, 20), cv.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)


                    yield cv.imencode('.jpg', frame)[1].tobytes(), cv.imencode('.jpg', result_image)[1].tobytes() # to bytes.
                    cv.waitKey(50)





                else:
                    print("can't get image, please check you camera if opened?")
                    break

            cap.release() # release resource.

        else:
            print("Video mode.")
            return None