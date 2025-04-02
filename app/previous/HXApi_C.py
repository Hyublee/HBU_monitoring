'''
HXAPI 통신 및 좌표 데이터 수집 코드
'''

import ctypes
from ctypes import c_int, c_double, POINTER, byref
import os 
import time
import matplotlib.pyplot as plt

dll_path = "HXApi/dll"
os.environ['PATH'] = dll_path + os.pathsep + os.environ['PATH']

hxapi = ctypes.CDLL("HXAPI_py.dll")
# Connect 함수 설정
hxapi.Connect.restype = c_int
hxapi.Connect.argtypes = []

# GetPositions 함수 설정
hxapi.GetPositions.restype = None  # 반환 값이 없으므로 None으로 설정
hxapi.GetPositions.argtypes = [POINTER(c_double), POINTER(c_int)]

# Connect 함수 호출
if hxapi.Connect():
    print('Connection successful')
else:
    print('Connection failed')

# GetPositions 함수 호출
# 최대 좌표 수를 저장할 변수를 설정
max_positions = 5
positions = (c_double * max_positions)()  # 좌표를 저장할 배열 생성
size = c_int(max_positions)  # 배열의 크기를 저장할 변수


while True:
    hxapi.GetPositions(positions, byref(size))
    print(f"X : {positions[0]:.3f}")
    print(f"Y : {positions[1]:.3f}")
    print(f"Z : {positions[2]:.3f}")
    print(f"A : {positions[3]:.3f}")
    print(f"C : {positions[4]:.3f}\n")
    # plt.scatter(positions[0], positions[1],color='b')
    # plt.xlim([0,100])
    # plt.ylim([0,100])
    # plt.pause(0.1)
    time.sleep(0.5)
   

    # print(f"X : {positions[size.value[0]]}")
    # for i in range(size.value):
    #     print(f'Position {i}: {positions[i]}')