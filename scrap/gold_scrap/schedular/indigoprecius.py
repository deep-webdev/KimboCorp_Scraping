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

def troy_to_price():
    data = scraping('https://www.monex.com/gold-prices/')
    dfs = data[0]
    soup = data[1]
    spot = float(dfs[0]['Today'][0].replace('$','').replace(',',''))
    return spot

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
    
spot = troy_to_price()
def indigofetch(url):
    data = scraping(url)
    df = data[0]
    soup = data[1]
    indigo = {}
    indigo['Product Name'] = soup.find("div", {"class": "product-name"}).get_text().split("\n")[1]
    indigo['Crypto Price'] = None
    try:
        indigo['Price'] = float(df[0]['Prices'][0].split('USD')[0].strip().replace(",",""))
    except:
        indigo['Price'] = float(soup.find_all('span','price')[5].get_text().split()[0].replace(",",""))
    indigo['CC/PayPal Price'] = None
    indigo['Product Id']= None
    indigo['Metal Content']= soup.find("div", {"class":"specifications"}).get_text(strip=True).split('Country')[0].split('Weight')[1]

    if 'KG' in indigo['Metal Content'].split():
        content = convert_to_float(indigo['Metal Content'].split()[0]) * 0.035274 *1000
    elif 'grams' in indigo['Metal Content'].split():
        content = convert_to_float(indigo['Metal Content'].split()[0]) * 0.035274

    unit_price = float(spot) * float(convert_to_float(content))
    if indigo['Price']: 
        difference = abs(int(indigo['Price']) - unit_price)
        indigo['Premium'] = round((difference / unit_price) * 100, 2)
    else:   
        indigo['Premium'] = 'NA'
    if indigo['Price']:
        indigo['Stock'] = "In Stock"
    else:
        indigo['Stock'] = "Out Of Stock"
    indigo['Manufacture'] = None
    try:
        line = soup.find("ul", {"class": "spec-list"}).get_text(strip=True)
        regex = re.compile('Purity([0-9]*)')
        indigo['Purity'] = regex.findall(line)[0]
    except:
        indigo['Purity'] = None
    indigo['Product URL'] = url
    indigo['Supplier name'] = 'Indigo precious metals'
    indigo['Supplier Country'] = 'Singapore'
    indigo['Weight'] = None
    return indigo

def indigo():
    products = ['https://www.indigopreciousmetals.com/bullion-products/gold/gold-bars.html',
              'https://www.indigopreciousmetals.com/bullion-products/gold/gold-coins.html']
    data_set = []            
    for prod in products:
        data = scraping(prod)
        df = data[0]
        soup = data[1]
        pro = soup.find_all('a', 'product-image')

        for i in pro:
            url = i.get('href')
            data_set.append(indigofetch(url))
    return data_set

data_set = indigo()
df_final = pd.DataFrame(data_set)
df_final['Fees'] = 0.8
df_final['Commissions'] = 0.5
df_final['Final Price'] = df_final['Price'] + df_final['Price'] * (df_final['Fees']/100) + df_final['Price'] * (df_final['Commissions']/100)

cols = df_final.columns.tolist()
cols = cols[0:4] + cols[6:8] + [cols[4]] + [cols[5]] + [cols[8]] + [cols[10]] + [cols[9]] + cols[11:] 
df_final = df_final[cols]
df_final.fillna('NA',inplace=True)
cg = CoinGeckoAPI()
crypto_price = cg.get_price(ids='bitcoin,tether,ethereum', vs_currencies='usd')
df_final['Price'] = df_final['Price'].replace('NA',0)
df_final['Crypto Price'] = df_final['Crypto Price'].replace('NA',0)
df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace('NA',0)
df_final['Price'] = df_final['Price'].astype(float).astype(int)
df_final['Crypto Price'] = df_final['Crypto Price'].astype(int)
df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].astype(int)
df_final['Price'] = df_final['Price'].replace(0,'NA')
df_final['Crypto Price'] = df_final['Crypto Price'].replace(0,'NA')
df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace(0,'NA')
df_final['Purity'] = df_final['Purity'].replace('','NA')
df_final['Final Price'] = df_final['Final Price'].astype(int)
df_final['Bitcoin Price'] = round(df_final['Final Price'] / crypto_price['bitcoin']['usd'], 4)
df_final['Ethereum Price'] = round(df_final['Final Price'] / crypto_price['ethereum']['usd'], 4)
df_final['Tether Price'] = round(df_final['Final Price'] / crypto_price['tether']['usd'], 4)

Sheet_name = "Gold Data"
API_key_file = "/root/gold-data/crypto-sheet-324805-ece76fbce54b.json"
gc = gspread.service_account(filename=API_key_file)
sh = gc.open(Sheet_name)

worksheet = sh.get_worksheet(4)
worksheet.update([df_final.columns.values.tolist()] + df_final.values.tolist())