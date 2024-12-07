from flask import Flask, jsonify, request
import pymysql
from if_mt_control_class import WindowControl

# Flask 앱 생성
app = Flask(__name__)

# 데이터베이스 연결 설정
db_config = {
    'host': '192.168.0.90',
    'user': 'root',
    'password': 'mypassword',
    'database': 'dina'
}

# 스텝 모터 설정
steps_per_revolution = 82  # 한 바퀴 회전에 필요한 스텝 수

# 창문 제어 객체 초기화
window_control = WindowControl(steps_per_revolution)

# 데이터베이스에서 마지막 창문 상태 가져오기
def get_last_window_state():
    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            cursor.execute("SELECT WindowState FROM choi ORDER BY timestamp DESC LIMIT 1")  # 수정된 열 이름
            result = cursor.fetchone()
        conn.close()
        return result[0] if result else "closed"
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return "closed"

# 데이터베이스에 창문 상태 기록
def update_window_state(state):
    try:
        conn = pymysql.connect(**db_config)  # DB 연결 설정
        with conn.cursor() as cursor:
            # 모든 행의 WindowState 값을 갱신
            cursor.execute("UPDATE choi SET WindowState = %s", (state,))
        conn.commit()
        conn.close()
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")


# 현재 창문 상태 조회
@app.route('/status', methods=['GET'])
def status():
    current_state = get_last_window_state()
    return jsonify({"message": f"Current window state is {current_state}."})

# 창문 열기
@app.route('/open', methods=['POST'])
def open_window():
    current_state = get_last_window_state()

    # 데이터베이스 상태 동기화
    if current_state != window_control.window_state:
        window_control.window_state = current_state

    if window_control.window_state == "open":
        return jsonify({"message": "Window is already open."}), 400

    window_control.open_window()  # 창문 열기 동작
    update_window_state("open")
    return jsonify({"message": "Window opened successfully."})

# 창문 닫기
@app.route('/close', methods=['POST'])
def close_window():
    current_state = get_last_window_state()

    # 데이터베이스 상태 동기화
    if current_state != window_control.window_state:
        window_control.window_state = current_state

    if window_control.window_state == "closed":
        return jsonify({"message": "Window is already closed."}), 400

    window_control.close_window()  # 창문 닫기 동작
    update_window_state("closed")
    return jsonify({"message": "Window closed successfully."})

# Flask 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
