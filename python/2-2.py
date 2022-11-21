# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
import urllib.parse
import time
import re
import pandas as pd
from sqlalchemy import create_engine


store_names = [] #店舗名
detail_URL_list = [] #店舗詳細URL
phone_numbers = [] #電話番号
mail_address = [] #メールアドレス
prefectures = [] #都道府県
municipalities = [] #市区町村
house_number = [] #番地
buildings = [] #建物名
store_URL = [] #店舗ホームページURL
store_SSL = [] #SSL証明書の有無


#検索語
s = '居酒屋'
#検索語のURLエンコーディング
s_quote = urllib.parse.quote(s)


user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--user-agent='+user_agent)

#driver = webdriver.Chrome(chrome_options=options, executable_path="/Users/matsuosouichirou/Downloads/chromedriver")
driver = webdriver.Remote(
        command_executor="http://selenium:4444/wd/hub",
        options=options
    )

#店舗詳細ページに店舗のホームページのリンクが存在するか確認する関数
#入力：店舗詳細ページを読み込んだdriver
def find_homepage(driver):
    try:
        element = driver.find_element(By.ID,'sv-site')
        aTag = element.find_element(By.TAG_NAME, "a")
        homepage_url = aTag.get_attribute("href")
        return homepage_url
    except:
        #ホームページがない場合
        return 


for i in range(3):
  #URLから対象のHTMLを取得
  url = "https://r.gnavi.co.jp/area/jp/rs/?fw={}&p={}".format(s_quote, i+1)

  time.sleep(3)
  driver.get(url)

  #店舗名
  for h2 in driver.find_elements(By.CLASS_NAME, 'style_restaurantNameWrap__wvXSR'):
    if len(store_names) >= 50:
      break
    else:
      store_names.append(h2.text)   

  #店舗詳細
  for a in driver.find_elements(By.CLASS_NAME, 'style_titleLink__oiHVJ'):
    #print(a.get_attribute('href'))
    if len(detail_URL_list) >= 50:
      break
    else:
      detail_URL_list.append(a.get_attribute('href'))

for detail_URL in detail_URL_list:
  time.sleep(3)
  driver.get(detail_URL)

  #電話番号
  tel = driver.find_element(By.CLASS_NAME, 'phone-guide__number')
  res = re.findall(r'\d+', tel.text)
  #print('-'.join(res))
  phone_numbers.append('-'.join(res))

  #メール
  mail_pattern = "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
  mail = re.findall(mail_pattern, str(driver.page_source))
  mail_address.append(' '.join(mail))

  #住所
  region = driver.find_element(By.CLASS_NAME, 'region')
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

  #ホームページURL
  homepage_url = str(find_homepage(driver))
  store_URL.append(homepage_url)

  #SSL証明書の有無
  if re.match("https:", homepage_url):
    store_SSL.append(True)
  else:
    store_SSL.append(False)



df = pd.DataFrame(
    data={'store_name':store_names, 'phone_number':phone_numbers, 'mail_address':mail_address, 'prefecture':prefectures, 'municipality':municipalities, 'house_number':house_number, 'buildings':buildings, 'URL':store_URL, 'SSL_':store_SSL}
)

#CSV書き出し
#df.to_csv('2-1.csv')

#sql書き出し
engine = create_engine('mysql://docker:docker@db/test_database?charset=utf8')
df.to_sql('result',con=engine, if_exists='append', index=False)
