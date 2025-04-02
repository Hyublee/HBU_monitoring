import time
from datetime import datetime
from threading import Thread
import numpy as np
import pandas as pd
import os
import configparser

from app.sensors.optris_client import OptrisCamera
from app.sensors.sensortherm_client import SensorthermPyrometer
from app.sensors.hxapi_client import CNCPosition
from app.sensors.ipg_client import IPGLaser


class DataCollector:
    def __init__(self, main):
        self.main = main
        self.sample_rate = 50
        self.is_running = False
        self.is_saving = False

        # 센서 연결
        self.cam = OptrisCamera()
        self.pyro = SensorthermPyrometer()
        self.cnc = CNCPosition()
        self.ipg = IPGLaser()

        self.config_data = self.load_config_keys()
        self.initialize_data_storage_list()

    def load_config_keys(self, config_path="./config/main.ini"):
        config = configparser.ConfigParser()
        config.read(config_path)
        cnc_keys = config['cnc'] if 'cnc' in config else {}
        ipg_keys = config['ipg'] if 'ipg' in config else {}
        pyro_keys = config['pyro'] if 'pyro' in config else {}
        camera_keys = config['camera'] if 'camera' in config else {}
        return {'cnc': cnc_keys, 'ipg': ipg_keys, 'pyro': pyro_keys, 'camera': camera_keys}

    def initialize_data_storage_list(self):
        self.data_storage = {'time': [], '_t': []}
        for key_group in self.config_data.values():
            for key in key_group:
                self.data_storage[key] = []

    def start_threads(self):
        self.is_running = True
        Thread(target=self.collect_and_merge_data_list, daemon=True).start()

    def stop_threads(self):
        self.is_running = False
        self.cam.stop()
        self.pyro.stop()
        self.cnc.stop()
        self.ipg.stop()

    def collect_and_merge_data_list(self):
        start_time = time.perf_counter()

        while self.is_running:
            loop_start_time = time.perf_counter()
            elapsed_time = round(time.perf_counter() - start_time, 3)
            current_time = str(datetime.now().strftime("%H_%M_%S_%f")[:-3])

            new_data = {'time': current_time, '_t': elapsed_time}

            # 센서별 데이터 수집
            if self.cnc.connected:
                cnc_data = self.cnc.get_data()
                if cnc_data:
                    new_data.update(cnc_data)

            if self.ipg.connected:
                ipg_data = self.ipg.get_data()
                if ipg_data:
                    new_data.update(ipg_data)

            if self.pyro.connected:
                pyro_data = self.pyro.get_data()
                if pyro_data:
                    new_data.update(pyro_data)

            if self.cam.connected:
                cam_data = self.cam.get_data()
                if cam_data:
                    new_data['image'] = np.random.randint(0, 255, (1920, 1200), dtype=np.uint8)
                    new_data.update(cam_data)

            self.update_data_storage_list(new_data)
            sleep_time = max(0, (1 / self.sample_rate) - (time.perf_counter() - loop_start_time))
            time.sleep(sleep_time)

    def update_data_storage_list(self, new_data):
        for key, value in new_data.items():
            if isinstance(self.data_storage.get(key), list):
                if len(self.data_storage[key]) >= 5000:
                    self.data_storage[key].pop(0)
                self.data_storage[key].append(value)
            else:
                self.data_storage[key] = value

    def save(self):
        start_time = datetime.now()
        file_name = str(start_time.strftime("%Y%m%d%H%M%S"))
        folder_path = self.main.folder_path if hasattr(self.main, 'folder_path') else None

        if folder_path:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file_path = os.path.join(folder_path, f"{file_name}.csv")

            while self.main.is_saving:
                loop_start_time = time.perf_counter()
                current_time = datetime.now()
                time_difference = current_time - start_time

                if time_difference >= pd.Timedelta(hours=1):
                    file_path = os.path.join(folder_path, f"{current_time.strftime('%Y%m%d%H%M%S')}.csv")
                    start_time = current_time

                data_to_save = {k: v[-1] if isinstance(v, list) else v for k, v in self.data_storage.items()}
                df = pd.DataFrame([data_to_save])
                selected_cols = ['time', 'curpos_x', 'curpos_y', 'curpos_z', 'curpos_a', 'curpos_c', 'mpt', 'melt_pool_area', 'outpower']
                df = df[selected_cols] if all(c in df.columns for c in selected_cols) else df

                if os.path.exists(file_path):
                    df.to_csv(file_path, header=False, index=False, mode='a')
                else:
                    df.to_csv(file_path, header=True, index=False, mode='w')

                sleep_time = max(0, (1 / 30) - (time.perf_counter() - loop_start_time))
                time.sleep(sleep_time)



    def update_ui_sensor_status(self):
        self.main.ui.label_cnc_status.setText("연결됨" if self.cnc.connected else "끊김")
        self.main.ui.label_cnc_status.setStyleSheet("color: green;" if self.cnc.connected else "color: red;")

        self.main.ui.label_ipg_status.setText("연결됨" if self.ipg.connected else "끊김")
        self.main.ui.label_ipg_status.setStyleSheet("color: green;" if self.ipg.connected else "color: red;")

        self.main.ui.label_pyro_status.setText("연결됨" if self.pyro.connected else "끊김")
        self.main.ui.label_pyro_status.setStyleSheet("color: green;" if self.pyro.connected else "color: red;")

        self.main.ui.label_cam_status.setText("연결됨" if self.cam.connected else "끊김")
        self.main.ui.label_cam_status.setStyleSheet("color: green;" if self.cam.connected else "color: red;")
