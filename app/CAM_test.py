import ctypes
import numpy as np
import time
import os, sys

# Python 실행 환경 확인
is_64bit = os.environ['PROCESSOR_ARCHITECTURE'] == 'AMD64'

# 환경 변수 PATH에 추가 (Python이 실행될 때 DLL을 찾도록 설정)
DLL_DIR = "C:/Program Files (x86)/Optris GmbH/PIX Connect/Connect SDK/Lib/v120"
os.environ["PATH"] = DLL_DIR + os.pathsep + os.environ["PATH"]
sys.path.append(DLL_DIR)

# PIX Connect SDK의 DLL 경로 설정
DLL_FILE = "ImagerIPC2x64.dll" if is_64bit else "ImagerIPC2.dll"
DLL_PATH = os.path.join(DLL_DIR, DLL_FILE)

# DLL 파일이 존재하는지 확인
if not os.path.exists(DLL_PATH):
    print(f"❌ DLL 파일을 찾을 수 없습니다: {DLL_PATH}")
else:
    print(f"✅ DLL 파일이 존재합니다: {DLL_PATH}")

# DLL 로드 시도
try:
    pix_sdk = ctypes.CDLL(DLL_PATH)
    print("✅ DLL 로드 성공!")
except Exception as e:
    print(f"❌ DLL 로드 실패: {e}")
    
# 함수 반환값 및 인수 정의
pix_sdk.SetImagerIPCCount.argtypes = [ctypes.c_ushort]
pix_sdk.SetImagerIPCCount.restype = ctypes.c_long

pix_sdk.InitImagerIPC.argtypes = [ctypes.c_ushort]
pix_sdk.InitImagerIPC.restype = ctypes.c_long

pix_sdk.GetTempTarget.argtypes = [ctypes.c_ushort]
pix_sdk.GetTempTarget.restype = ctypes.c_float

pix_sdk.GetIPCState.argtypes = [ctypes.c_ushort]
pix_sdk.GetIPCState.restype = ctypes.c_long

# 1. 카메라 인스턴스 설정
res = pix_sdk.SetImagerIPCCount(1)
print("🔄 카메라 초기화 중...")
# 2. 카메라 초기화
init_result = pix_sdk.InitImagerIPC(0)
time.sleep(2)
state = pix_sdk.GetIPCState(0)
print(f"📌 현재 IPC 상태: {state}")
if init_result != 0:
    print(f"❌ 카메라 초기화 실패! (코드: {init_result})")
    sys.exit(1)
print("✅ 카메라 초기화 성공!")

# 3. 카메라 실행
print("🔄 카메라 실행 중...")
run_result = pix_sdk.RunImagerIPC(0)
if run_result != 0:
    print(f"❌ 카메라 실행 실패! (코드: {run_result})")
    sys.exit(1)
print("✅ 카메라 실행 성공!")

# 4. 카메라 상태 확인 (초기화 완료 여부)
print("🔍 카메라 상태 확인 중...")
for i in range(10):
    state = pix_sdk.GetIPCState(0, True)
    if state & 0x01:  # IPC_EVENT_INIT_COMPLETED 비트 체크
        print("✅ 카메라 정상 작동 중!")
        break
    time.sleep(1)
else:
    print("⚠️ 카메라 상태 확인 실패! 정상적으로 실행되지 않을 수 있음.")

# 5. 온도 데이터 가져오기
temperature = pix_sdk.GetTempTarget(0)
if temperature == -100.0:
    print("❌ 온도 데이터 읽기 실패!")
else:
    print(f"🌡️ 현재 대상 온도: {temperature:.2f}°C")