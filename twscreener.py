from selenium_crawl import selenium_crawl
import requests
import pandas as pd
from datetime import datetime
import time
from PIL import Image, ImageSequence
import os

fig_folder_path = r'C:\Users\User\Desktop\pool\screener\fig'

def delete_gif_in_fig_folder():
    # List all files in the folder
    file_list = os.listdir(fig_folder_path)
    # Iterate through the files and delete those with the .gif extension
    for file in file_list:
        if file.endswith(".gif"):
            os.remove(os.path.join(fig_folder_path, file))
            
def twscreener():
    # goodinfo stock screener
    # url = 'https://goodinfo.tw/tw2/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=&FL_VAL_S0=&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=MACD%7C%7CDIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0%40%40%E6%97%A5MACD%E8%90%BD%E9%BB%9E%40%40DIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0&FL_RULE1=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C5%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%405%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5&FL_RULE2=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A820%E6%97%A5%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A8%E5%9D%87%E9%87%8F%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%4020%E6%97%A5%E7%B7%9A&FL_RULE3=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%7C%7C%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%8D%8A%E5%B9%B4%E9%AB%98%E9%BB%9E%40%40%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%A4%9A%E6%97%A5%E9%AB%98%E9%BB%9E%40%40%E5%8D%8A%E5%B9%B4&FL_RULE4=RSI%7C%7C%E6%97%A5RSI6%E4%BB%8B%E6%96%BC50%7E80%40%40%E6%97%A5RSI%E8%90%BD%E9%BB%9E%40%40RSI6%E4%BB%8B%E6%96%BC50%7E80&FL_RULE5=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C20%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%4020%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E4%B8%8A%E5%B8%82%2F%E4%B8%8A%E6%AB%83&FL_QRY=%E6%9F%A5++%E8%A9%A2'
    # # url = 'https://goodinfo.tw/tw2/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=&FL_VAL_S0=&FL_VAL_E0=&FL_ITEM1=&FL_VAL_S1=&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=MACD%7C%7CDIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0%40%40%E6%97%A5MACD%E8%90%BD%E9%BB%9E%40%40DIF%E3%80%81MACD%E5%A4%A7%E6%96%BC0&FL_RULE1=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C5%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%E4%B8%94%E8%B5%B0%E6%8F%9A%40%405%E6%97%A5%2F10%E6%97%A5%2F20%E6%97%A5&FL_RULE2=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A820%E6%97%A5%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%40%E6%88%90%E4%BA%A4%E9%87%8F%E5%9C%A8%E5%9D%87%E9%87%8F%E7%B7%9A%E4%B9%8B%E4%B8%8A%40%4020%E6%97%A5%E7%B7%9A&FL_RULE3=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81%7C%7C%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%8D%8A%E5%B9%B4%E9%AB%98%E9%BB%9E%40%40%E8%82%A1%E5%83%B9%E6%8E%A5%E8%BF%91%E5%A4%9A%E6%97%A5%E9%AB%98%E9%BB%9E%40%40%E5%8D%8A%E5%B9%B4&FL_RULE4=RSI%7C%7C%E6%97%A5RSI6%E4%BB%8B%E6%96%BC50%7E80%40%40%E6%97%A5RSI%E8%90%BD%E9%BB%9E%40%40RSI6%E4%BB%8B%E6%96%BC50%7E80&FL_RULE5=%E5%9D%87%E7%B7%9A%E4%BD%8D%E7%BD%AE%7C%7C20%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%40%E5%9D%87%E5%83%B9%E7%B7%9A%E5%A4%9A%E9%A0%AD%E6%8E%92%E5%88%97%40%4020%E6%97%A5%2F60%E6%97%A5%2F120%E6%97%A5&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E4%B8%8A%E5%B8%82%2F%E4%B8%8A%E6%AB%83&FL_QRY=%E6%9F%A5++%E8%A9%A2'
    selenium_crawl()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    # response = requests.get(url, headers=headers)
    # response.encoding = 'utf-8'  # or the appropriate encoding for your webpage

    # soup = BeautifulSoup(response.text, 'html.parser')
    # table = soup.find('table', {'id': 'tblStockList'})

    # df = pd.read_html(str(table), encoding='utf-8')[0]
    # df.to_pickle('stock_list.pkl')

    df = pd.read_pickle('screener_data.pkl')
    # df = df.loc[df['成交額 (百萬)']!='成交額 (百萬)']
    # df['成交額 (百萬)'] = df['成交額 (百萬)'].astype(float)
    # df = df[df['成交額 (百萬)'] >= 1]
    df = df.loc[df['代號'].apply(lambda x: len(str(x)) == 4)]
    # df = df.sort_values(by=['成交額 (百萬)'], ascending=False)
    df.to_pickle('stock_list.pkl')

    def download_fig(filename, url):
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
    print("下載價格趨勢圖")
    for stock_id in list(df['代號'].unique())[:70]:
        for fig_type in ['WEEK', 'DATE']:
            # stock_id = df[df['代號'] == '8227']['代號'].iloc[0]
            url = f'https://goodinfo.tw/tw/image/StockPrice/PRICE_{fig_type}_{stock_id}.gif'
            url += '?t=' + datetime.now().isoformat()
            filename = f'{fig_folder_path}/{stock_id}_{fig_type}.gif'
            download_fig(filename, url)
            change_background_color(filename, filename)
            time.sleep(2)
    print("下載外資持股比例趨勢圖")
    for stock_id in list(df['代號'].unique())[:70]:
        url = f'https://goodinfo.tw/tw/image/StockBuySale/BUY_SALE_DATE_{stock_id}.gif'
        url += '?t=' + datetime.now().isoformat()
        filename = f'{fig_folder_path}/{stock_id}_BUY_SALE_DATE.gif'
        download_fig(filename, url)
        change_background_color(filename, filename)
        time.sleep(2)
    
    print('finished.')

if __name__ == '__main__':
    twscreener()
