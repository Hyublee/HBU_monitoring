# app/sensors/hxapi_client.py

import ctypes
import os
import configparser
import time
import threading

class CNCPosition:
    def __init__(self, config_path=os.path.abspath("./config/hxapi.ini")):
        self.connected = False
        self.data = {}
        self.lock = threading.Lock()
        self.running = False

        try:
            # INI 설정 읽기
            config = configparser.ConfigParser()
            config.read(config_path)
            ip = config.get("adress", "ip").split(".")
            port = int(config.get("adress", "port"))

            dll_path = os.path.abspath("./vendor/hxapi/dll/HXApi.dll")
            self.hx = ctypes.CDLL(dll_path)

            # 함수 시그니처 지정
            self.hx.HxInitialize2.argtypes = [ctypes.c_int32]*6
            self.hx.HxInitialize2.restype = ctypes.c_bool

            self.hx.HxGetSVF.argtypes = [ctypes.c_int32, ctypes.c_int32]
            self.hx.HxGetSVF.restype = ctypes.c_double

            self.hx.HxGetSNF.argtypes = [ctypes.c_int32, ctypes.c_int32]
            self.hx.HxGetSNF.restype = ctypes.c_double

            # 연결 시도
            result = self.hx.HxInitialize2(0, int(ip[0]), int(ip[1]), int(ip[2]), int(ip[3]), port)
            if result:
                self.connected = True
                self.running = True
                self.thread = threading.Thread(target=self.collect_loop, daemon=True)
                self.thread.start()
                print("[HXAPI] CNC 연결 성공")
            else:
                print("[HXAPI] CNC 연결 실패")

        except Exception as e:
            print("[HXAPI] 초기화 실패:", e)

    def collect_loop(self):
        while self.running:
            try:
                data = {}
                # 현재 위치
                data['curpos_x'] = self.hx.HxGetSVF(0, 83)
                data['curpos_y'] = self.hx.HxGetSVF(0, 84)
                data['curpos_z'] = self.hx.HxGetSVF(0, 85)
                data['curpos_a'] = self.hx.HxGetSVF(0, 86)
                data['curpos_c'] = self.hx.HxGetSVF(0, 87)

                # 기계 위치
                data['macpos_x'] = self.hx.HxGetSNF(0, 237)
                data['macpos_y'] = self.hx.HxGetSNF(0, 238)
                data['macpos_z'] = self.hx.HxGetSNF(0, 239)
                data['macpos_a'] = self.hx.HxGetSNF(0, 240)
                data['macpos_c'] = self.hx.HxGetSNF(0, 241)

                # 남은 거리
                data['rempos_x'] = self.hx.HxGetSNF(0, 247)
                data['rempos_y'] = self.hx.HxGetSNF(0, 248)
                data['rempos_z'] = self.hx.HxGetSNF(0, 249)
                data['rempos_a'] = self.hx.HxGetSNF(0, 250)
                data['rempos_c'] = self.hx.HxGetSNF(0, 251)

                # 피드/속도
                data['oper_time'] = self.hx.HxGetSNF(0, 0)
                data['total_oper_time'] = self.hx.HxGetSNF(0, 1)
                data['feed_override'] = self.hx.HxGetSVF(0, 675)
                data['rapid_override'] = self.hx.HxGetSVF(0, 676)
                data['feed_rate'] = self.hx.HxGetSVF(0, 722)

                with self.lock:
                    self.data = data

                time.sleep(0.1)  # 10Hz 수집
            except Exception as e:
                print("[HXAPI] 수집 오류:", e)
                self.connected = False
                break

    def get_data(self):
        with self.lock:
            return self.data.copy() if self.data else None

    def stop(self):
        self.running = False
        print("[HXAPI] 수집 중지됨")
