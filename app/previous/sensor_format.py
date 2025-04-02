import configparser as conf
import random
import time
from collections import deque
import threading


class Communication:
    def __init__(self, config_path="./Monitoring/Sensors/ini_files/.ini") -> None:
        '''Inintializes the sensor and communication'''

        # self.config = conf.ConfigParser()
        # self.config.read(config_path)
        # self.data = {key: value for key, value in self.config.items('name')}
        self.data = {'test':None}

        self.open()

    def open(self):
        self.activate = True

    def get_data(self):
        self.data['test'] = random.randint(0,10)

        return self.data
    
    def close(self):
        self.activate = False
    
class DB:
    def __init__(self, max_size=100) -> None:
        self.data_queue = deque(maxlen=max_size)
    
    def store_data(self, data):
        self.data_queue.append(data)

    def retrieve_data(self):
        if self.data_queue:
            return self.data_queue[-1]
        return print("Test Data queue is empty")

class Collector(threading.Thread):
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

if __name__ == "__main__":
    com = Communication()
    db = DB()
    collector = Collector(com, db)
    collector.start()

    try:
        while True:
            if db.data_queue:
                data = db.retrieve_data()
                print(data)
            
            time.sleep(1)
    except:
        print('Error')