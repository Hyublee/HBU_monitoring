'''
HXAPI 통신 및 좌표 데이터 수집 코드
Copyleft ⓒ Seonghun_ji
last update: 2025. 02.17
Requirement package (HXApi)
'''
import configparser as conf
import random
import time
from collections import deque
import threading
import ctypes
import os
import sys

dll_path = "./Monitoring/Sensors/HXApi/dll"
os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']

class CNC_Communication:
    def __init__(self, config_path="./Monitoring/Sensors/ini_files/HXApi.ini") -> None:
        '''Inintializes the sensor and communication'''

        self.config = conf.ConfigParser()
        self.config.read(config_path)
        self.adress = {key: value for key, value in self.config.items('adress')}
        self.data = {key: value for key, value in self.config.items('data')}
        print(self.adress)
        self.api_types()
        self.open()

    def api_types(self):
        self.hx = ctypes.CDLL("./Monitoring/Sensors/HXApi/dll/HXApi.dll")

        self.HX_ETHERNET = 0
        self.HXRTX       = 1

        ############## hxapi 함수 타입 정의 ################
        self.hx.HxInitialize2.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.hx.HxInitialize2.restype = ctypes.c_bool

        self.hx.HxConnect.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.hx.HxConnect.restype = ctypes.c_bool

        self.hx.HxGetConnectState.argtypes = [ctypes.c_int32]
        self.hx.HxGetConnectState.restype = ctypes.c_bool

        self.hx.HxGetSVF.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.hx.HxGetSVF.restype = ctypes.c_double

        self.hx.HxGetSNF.argtypes = [ctypes.c_int32, ctypes.c_int32]
        self.hx.HxGetSNF.restype = ctypes.c_double

    def open(self): 
        # API 초기화 및 연결
        ip = self.adress['ip'].split('.')
        port = int(self.adress['port'])
        res = self.hx.HxInitialize2(0, int(ip[0]), int(ip[1]), int(ip[2]), int(ip[3]), port) # return bool
        if res:
            self.activate = True
            print(f"API 초기화 및 연결 성공: {res}") 
        else:
            self.activate = False
            print("HXApi 연결 실패")

    def get_pos_data(self):
        if self.activate:
            ## 현재 위치
            self.data['curpos_x'] = self.hx.HxGetSVF(0, 83)
            self.data['curpos_y'] = self.hx.HxGetSVF(0, 84)
            self.data['curpos_z'] = self.hx.HxGetSVF(0, 85)
            self.data['curpos_a'] = self.hx.HxGetSVF(0, 86)
            self.data['curpos_c'] = self.hx.HxGetSVF(0, 87)

            ## 기계 위치
            self.data['macpos_x'] = self.hx.HxGetSNF(0, 237)
            self.data['macpos_y'] = self.hx.HxGetSNF(0, 238)
            self.data['macpos_z'] = self.hx.HxGetSNF(0, 239)
            self.data['macpos_a'] = self.hx.HxGetSNF(0, 240)
            self.data['macpos_c'] = self.hx.HxGetSNF(0, 241)

            ## 남은거리
            self.data['rempos_x'] = self.hx.HxGetSNF(0, 247)
            self.data['rempos_y'] = self.hx.HxGetSNF(0, 248)
            self.data['rempos_z'] = self.hx.HxGetSNF(0, 249)
            self.data['rempos_a'] = self.hx.HxGetSNF(0, 250)
            self.data['rempos_c'] = self.hx.HxGetSNF(0, 251)

            self.data['oper_time']       = self.hx.HxGetSNF(0, 0)
            self.data['total_oper_time'] = self.hx.HxGetSNF(0, 1)
            self.data['feed_override']   =  self.hx.HxGetSVF(0, 675)
            self.data['rapid_override']  =  self.hx.HxGetSVF(0, 676)
            self.data['feed_rate']    = self.hx.HxGetSVF(0, 722)

        return self.data
    
    def close(self):
        self.activate = False
    
class CNC_DB:
    def __init__(self, max_size=100) -> None:
        self.data_queue = deque(maxlen=max_size)
    
    def store_data(self, data):
        self.data_queue.append(data)

    def retrieve_data(self):
        if self.data_queue:
            return self.data_queue[-1]
        return print("Test Data queue is empty")

class CNC_Collector(threading.Thread):
    def __init__(self, com, db):
        threading.Thread.__init__(self)
        self.com = com
        self.db = db
        self.running = True
        self.sample_rate = 100

    def run(self):
        while self.running:
            loop_start = time.perf_counter()
            if self.com.activate:
                data = self.com.get_pos_data()
                if data:
                    self.db.store_data(data)
            else:
                time.sleep(0.5)
            sleep_time = max(0, (1/self.sample_rate)-(time.perf_counter()-loop_start))
            time.sleep(sleep_time)
        time.sleep(0.1)
    
    def stop(self):
        self.running = False
        self.active = False

if __name__ == "__main__":
    # data = {}
    # while True:
    #     data = {'key1': 1,
    #             'key2': 2}
    #     print(data)
        # time.sleep(1)

    com = CNC_Communication()
    db = CNC_DB()
    collector = CNC_Collector(com, db)
    collector.start()
        
    try:
        while True:
            if db.data_queue:
                data = db.retrieve_data()
                print(data)
                # sys.stdout.flush()
            
            time.sleep(0.01)
    except:
        print('Error')

