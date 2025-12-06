import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_chat_id():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    print("Please send any message to your bot (@dre_stock_bot) on Telegram now...")
    print("Waiting for message...")

    for i in range(30):  # Wait up to 30 seconds
        time.sleep(1)
        response = requests.get(url)
        data = response.json()

        if data['ok'] and data['result']:
            chat_id = data['result'][-1]['message']['chat']['id']
            print(f"\n✓ Chat ID found: {chat_id}")

            # Update .env file
            env_path = '.env'
            with open(env_path, 'r') as f:
                lines = f.readlines()

            # Update or add TELEGRAM_CHAT_ID
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('TELEGRAM_CHAT_ID='):
                    lines[i] = f'TELEGRAM_CHAT_ID={chat_id}\n'
                    updated = True
                    break

            if not updated:
                lines.append(f'TELEGRAM_CHAT_ID={chat_id}\n')

            with open(env_path, 'w') as f:
                f.writelines(lines)

            print(f"✓ Updated .env with chat_id: {chat_id}")
            return chat_id

    print("\n✗ No message received. Please try again.")
    return None

if __name__ == "__main__":
    get_chat_id()
