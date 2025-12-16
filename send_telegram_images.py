import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_telegram_photo(image_path, caption=""):
    """Send a single image via Telegram bot"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    try:
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption
            }

            response = requests.post(url, files=files, data=data)

            if response.status_code == 200:
                print(f"✓ Sent: {os.path.basename(image_path)}")
                return True
            else:
                print(f"✗ Failed to send {os.path.basename(image_path)}: {response.text}")
                return False
    except Exception as e:
        print(f"✗ Error sending {image_path}: {e}")
        return False

def send_all_images_from_folder(folder_path='fig'):
    """Send all images from the specified folder"""
    # Supported image formats
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}

    # Get all image files
    folder = Path(folder_path)
    if not folder.exists():
        print(f"✗ Folder '{folder_path}' not found!")
        return

    image_files = [f for f in folder.iterdir()
                   if f.is_file() and f.suffix.lower() in image_extensions]

    if not image_files:
        print(f"✗ No images found in '{folder_path}'")
        return

    print(f"Found {len(image_files)} image(s) in '{folder_path}'")
    print("-" * 50)

    success_count = 0
    for img_file in sorted(image_files):
        caption = img_file.stem  # Use filename without extension as caption
        if send_telegram_photo(str(img_file), caption):
            success_count += 1

    print("-" * 50)
    print(f"Sent {success_count}/{len(image_files)} images successfully!")

def send_specific_image(image_name, caption=""):
    """Send a specific image by filename"""
    image_path = Path('fig') / image_name

    if not image_path.exists():
        print(f"✗ Image '{image_path}' not found!")
        return False

    return send_telegram_photo(str(image_path), caption)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Send specific image(s) if filenames provided
        for img_name in sys.argv[1:]:
            send_specific_image(img_name)
    else:
        # Send all images from fig/ folder
        send_all_images_from_folder('fig/today')
