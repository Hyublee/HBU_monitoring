import socket
import configparser
import threading
import time

class IPGLaser:
    def __init__(self, config_path="./config/ipg.ini"):
        self.connected = False
        self.data = {}
        self.lock = threading.Lock()
        self.running = False

        try:
            config = configparser.ConfigParser()
            config.read(config_path)
            ip = config.get("adress", "ip")
            port = int(config.get("adress", "port"))

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(1.0)
            self.sock.connect((ip, port))
            self.connected = True
            self.running = True
            self.thread = threading.Thread(target=self.collect_loop, daemon=True)
            self.thread.start()
            print("[IPG] 레이저 연결 성공")
        except Exception as e:
            print("[IPG] 연결 실패:", e)
            self.connected = False

    def collect_loop(self):
        while self.running:
            try:
                outpower = self._send_cmd("SOURce:POWer:OUTPut?")
                setpower = self._send_cmd("SOURce:POWer?")
                with self.lock:
                    self.data['outpower'] = float(outpower)
                    self.data['setpower'] = float(setpower)
            except Exception as e:
                print("[IPG] 데이터 수집 오류:", e)
                self.connected = False
            time.sleep(0.1)

    def _send_cmd(self, cmd):
        try:
            self.sock.send((cmd + "\n").encode())
            recv = self.sock.recv(1024).decode().strip()
            return recv
        except Exception as e:
            print(f"[IPG] 명령어 전송 오류 ({cmd}):", e)
            raise

    def get_data(self):
        with self.lock:
            return self.data.copy() if self.data else None

    def stop(self):
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except Exception as e:
            print("[IPG] 소켓 종료 오류:", e)
        print("[IPG] 수집 중지됨")
