import socket
import time
from threading import Thread

class Autotracking():
    def __init__(self):
        host = '127.0.0.1'
        port = 8123
        self.sample_rate = 100
        # socket_AF_INET: 주소 종류 지정(IP), socket.SOCK_STREAM: 통신종류 지정(UDP, TCP)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        print('run')
        # 예외 및 연결 상태 확인 코드 추가 필요

    def start_get_data(self):
        print('start')
        Thread(target=self.get_data, daemon=True).start()

    def get_data(self):
        # self.is_running = True
        # while self.is_running:
        data = self.client.recv(100)
        data = data.decode()
        print(data)
            
        
    def data_processing(self):
        pass

    def close_socket(self):
        self.client.close()

if __name__ =='__main__':
    a = Autotracking()
    while True:
        a.get_data()
        time.sleep(1/5)
    # a.start_get_data()


