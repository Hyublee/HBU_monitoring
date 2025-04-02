# '''
# Basler Camera 통신 및 이미지 데이터 수집 코드
# Copyleft ⓒ Seonghun_ji
# last update: 2024.09.03
# Requirement package (pypylon, opencv-python)
# '''
# from MvCameraControl_class import MvCamera
# import cv2
# import numpy as np
# import time
# import configparser as conf
# from collections import deque
# import threading

# class Camera_communication:
#     def __init__(self, config_path="./Monitoring/Sensors/ini_files/Camera.ini"):
#         """Initializes the camera communication with a path to the configuration file."""
#         self.config = conf.ConfigParser()
#         self.config.read(config_path)
        
#         self.camera_params = {key: value for key, value in self.config.items('parameters')}
#         self.data = {key: value for key, value in self.config.items('data')}
#         print(f"parameters:{self.camera_params}\ndata:{self.data}")

#         self.frame_width = int(self.camera_params['width'])
#         self.frame_height = int(self.camera_params['height'])
    
#         self.activate = False
#         self.retry_interval = 5  # seconds

#         self.create_camera()

#     def create_camera(self, retries=3):
#         """Creates and opens a camera object based on the configuration."""
#         for i in range(retries):
#             try:
#                 self.camera = MvCamera()
#                 device_list = self.get_device_list()
#                 if len(device_list) == 0:
#                     raise Exception("No camera device found.")

#                 self.camera.Open(device_list[0])
#                 self.camera.SetIntValue("Width", self.frame_width)
#                 self.camera.SetIntValue("Height", self.frame_height)
#                 self.camera.SetFloatValue("ExposureTime", float(self.config['parameters']['exposure']))
#                 self.camera.SetFloatValue("Gain", float(self.config['parameters']['gain']))
#                 self.camera.StartGrabbing()

#                 print("Camera Connected!")
#                 self.activate = True
#                 break
#             except Exception as e:
#                 print(f"Connection attempt {i + 1} failed. Error: {e}")
#         else:
#             print("Failed to connect to the camera after several retries.")
#             self.activate = False

#     def get_device_list(self):
#         """Retrieve a list of available camera devices."""
#         device_list = []
#         cam_obj = MvCamera()
#         ret = cam_obj.EnumDevices()
#         for i in range(ret):
#             device_list.append(i)
#         return device_list

#     def get_image(self):
#         """Capture an image frame from the camera."""
#         if self.activate:
#             try:
#                 ret, frame = self.camera.GetOneFrameTimeout(1000)
#                 if ret == 0:
#                     img = np.frombuffer(frame, dtype=np.uint8).reshape((self.frame_height, self.frame_width))
#                     self.data['image'] = img
#                     return self.data
#                 else:
#                     print("Failed to grab image.")
#                     return None
#             except Exception as e:
#                 print(f"!!!!!!!!get_image Error: {e}")
#                 self.activate=False
#                 return None
#         else:
#             print("camera close")
#             self.camera.Close()

#         return self.data 
    
#     def close_camera(self):
#         """Close the camera connection."""
#         if self.camera is not None:
#             self.camera.StopGrabbing()
#             self.camera.Close()
#             print("Camera closed.")

# class Camera_DB:
#     def __init__(self, max_size=30):
#         self.data_queue = deque(maxlen=max_size)
#         self.start_time = time.time()

#     def store_data(self, data):
#         self.data_queue.append(data)

#     def retrieve_data(self):
#         if self.data_queue:
#             return self.data_queue[-1]
#         return None

# class Camera_Collector(threading.Thread):
#     def __init__(self, camera, db):
#         threading.Thread.__init__(self)
#         self.camera = camera
#         self.db = db
#         self.running = True
#         self.sample_rate = int(self.camera.camera_params['fps'])  # FPS

#     def run(self):
#         while self.running:
#             loop_start = time.perf_counter()
#             if self.camera.activate:
#                 data = self.camera.get_image()
#                 if data:
#                     self.db.store_data(data)
#             else:
#                 time.sleep(0.5)

#             sleep_time = max(0, (1/self.sample_rate)-(time.perf_counter()-loop_start))
#             time.sleep(sleep_time)

#     def stop(self):
#         self.running = False

# def main():
#     camera = Camera_communication()
#     db = Camera_DB()
#     collector = Camera_Collector(camera, db)
#     collector.start()

#     try:
#         while True:
#             time.sleep(0.1)  # Adjust timing or condition as needed
#             if db.data_queue:
#                 data = db.retrieve_data()
#                 if data and 'image' in data:
#                     img = data['image']
#                     print(data)
#                     cv2.imshow('Camera', img)
#                 if cv2.waitKey(1) & 0xFF == ord('q'):
#                     break
#     finally:
#         collector.stop()
#         collector.join()
#         camera.close_camera()
#         cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()


# app/datacollector/Camera.py

import numpy as np

class Camera_communication:
    def __init__(self):
        self.active = False
        self.image = self.generate_dummy_image()

    def create_camera(self):
        print("[카메라] 더미 카메라 연결됨 (테스트 모드)")
        self.active = True

    def get_image(self):
        # 이미지 1장 리턴
        return self.generate_dummy_image()

    def generate_dummy_image(self):
        # 1920 x 1200 그레이스케일 이미지 생성 (값: 평균 150, 노이즈 포함)
        dummy = np.random.normal(150, 25, (1920, 1200))
        dummy = np.clip(dummy, 0, 255).astype(np.uint8)
        return dummy
