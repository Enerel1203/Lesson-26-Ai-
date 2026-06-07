import time
import requests
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from config import HF_API_KEY

MODELS = [
    "ByteDance/SDXL-Lightning",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0",
]

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Accept": "image/png"
}

def generate_image_from_text(prompt):
    payload = {"inputs": prompt}
    last_err = None

    for model in MODELS:
        url = f"https://api-inference.huggingface.co/models/{model}"

        for _ in range(3):
            r = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            ct = (r.headers.get("Content-Type") or "").lower()

            if r.status_code == 503:
                time.sleep(5)
                continue

            if r.status_code == 200 and "image" in ct:
                return Image.open(BytesIO(r.content))

            last_err = f"Request failed with status code {r.status_code}: {r.text}"

    raise Exception(last_err or "Image generation failed.")

def create_daylight_edition(image):
    daylight = image.copy()
    daylight = ImageEnhance.Brightness(daylight).enhance(1.4)
    daylight = ImageEnhance.Contrast(daylight).enhance(0.9)
    daylight = daylight.filter(ImageFilter.GaussianBlur(radius=2))
    return daylight

def create_night_mood(image):
    night = image.copy()
    night = ImageEnhance.Brightness(night).enhance(0.85)
    night = ImageEnhance.Contrast(night).enhance(1.5)
    night = night.filter(ImageFilter.GaussianBlur(radius=1))
    return night

def main():
    print("Welcome to the AI Image Mood Studio!")
    print("Type 'exit' to quit.\n")

    while True:
        prompt = input("Enter a text prompt: ").strip()

        if prompt.lower() == "exit":
            break

        try:
            print("Generating image...")
            image = generate_image_from_text(prompt)

            print("Creating Daylight Edition...")
            daylight = create_daylight_edition(image)

            print("Creating Night Mood version...")
            night = create_night_mood(image)

            file_name = input("Enter a base file name: ").strip()

            image.save(f"{file_name}_original.png")
            daylight.save(f"{file_name}_daylight.png")
            night.save(f"{file_name}_night.png")

            print(f"Saved: {file_name}_original.png")
            print(f"Saved: {file_name}_daylight.png")
            print(f"Saved: {file_name}_night.png")
            print("-" * 80)

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
