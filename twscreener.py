from crawl_screener import selenium_crawl
from crawl_stock_info import get_stock_info
import requests
import pandas as pd
from datetime import datetime
import time
from PIL import Image, ImageSequence
import os
from config import user_agents_list
import random

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

fig_folder_path = r'fig'
driver_path = r'driver\edgedriver_win32\msedgedriver.exe'

def delete_gif_in_fig_folder():
    # List all files in the folder
    file_list = os.listdir(fig_folder_path)
    # Iterate through the files and delete those with the .gif extension
    for file in file_list:
        if file.endswith(".gif"):
            os.remove(os.path.join(fig_folder_path, file))

def twscreener():
    user_agent = random.choice(user_agents_list)
    # Set up Edge options
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # Instantiate the Edge WebDriver with the service and options
    service = Service(executable_path=driver_path)
    driver = webdriver.Edge(service=service, options=options)

    try:
        # Run selenium_crawl to get screener stocks list df
        print("Fetching screener list...")
        selenium_crawl(driver=driver)
        df = pd.read_pickle('data/screener_data.pkl')

        # print("Fetching high return list...")
        # df = pd.read_csv(r'C:\Users\User\Downloads\StockList (3).csv')
        # df['代號'] = df['代號'].apply(lambda x: x.replace("=", '').replace('"', ''))
        # df = df.sort_values(by='現距1個月低點漲幅', ascending=False)
        # df = df.iloc[:40, :]

        # Loop over df['代號'] and get stock info to add to df
        print("Fetching stock info...")
        industry_list = []
        main_service_list = []

        for stock_id in df['代號']:
            stock_info = get_stock_info(stock_id, driver=driver)
            if stock_info is not None:
                industry = stock_info['產業別'].iloc[0]
                main_service = stock_info['主要業務'].iloc[0]
            else:
                industry = None
                main_service = None
            industry_list.append(industry)
            main_service_list.append(main_service)
            time.sleep(1)  # Sleep to avoid overwhelming the server

    finally:
        driver.quit()

    df['產業別'] = industry_list
    df['主要業務'] = main_service_list
    df.to_pickle('data/screener_data.pkl')
    df.to_csv('data/screener_data.csv', index=False, encoding='utf-8-sig')
    
    # Proceed to download GIFs
    def download_fig(filename, url):
        headers = {
            'User-Agent': random.choice(user_agents_list)
        }        
        response = requests.get(url, headers=headers)
        with open(filename, 'wb') as f:
            f.write(response.content)

    def change_background_color(input_path, output_path):
        with Image.open(input_path) as img:
            frames = [frame.copy() for frame in ImageSequence.Iterator(img)]

            # Create a new sequence of frames with white background
            new_frames = []
            for frame in frames:
                # Convert the frame to RGBA if it's not already in that mode
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                
                # Create a new image with a white background
                new_frame = Image.new('RGBA', frame.size, (255, 255, 255))
                new_frame.paste(frame, (0, 0), frame)
                new_frames.append(new_frame)

            # Save the modified frames as a new GIF
            new_frames[0].save(output_path, save_all=True, append_images=new_frames[1:], loop=0)

    delete_gif_in_fig_folder()
    print("Downloading price trend charts...")
    for i, stock_id in enumerate(list(df['代號'].unique())):
        for fig_type in ['WEEK', 'DATE']:
            url = f'https://goodinfo.tw/tw/image/StockPrice/PRICE_{fig_type}_{stock_id}.gif'
            url += '?t=' + datetime.now().isoformat()
            filename = f'{fig_folder_path}/{i+1}_{stock_id}_{fig_type}.gif'
            download_fig(filename, url)
            change_background_color(filename, filename)
            time.sleep(2)
    print("Downloading foreign holding trend charts...")
    for i, stock_id in enumerate(list(df['代號'].unique())):
        url = f'https://goodinfo.tw/tw/image/StockBuySale/BUY_SALE_DATE_{stock_id}.gif'
        url += '?t=' + datetime.now().isoformat()
        filename = f'{fig_folder_path}/{i+1}_{stock_id}_BUY_SALE_DATE.gif'
        download_fig(filename, url)
        change_background_color(filename, filename)
        time.sleep(2)
    
    print('Finished.')

if __name__ == '__main__':
    twscreener()