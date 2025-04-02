'''
Pyrometer 통신 및 데이터 수집 코드
Copyleft ⓒ Seonghun_ji
last update: 2024.09.03
Requirement package (?)
'''
# import serial
# import time

# ser = serial.Serial(
#                     port='COM8',
#                     baudrate=115200,
#                     parity='E',
#                     stopbits=1,
#                     bytesize=8,
#                     timeout=8)


# while 1:
#     loop_start= time.perf_counter()
#     cmd = "01mw0\r"
#     cmd = str.encode(cmd)
#     ser.write(cmd)
#     #print(f"Write Command: {cmd}")
   

#     data = ser.read(5)      #(4바이트 데이터 + 1바이트 \r)
#     #print(f"Response (raw): {data}")
#     data = data.decode("utf-8").strip() # 응답 데이터에서 \r 제거
#     temp_celsius = int(data, 16) / 10  # 16진수를 10진수로 변환, 1/10로 나눔 (매뉴얼 48P) 
#     #print(f"Response (Celsius): {temp_celsius} °C")
#     print(time.perf_counter()-loop_start)
        
    


import serial
import time

ser = serial.Serial(
                    port='COM8',
                    baudrate=115200,
                    parity='E',
                    stopbits=1,
                    bytesize=8,
                    timeout=8)
    
  
    
    # 버퍼 모드 설정 (Buffer mode 01)
cmd = "01bum01\r"  # 버퍼 모드 01 설정
ser.write(cmd.encode())

initial_response = ser.read_until(b'\r')  # OK\r을 읽음
print(f"Initial Response (OK): {initial_response.decode('utf-8').strip()}")  # 'OK' 출력
while True:
    loop_start= time.perf_counter()
    # 버퍼 데이터 읽기 명령어 전송
    cmd = "01bup\r"  # 현재 버퍼 패킷 읽기
    ser.write(cmd.encode())
   

    # 캐리지 리턴(\r) 기준으로 데이터 읽기
    data = ser.read_until(b'\r')  # \r까지 읽음
    data = data.decode("utf-8").strip()  # 캐리지 리턴 제거
    #print(f"Response (cleaned): {data}")
    #print(f"Response length (without CR): {len(data)} bytes")  # 응답 길이 출력 (캐리지 리턴 제외)

    # 데이터 처리 (2컬러, 채널 1, 채널 2 온도)
    if len(data) == 12:  # '\r'을 제거한 후 12바이트여야 함
        # 각 바이트를 16진수로 변환하여 온도 계산 (엔디안 처리 없이 직접 계산)
        temp_2color = int(data[0:4], 16) / 10   # 2컬러 온도 (AAAA)
        temp_channel1 = int(data[4:8], 16) / 10 # 채널 1 온도 (BBBB)
        temp_channel2 = int(data[8:12], 16) / 10 # 채널 2 온도 (CCCC)
            
        #print(f"2컬러 온도: {temp_2color} °C")
        #print(f"채널 1 온도: {temp_channel1} °C")
        #print(f"채널 2 온도: {temp_channel2} °C")
        print(time.perf_counter()-loop_start)
    else:
        print("잘못된 응답 크기: ", data)




