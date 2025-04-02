'''
HXAPI 통신 및 좌표 데이터 수집 코드
Copyleft ⓒ Seonghun_ji
last update: 2024.04.12
Requirement package (nidaqmx)
'''
import ctypes
import os
dll_path = "./Monitoring/Sensors/HXApi/dll"
os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']

hxapi = ctypes.CDLL("./Monitoring/Sensors/HXApi/dll/HXApi.dll")

class HX_ComType():
    HX_ETHERNET = 0
    HXRTX       = 1

############## hxapi 함수 타입 정의 ################
hxapi.HxInitialize2.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
hxapi.HxInitialize2.restype = ctypes.c_bool

hxapi.HxConnect.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
hxapi.HxConnect.restype = ctypes.c_bool

hxapi.HxGetConnectState.argtypes = [ctypes.c_int32]
hxapi.HxGetConnectState.restype = ctypes.c_bool

hxapi.HxGetSVF.argtypes = [ctypes.c_int32, ctypes.c_int32]
hxapi.HxGetSVF.restype = ctypes.c_double

# API 초기화 및 연결
res = hxapi.HxInitialize2(HX_ComType.HX_ETHERNET, 169, 254, 41, 99, 3000) # return bool
if res:
    print(f"API 초기화 및 연결 성공: {res}")

else:
    print("Check connect state")

## hx api tester MFC 15 page 참조

## 현재 위치
curpos_x = hxapi.HxGetSVF(0, 83)
curpos_y = hxapi.HxGetSVF(0, 84)
curpos_z = hxapi.HxGetSVF(0, 85)
curpos_a = hxapi.HxGetSVF(0, 86)
curpos_c = hxapi.HxGetSVF(0, 87)

# ## 기계 위치
# macpos_x = hxapi.HxGetSNF(0, 237)
# macpos_y = hxapi.HxGetSNF(0, 238)
# macpos_z = hxapi.HxGetSNF(0, 239)
# macpos_a = hxapi.HxGetSNF(0, 240)
# macpos_c = hxapi.HxGetSNF(0, 241)

# ## 상대 위치
# relpos_x = hxapi.HxGetSNF(0, 269)
# relpos_y = hxapi.HxGetSNF(0, 270)
# relpos_z = hxapi.HxGetSNF(0, 271)
# relpos_a = hxapi.HxGetSNF(0, 272)
# relpos_c = hxapi.HxGetSNF(0, 273)

# ## 남은거리
# dispos_x = hxapi.HxGetSNF(0, 247)
# dispos_y = hxapi.HxGetSNF(0, 248)
# dispos_z = hxapi.HxGetSNF(0, 249)
# dispos_a = hxapi.HxGetSNF(0, 250)
# dispos_c = hxapi.HxGetSNF(0, 251)

print(f"현재위치\n")
print(f"X : {curpos_x:.3f}")
print(f"Y : {curpos_y:.3f}")
print(f"Z : {curpos_z:.3f}")
print(f"A : {curpos_a:.3f}")
print(f"C : {curpos_c:.3f}")
