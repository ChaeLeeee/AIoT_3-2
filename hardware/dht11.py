import time
import board
import adafruit_dht

# DHT11 센서 설정: 물리 핀 3번 = GPIO2
dht_device = adafruit_dht.DHT11(board.D2)

try:
    while True:
        try:
            temperature = dht_device.temperature
            humidity = dht_device.humidity

            if temperature is not None and humidity is not None:
                print(f"온도: {temperature:.1f}°C")
                print(f"습도: {humidity:.1f}%")
                print("-" * 30)

        except RuntimeError as error:
            print(f"측정 재시도: {error}")

        time.sleep(2)

except KeyboardInterrupt:
    print("\n측정 종료")

finally:
    dht_device.exit()
