
import json
import time
import board
import adafruit_dht

from datetime import datetime, timezone
from getpass import getpass
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# API 서버 설정
server = "http://172.20.10.8:8000"
plant_id = 1

# DHT11 센서 설정 (GPIO2)
dht_device = adafruit_dht.DHT11(board.D2)

try:
    # 1. 장비 업로드 토큰 입력
    token = getpass("장비 업로드 토큰: ")

    # 2. 센서 데이터 측정
    print("\nDHT11 센서 측정 시작")

    temperature = None
    humidity = None

    while temperature is None or humidity is None:
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity

            if temperature is not None and humidity is not None:
                print(f"온도: {temperature:.1f}°C")
                print(f"습도: {humidity:.1f}%")
                break

        except RuntimeError as error:
            print(f"측정 재시도: {error}")
            time.sleep(2)

    # 3. JSON 데이터 생성
    body = {
        "items": [{
            "plant_id": plant_id,
            "ts": datetime.now(timezone.utc).isoformat(),
            "air_temp_c": temperature,
            "rh_pct": humidity,
        }]
    }

    print("\n전송할 데이터:")
    print(json.dumps(body, indent=2, ensure_ascii=False))

    # 4. API 요청 생성
    request = Request(
        f"{server}/api/v1/ingest/sensor-readings",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    # 5. 서버로 데이터 전송
    print("\n서버로 데이터 전송 중...")

    try:
        with urlopen(request, timeout=30) as response:

            print(f"\nHTTP 상태 코드: {response.status}")
            print("서버 응답:", response.read().decode("utf-8"))

    except HTTPError as error:
        print(f"HTTP 오류: {error.code}")
        print(error.read().decode("utf-8"))

    except URLError as error:
        print("서버 연결 실패:", error.reason)

except KeyboardInterrupt:
    print("\n프로그램 종료")

finally:
    dht_device.exit()
    print("DHT11 센서 종료")

