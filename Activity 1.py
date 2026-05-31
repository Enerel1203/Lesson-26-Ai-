import time
import requests
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
from config import HF_API_KEY

MODEL = [
    "Bytedance/SDXL-Lightning",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-xl-base-1.0"
]

HEADERS = {"Authorization": f"Bearer {HF_API_KEY}", "Accept": "image/png"}

def generate_image_from_text(prompt):
    """prompt - > PIL.Image (or raise Exception)."""
    payload, last_err = {"inputs": prompt}, None
    
    for model in MODEL:
        url = f"https://api-inference.huggingface.co/models/{model}"

        for _ in range(3):
            r = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            ct = (r.headers.get("Content-Type") or "").lower()
            
            if r.status_code == 503 and "application/json" in ct:
                try:
                    return Image.open(BytesIO(r.content))
                except Exception as e:
                    last_err = f"Request failed with status code 200: Could not decode image bytes: {e}"
                    break

        raise Exception(last_err or f"Request failed with status code {r.status_code}: {r.text}")
    
def post_process_image(image):
    """Returns the processed PIL.Image (same I/O as your code)"""
    image = ImageEnhance.Brightness(image).enhance(1.2)
    image = ImageEnhance.Contrast(image).enhance(1.3)
    return image.filter(ImageFilter.GaussianBlur(radius=2))

def main():
    print("Welcome to the Post-Processing Magic Workshop!")
    print("This programme generates an image from text and applies post-processing effects.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Enter a text prompt (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break

        try:
            print("Generating image...")
            image = generate_image_from_text(user_input)
            print("Applying post-processing effects...")
            processed_image = post_process_image(image)
            
            save_option = input("Do you want to save the processed image? (yes/no)").strip().lower()
            if save_option == "yes":
                file_name = input("Enter a name for the image file (without extension): ").strip()
                processed_image.save(f"{file_name}.png")
                print(f"Image saved as {file_name}.png")

            print("-" * 80 + "\n")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()