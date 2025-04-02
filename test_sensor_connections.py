from app.sensors.optris_client import OptrisCamera
from app.sensors.sensortherm_client import SensorthermPyrometer
from app.sensors.hxapi_client import CNCPosition
from app.sensors.ipg_client import IPGLaser

def test_sensor_connection(sensor_class, name):
    try:
        sensor = sensor_class()
        if hasattr(sensor, "connected") and sensor.connected:
            print(f"[{name}] 연결 성공")
        else:
            print(f"[{name}] 연결 실패")
    except Exception as e:
        print(f"[{name}] 예외 발생: {e}")

if __name__ == "__main__":
    print("🔍 센서 연결 상태 테스트 시작")
    test_sensor_connection(OptrisCamera, "Optris")
    test_sensor_connection(SensorthermPyrometer, "Sensortherm")
    test_sensor_connection(CNCPosition, "HXAPI")
    test_sensor_connection(IPGLaser, "IPG")
