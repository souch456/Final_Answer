# coding:utf-8

#課題1-1

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import urllib.parse
import time

store_names = [] #店舗名
detail_URL_list = [] #店舗詳細URL
phone_numbers = [] #電話番号
mail_address = [] #メールアドレス
prefectures = [] #都道府県
municipalities = [] #市区町村
house_number = [] #番地
buildings = [] #建物名

#検索語
s = '居酒屋'
#検索語のURLエンコーディング
s_quote = urllib.parse.quote(s)

#ユーザーエージェントの設定
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
header = {
    'User-Agent': user_agent
}

for i in range(3):
  #URLから対象のHTMLを取得
  url = "https://r.gnavi.co.jp/area/jp/rs/?fw={}&p={}".format(s_quote, i+1)

  time.sleep(3)
  r = requests.get(url, headers=header)
  soup = BeautifulSoup(r.text, 'html.parser')

  #店舗名
  h2_list = soup.find_all('h2', attrs={'class': 'style_restaurantNameWrap__wvXSR'}) 
  for h2 in h2_list:
    #print(h2.text)
    if len(store_names) >= 50:
      break
    else:
      store_names.append(h2.text)

  #店舗詳細
  a_list = soup.find_all('a', attrs={'class': 'style_titleLink__oiHVJ'}) 
  #print(a_list)

  for a in a_list:
    #print(a.get('href'))
    if len(detail_URL_list) >= 50:
      break
    else:
      detail_URL_list.append(a.get('href'))

for detail_URL in detail_URL_list:
  time.sleep(3)
  r = requests.get(detail_URL, headers=header)
  soup = BeautifulSoup(r.content, 'html.parser')

  #電話番号
  tel = soup.find('div', attrs={ 'class': 'phone-guide__number'}) 
  #print(tel.text)
  res = re.findall(r'\d+', tel.text)
  #print('-'.join(res))
  phone_numbers.append('-'.join(res))

  #メール
  mail_pattern = "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
  mail = re.findall(mail_pattern, str(soup))
  mail_address.append(mail)

  #住所
  region = soup.find('span', attrs={'class': 'region'}) 
  #print(region.text) 

  #都道府県，市区町村，それ以降の分割
  region_pattern = '''(...??[都道府県])((?:旭川|伊達|川崎|石狩|盛岡|奥州|田村|南相馬|那須塩原|東村山|武蔵村山|羽村|十日町|上越|富山|野々市|大町|蒲郡|四日市|姫路|大和郡山|廿日市|下松|岩国|田川|大村)市|.+?郡(?:玉村|大町|.+?)[町村]|.+?市.+?区|.+?[市区町村])(.+)'''
  result = re.match(region_pattern, region.text)
  #print(result.group(1))
  #print(result.group(2))
  #print(result.group(3))

  #地域，番地，建物名の分割
  banti_pattern = '''(.*?)([0-9０-９-]+)(.*)'''
  result_banti = re.match(banti_pattern, str(result.group(3)))
  #print(result_banti.group(1))
  #print(result_banti.group(2))
  #print(result_banti.group(3))

  #都道府県
  prefectures.append(result.group(1))
  #市区町村（今回は市区町村と地域をまとめる）
  municipalities.append(result.group(2)+result_banti.group(1))
  #番地
  house_number.append(result_banti.group(2))
  #建物名
  buildings.append(result_banti.group(3))


df = pd.DataFrame(
    data={'店舗名':store_names, '電話番号':phone_numbers, 'メールアドレス':mail_address, '都道府県':prefectures, '市区町村':municipalities, '番地':house_number, '建物名':buildings}
)

#CSV書き出し
df.to_csv('1-1.csv')
