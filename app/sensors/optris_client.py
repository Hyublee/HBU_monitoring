import os
import ctypes
import time
import threading

class OptrisCamera:
    def __init__(self, dll_path=os.path.abspath("./vendor/optris/ImagerIPC.dll")):
        self.connected = False
        self.running = False
        self.lock = threading.Lock()
        self.temperature_data = None

        try:
            self.dll = ctypes.WinDLL(dll_path)

            # 함수 예시 시그니처 (구체적 함수명/인자 수정 필요)
            # self.dll.InitializeCamera.restype = ctypes.c_bool

            # 예: 연결 시도
            # result = self.dll.InitializeCamera()
            # if result:
            self.connected = True
            self.running = True
            self.thread = threading.Thread(target=self.capture_loop, daemon=True)
            self.thread.start()
            print("[OptrisCamera] 연결 성공")
            # else:
            #     print("[OptrisCamera] 연결 실패")

        except Exception as e:
            print("[OptrisCamera] DLL 로딩 실패:", e)

    def capture_loop(self):
        while self.running:
            try:
                # 임시 데이터 (실제 SDK 함수 호출 필요)
                with self.lock:
                    self.temperature_data = {
                        'center_temp': 750.0 + (time.time() % 5),  # 시뮬레이션 값
                        'max_temp': 800.0
                    }
                time.sleep(0.1)
            except Exception as e:
                print("[OptrisCamera] 캡처 오류:", e)
                self.connected = False
                break

    def get_data(self):
        with self.lock:
            return self.temperature_data.copy() if self.temperature_data else None

    def stop(self):
        self.running = False
        print("[OptrisCamera] 수집 중지됨")
