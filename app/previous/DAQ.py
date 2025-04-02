'''
DAQ Communication    
Copyleft ⓒ Seonghun_ji
last update: 2024.04.12
Requirement package (nidaqmx)
'''
import nidaqmx
from nidaqmx.constants import AcquisitionType, Edge
import numpy as np
import matplotlib.pyplot as plt
import time
import threading
import multiprocessing as mp

class DAQ():
    def __init__(self): 
        # # self.task = nidaqmx.Task()
        # # self.task.ai_channels.add_ai_voltage_chan("Dev2/ai0:2")
        # # # self.task.timing.cfg_samp_clk_timing(rate=100, active_edge=Edge.RISING, sample_mode=AcquisitionType.HW_TIMED_SINGLE_POINT)
        # # self.task.start()
        pass

    def get_data(self):
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(channel)
            return self.task.read(number_of_samples_per_channel=1)

    def dis_conn(self):
        self.task.stop()
        self.task.close()   

    def data_collector(self, channel):
        self.data = []
        self.loop_time = []
        self.cnt = 0
        target_sample_rate = 100 # Hz
        target_delay = 1/ target_sample_rate

        while True:
            loop_time = time.time()
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(channel)
                voltage = task.read(number_of_samples_per_channel=1)

            if len(self.data) < 5000:
                self.data.append(voltage)
            else:
                self.data = self.data[1:]

            wait_time = target_delay-(time.time()-loop_time)

            if len(self.loop_time) < 5000:
                self.loop_time.append(wait_time)
            else:
                self.loop_time = self.loop_time[1:]

            if wait_time >= 0:      # case2
                time.sleep(wait_time/1000)
                print(f"remained time:{abs(wait_time*1000):.3f} ms")
            else:
                self.cnt += 1
                print(f"---------Over time:{abs(wait_time*1000):.3f} ms---------")



if __name__ == '__main__':
    '''
    3 channel voltage value real time acquisition
    sample rate: 100 Hz
    해결방법, 병렬처리, 스케줄러(import sched)
    '''
    daq = DAQ()
    channel = ["Dev2/ai0:2"]

    threading.Thread(target=daq.data_collector, args=(channel), daemon=True).start()
    
    fig = plt.figure(figsize=(10,8))
    start = time.time()
    while True:
        data = daq.data
        print(f"\nelapsed time: {time.time()-start:.2f} | data lenght:{len(daq.loop_time)} | over time count:{daq.cnt}")
        if len(daq.data) > 0 :
            ch0 = [data[i][0] for i in range(len(data))]
            ch1 = [data[i][1] for i in range(len(data))]
            ch2 = [data[i][2] for i in range(len(data))]
            plt.plot(ch0, color='red', label="ch0")
            plt.plot(ch1, color='blue', label="ch1")
            plt.plot(ch2, color='g', label="ch2")
            plt.plot(daq.loop_time, color='black', label="loop time")
            plt.title("DAQ data")
            plt.xlabel("Index")
            plt.ylabel("Voltage(V)")
            plt.legend()
            plt.pause(1)
            plt.gca().cla()
        