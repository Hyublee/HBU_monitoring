##### Basler Camera Communication Ver 0.1 #####
##### 2023.12.26
##### Requirement package (pypylon)

from pypylon import pylon
import cv2
import numpy as np
import time 

class Cam():
    def __init__(self):
        for i in range(0, 3):
            try:
                self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
                if self.camera is not None:
                    self.camera.Open()
                    self.cam_setting(self)
                    print("Camera Connected!")
                    break 
            except:
                print("No device is available, Please check camera connection")
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)  ## Continous image grab
        
    def cam_setting(self, expos=5000, width=720, height=520):
        # self.camera.ExposureTime.SetValue(expos)
        self.camera.Width.SetValue(width)
        self.camera.Height.SetValue(height)
    
    def get_data(self):
        self.grabResult = self.camera.RetrieveResult(400, pylon.TimeoutHandling_ThrowException)          # timeOut > exposure time
        if self.grabResult.GrabSucceeded():
            _img = self.grabResult.Array
        else:
            print("faild get image")
            self.grabResult.Release()
            self.camera.Close()
        return _img

    def processing(self, img):
        ret, dst = cv2.threshold(img, 120, 255, cv2.THRESH_BINARY)
        return dst
    
if __name__ == '__main__':
    cam=Cam()    
    start_time = time.time()
    while True:
        img = cam.get_image()

        if cv2.waitKey(1) & 0xFF == ord('q') : break
        cv2.imshow('Camera', img)

    cam.camera.Close()
    cv2.destroyAllWindows()
