import serial
import configparser
import time
import threading

class SensorthermPyrometer:
    def __init__(self, config_path="./config/sensortherm.ini"):
        self.connected = False
        self.data = {}
        self.lock = threading.Lock()
        self.running = False
        self.sample_rate = 100  # Hz

        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            self.adress = dict(config.items("adress"))

            self.serial = serial.Serial(
                port=self.adress['port'],
                baudrate=int(self.adress['baudrate']),
                parity=self.adress['parity'],
                stopbits=int(self.adress['stopbits']),
                bytesize=int(self.adress['bytesize']),
                timeout=int(self.adress['timeout'])
            )

            self.serial.write("00bum01\r".encode('ascii'))
            initial_response = self.serial.read_until(b'\r').decode().strip()

            if initial_response == 'ok':
                self.connected = True
                self.thread = threading.Thread(target=self.collect_loop, daemon=True)
                self.running = True
                self.thread.start()
                print("[Sensortherm] 연결 성공")
            else:
                print(f"[Sensortherm] 연결 실패: {initial_response}")

        except Exception as e:
            print("[Sensortherm] 초기화 실패:", e)

    def collect_loop(self):
        while self.running:
            start = time.perf_counter()

            try:
                self.serial.write("00bup\r".encode())
                response = self.serial.read_until(b'\r').decode().strip()
                if len(response) == 12:
                    with self.lock:
                        self.data['mpt'] = int(response[0:4], 16) / 10
                        self.data['1ct'] = int(response[4:8], 16) / 10
                        self.data['2ct'] = int(response[8:12], 16) / 10
            except Exception as e:
                print(f"[Sensortherm] 수집 실패: {e}")
                self.connected = False

            time.sleep(max(0, (1/self.sample_rate) - (time.perf_counter() - start)))

    def get_data(self):
        with self.lock:
            return self.data.copy() if self.data else None

    def stop(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
        print("[Sensortherm] 종료")
