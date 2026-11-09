from picamera2 import Picamera2
from datetime import datetime
from pathlib import Path
import time

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parents[1]

# 사진 저장 폴더
IMAGE_DIR = BASE_DIR / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

def capture_image():
    camera = Picamera2()

    try:
        config = camera.create_still_configuration()
        camera.configure(config)

        camera.start()
        time.sleep(2)

        filename = datetime.now().strftime(
            "plant_%Y%m%d_%H%M%S.jpg"
        )

        image_path = IMAGE_DIR / filename

        camera.capture_file(str(image_path))

        print(f"촬영 완료: {image_path}")

    finally:
        camera.stop()

if __name__ == "__main__":
    capture_image()
