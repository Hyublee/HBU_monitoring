'''
IPG laser 통신 및 좌표 데이터 수집 코드
Copyleft ⓒ Seonghun_ji
last update: 2024.09.03
Requirement package ()
'''
import socket
import configparser as conf
import time
from collections import deque
import threading


class IPG_communication:
    def __init__(self, config_path="./Monitoring/Sensors/ini_files/IPG.ini"):
        '''Inintializes the sensor and communication'''

        self.config = conf.ConfigParser()
        self.config.read(config_path)
        self.adress = {key: value for key, value in self.config.items('adress')}
        self.data = {key: value for key, value in self.config.items('data')}
        
        self.adress = str(self.ip['ip'])
        self.port = self.ip['port']

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        try:
            self.socket.connect((self.ip, self.port))
            self.activate = True
            print(f"Connected to IPG LASER at {self.ip}:{self.port}")
        except Exception as e:
            self.activate = False
            print(f"Failed to connect: {e}")

    def get_data(self):
        if self.activate:
            self.socket.sendall("ROP\r".encode('ascii'))    
            response = self.socket.recv(1024).decode('ascii').strip()
            outpower = response.split(':')[-1].strip()
            if outpower != 'OFF' or outpower != 'LOW':
                outpower = float(outpower)
            else:
                outpower = None

            self.socket.sendall("RCS\r".encode('ascii'))    
            response = self.socket.recv(1024).decode('ascii').strip()
            setpower = float(response.split(':')[-1].strip() * 1000)

            self.data['outpower'] = outpower
            self.data['setpower'] = setpower
        else:
            pass

        return self.data
    
    def close(self):
        if self.activate:
            self.activate = False
            self.socket.close()
        print("Connecntion closed.")

class IPG_DB:
    def __init__(self, max_size=100) -> None:
        self.data_queue = deque(maxlen=max_size)
    
    def store_data(self, data):
        self.data_queue.append(data)

    def retrieve_data(self):
        if self.data_queue:
            return self.data_queue[-1]
        return print("Test Data queue is empty")

class IPG_Collector(threading.Thread):
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
                data = self.com.get_data()
                if data:
                    self.db.store_data(data)
            else:
                time.sleep(0.5)
            sleep_time = max(0, (1/self.sample_rate)-(time.perf_counter()-loop_start))
            time.sleep(sleep_time)
        time.sleep(0.1)
    
    def stop(self):
        self.running = False
if __name__ =='__main__':
    com = IPG_communication()
    db = IPG_DB()
    collector = IPG_Collector(com, db)
    collector.start()

    try:
        while True:
            if db.data_queue:
                data = db.retrieve_data()
                print(data)
            
            time.sleep(1)
    except:
        print('Error')