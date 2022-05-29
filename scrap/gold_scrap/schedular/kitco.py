from forex_python.converter import CurrencyRates
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from lxml.html import fromstring
import unicodedata
import gspread
from pycoingecko import CoinGeckoAPI
import math

def scraping(url):
    header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url, headers=header)
    tree = fromstring(r.content)
    try:
        dfs = pd.read_html(r.text)
    except:
        dfs = pd.DataFrame()
    soup = BeautifulSoup(r.content, features="lxml")
    return [dfs, soup]

def urls():
    header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
    }
    req = Request("https://online.kitco.com/gold",headers=header)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")
    link_class = soup.find_all('div', 'product_description')
    links = []
    for link in link_class:
        links.append(link.find('a').get('href'))
    return links

def convert_to_float(frac_str):
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac
    
def troy_to_price():
    data = scraping('https://www.monex.com/gold-prices/')
    dfs = data[0]
    soup = data[1]
    spot = float(dfs[0]['Today'][0].replace('$','').replace(',',''))
    return spot

spot = troy_to_price()
def kitco(url):
    data = scraping('https://online.kitco.com' + url)
    kitco = {}
    soup = data[1]

    kitco['Product Name'] = soup.find("div", {"id": "prod_title"}).get_text().split('\n')[1].split('Buying')[0].replace('Buy','')
    try:
        dfs = data[0][0]
        kitco['Price'] = float(dfs['Wire/Check'][0].split('$')[1].replace(",", ""))
        try:
            kitco['CC/PayPal Price'] = float(dfs['MC/Visa/PayPal'][0].split('$')[1].replace(",", ""))
        except:
            kitco['CC/PayPal Price'] = None
        kitco['Stock'] = 'In Stock'
        
    except:
        kitco['Price'] = None
        kitco['CC/PayPal Price'] = None
        kitco['Stock'] = 'Out of Stock'

    kitco['Crypto Price'] = None
    kitco['Metal Content'] = soup.find("ul", {"id": "prod_details_list"}).get_text().split(':')[1].strip().split('\r')[0]

    if 'oz' in kitco['Metal Content'].split():
        content = kitco['Metal Content'].split()[0]
    elif 'g' in kitco['Metal Content'].split():
        content = convert_to_float(kitco['Metal Content'].split()[0]) * 0.035274

    unit_price = float(spot) * float(convert_to_float(content))
    if kitco['Price']: 
        difference = abs(int(kitco['Price']) - unit_price)
        kitco['Premium'] = round((difference / unit_price) * 100, 2)
    else:   
        kitco['Premium'] = 'NA'

    kitco['Product Id'] = None
    kitco['Product URL'] = "https://online.kitco.com" + url
    kitco['Supplier Country'] = "USA"
    kitco['Supplier name'] = "Kitco"
    kitco['Manufacture'] = None
    kitco['Purity'] = soup.find("ul", {"id": "prod_details_list"}).get_text().split('Fineness:')[1].strip().split('\r')[0]
    kitco['Weight'] = soup.find("span", {"property": "weight"}).get_text().strip()
    return kitco

url_S = urls()
data_set = []
for url in url_S:
    data_set.append(kitco(url))

df_final = pd.DataFrame(data_set)
df_final['Fees'] = 0.8
df_final['Commissions'] = 0.5
df_final['Final Price'] = df_final['Price'] + df_final['Price'] * (df_final['Fees']/100) + df_final['Price'] * (df_final['Commissions']/100)
cols = df_final.columns.tolist()
cols = cols[0:2] + [cols[4]] + [cols[2]] + cols[6:9] + [cols[5]] + [cols[3]] + cols[9:]
df_final = df_final[cols]
df_final.fillna('NA',inplace=True)
df_final['Price'] = df_final['Price'].replace('NA',0)
df_final['Crypto Price'] = df_final['Crypto Price'].replace('NA',0)
df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace('NA',0)
df_final['Final Price'] = df_final['Final Price'].replace('NA',0)
cg = CoinGeckoAPI()
crypto_price = cg.get_price(ids='bitcoin,tether,ethereum', vs_currencies='usd')
df_final['Bitcoin Price'] = round(df_final['Final Price'] / crypto_price['bitcoin']['usd'], 4)
df_final['Ethereum Price'] = round(df_final['Final Price'] / crypto_price['ethereum']['usd'], 4)
df_final['Tether Price'] = round(df_final['Final Price'] / crypto_price['tether']['usd'], 4)

df_final['Price'] = df_final['Price'].astype(float).astype(int)
df_final['Crypto Price'] = df_final['Crypto Price'].astype(int)
df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].astype(int)

df_final['Price'] = df_final['Price'].replace(0,'NA')
df_final['Crypto Price'] = df_final['Crypto Price'].replace(0,'NA')
df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace(0,'NA')
df_final['Final Price'] = df_final['Final Price'].replace(0,'NA')
df_final['Bitcoin Price'] = df_final['Bitcoin Price'].replace(0,'NA')
df_final['Ethereum Price']  = df_final['Ethereum Price'].replace(0,'NA')
df_final['Tether Price'] = df_final['Tether Price'].replace(0,'NA')

Sheet_name = "Gold Data"
API_key_file = "/root/gold-data/crypto-sheet-324805-ece76fbce54b.json"
gc = gspread.service_account(filename=API_key_file)
sh = gc.open(Sheet_name)

worksheet = sh.get_worksheet(3)
worksheet.update([df_final.columns.values.tolist()] + df_final.values.tolist())