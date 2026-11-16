
import json
import paho.mqtt.client as mqtt

from getpass import getpass
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# MQTT 설정
BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "smartfarm/sensor/environment"

# FastAPI 서버 설정
SERVER = "http://172.20.10.8:8000"
API_URL = f"{SERVER}/api/v1/ingest/sensor-readings"

# 장비 업로드 토큰 입력
TOKEN = getpass("장비 업로드 토큰: ")

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("MQTT Broker 연결 성공!")
        client.subscribe(TOPIC, qos=1)
        print(f"구독 Topic: {TOPIC}")
        print("센서 데이터 수신 대기 중...")
    else:
        print(f"MQTT 연결 실패: {reason_code}")


def on_message(client, userdata, msg):
    try:
        # MQTT 메시지 수신
        data = json.loads(msg.payload.decode("utf-8"))

        print("\n===== MQTT 센서 데이터 수신 =====")
        print(json.dumps(data, indent=4, ensure_ascii=False))

        # 기존 HTTP API 요청 생성
        request = Request(
            API_URL,
            data=json.dumps(data).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {TOKEN}",
            },
            method="POST",
        )

        # FastAPI 서버로 전송
        print("\nFastAPI 서버로 데이터 전송 중...")

        try:
            with urlopen(request, timeout=30) as response:
                print(f"HTTP 상태 코드: {response.status}")
                print("서버 응답:", response.read().decode("utf-8"))
                print("DB 저장 요청 완료!")

        except HTTPError as error:
            print(f"HTTP 오류: {error.code}")
            print(error.read().decode("utf-8"))

        except URLError as error:
            print("서버 연결 실패:", error.reason)

    except json.JSONDecodeError:
        print("MQTT JSON 데이터 형식 오류")


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="laptop_subscriber"
)

client.on_connect = on_connect
client.on_message = on_message

try:
    print("MQTT Subscriber 실행 중...")
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

except KeyboardInterrupt:
    print("\nSubscriber 종료")

except Exception as error:
    print(f"오류 발생: {error}")

finally:
    client.disconnect()
