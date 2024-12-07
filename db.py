import time
import pymysql
from temp_class import BME280Sensor
from wind_class import WindDirectionSensor
from rain_class import RainSensor
from usb_serial_class import USBSerial  # USBSerial 클래스 가져오기
from wind_speed_class import WindSpeedSensor  # WindSpeedSensor 클래스 가져오기

# 데이터베이스 연결 함수
def sql_connect():
    return pymysql.connect(
        host='192.168.0.90',  # 새로운 호스트
        user='root',
        password='mypassword',  # 새로운 비밀번호
        db='dina',  # 새로운 데이터베이스 이름
        charset='utf8'
    )

# 중복 데이터 확인 함수
def is_duplicate(conn, data):
    cur = conn.cursor()
    sql = """
        SELECT COUNT(*) FROM choi
        WHERE Temperature = %s AND Humidity = %s AND Pressure = %s AND WindDirection = %s AND WindSpeed = %s AND Rainfall = %s AND Dust = %s
    """
    cur.execute(sql, data)
    return cur.fetchone()[0] > 0

# 데이터 삽입 함수 (window_state 추가)
def insert_data(conn, data, window_state):
    cur = conn.cursor()
    sql = """
        INSERT INTO choi (Temperature, Humidity, Pressure, WindDirection, WindSpeed, Rainfall, Dust, WindowState)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(sql, data + (window_state,))
    conn.commit()

def main():
    # Initialize sensors
    bme280 = BME280Sensor(measured_pressure=1018.0, target_altitude=15.0, temperature_celsius=25.0)
    wind_sensor = WindDirectionSensor(json_file_path="wind_direction.json")
    rain_sensor = RainSensor(pin=6)
    wind_speed_sensor = WindSpeedSensor(wind_pin=17, radius_cm=9.0, adjustment=2.0, wind_interval=5)  # WindSpeedSensor 초기화
    # Initialize USB Serial
    usb_serial = USBSerial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
    # 이전 데이터 저장 변수 (이상치 검출용)
    last_values = None
    try:
        # Open the USB serial port
        usb_serial.open()
        while True:
            try:
                # 센서 데이터 읽기
                temperature = round(bme280.read_temperature(), 2)
                humidity = round(bme280.read_humidity(), 2)
                pressure = round(bme280.read_pressure(), 2)
                wind_direction = wind_sensor.get_direction()  # 방향값 읽기
                wind_speed = round(wind_speed_sensor.measure_wind_speed(), 2)  # 풍속 측정
                rainfall = round(rain_sensor.get_rainfall(), 2)
                # USB 데이터 읽기
                dust_data = usb_serial.receive()
                # USB 데이터가 없을 경우 처리
                if dust_data is None or not dust_data.isdigit():
                    continue
                # Convert dust data to integer
                dust = int(dust_data)
                # 데이터 유효성 검사
                if not (0 <= temperature <= 100):
                    print(f"Invalid temperature value: {temperature}")
                    continue
                if not (0 <= humidity <= 100):
                    print(f"Invalid humidity value: {humidity}")
                    continue
                if not (900 <= pressure <= 1100):  # Typical pressure range in hPa
                    print(f"Invalid pressure value: {pressure}")
                    continue
                if not (0 <= wind_speed <= 200):  # Typical wind speed range in km/h
                    print(f"Invalid wind speed value: {wind_speed}")
                    continue
                if not (0 <= rainfall):
                    print(f"Invalid rainfall value: {rainfall}")
                    continue
                if not (-1000 <= dust <= 1000):  # Assuming a valid dust range (adjust if needed)
                    print(f"Invalid dust value: {dust}")
                    continue
                # 이상치 검출
                if last_values:
                    if abs(temperature - last_values[0]) > 20:
                        print(f"Temperature anomaly detected: {temperature}")
                        continue
                last_values = (temperature, humidity, pressure, wind_direction, wind_speed, rainfall, dust)

                # 창문 상태 결정 (dust 값이 5를 초과하면 open, 아니면 closed)
                window_state = 'open' if dust > 5 else 'closed'

                # 데이터베이스 연결
                conn = sql_connect()
                # 중복 데이터 확인
                if is_duplicate(conn, (temperature, humidity, pressure, wind_direction, wind_speed, rainfall, dust)):
                    print("Duplicate data, skipping insertion")
                    conn.close()
                    continue

                # 데이터 삽입
                print("Inserting data:", (temperature, humidity, pressure, wind_direction, wind_speed, rainfall, dust, window_state))
                insert_data(conn, (temperature, humidity, pressure, wind_direction, wind_speed, rainfall, dust), window_state)
                conn.close()
                print("Connection closed")

                # Delay to prevent rapid polling
                time.sleep(1)
            except Exception as e:
                print(f"Error: {e}")
    finally:
        # Cleanup
        usb_serial.close()
        wind_speed_sensor.cleanup()

if __name__ == "__main__":
    main()
