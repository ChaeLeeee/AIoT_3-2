
import json
import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt

from datetime import datetime, timezone

# MQTT Broker 설정
BROKER = "172.20.10.5"
PORT = 1883
TOPIC = "smartfarm/sensor/environment"

plant_id = 1

# DHT11 센서 설정 (GPIO2)
dht_device = adafruit_dht.DHT11(board.D2)

# MQTT Client 생성
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="raspberrypi_sensor_01"
)

try:
    # MQTT Broker 연결
    print("MQTT Broker 연결 중...")
    client.connect(BROKER, PORT, 60)
    client.loop_start()

    print("MQTT 연결 성공!")
    print(f"전송 Topic: {TOPIC}")

    while True:
        try:
            # 센서 데이터 측정
            temperature = dht_device.temperature
            humidity = dht_device.humidity

            if temperature is None or humidity is None:
                print("센서 측정 실패")
                time.sleep(2)
                continue

            print(f"\n온도: {temperature:.1f}°C")
            print(f"습도: {humidity:.1f}%")

            # JSON 데이터 생성
            body = {
                "items": [{
                    "plant_id": plant_id,
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "air_temp_c": temperature,
                    "rh_pct": humidity,
                }]
            }

            payload = json.dumps(body)

            # MQTT Publish
            result = client.publish(
                TOPIC,
                payload,
                qos=1
            )

            result.wait_for_publish(timeout=10)

            if result.is_published():
                print("MQTT 데이터 전송 성공!")
            else:
                print("MQTT 전송 확인 시간 초과")

            time.sleep(3)

        except RuntimeError as error:
            print(f"센서 측정 재시도: {error}")
            time.sleep(2)

except KeyboardInterrupt:
    print("\n프로그램 종료")

except Exception as error:
    print(f"MQTT 오류: {error}")

finally:
    client.loop_stop()
    client.disconnect()
    dht_device.exit()
    print("센서 및 MQTT 연결 종료")
