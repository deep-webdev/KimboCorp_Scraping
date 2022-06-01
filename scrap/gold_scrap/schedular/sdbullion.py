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
def sdb(url):
    data = scraping(url)
    df = data[0]
    soup = data[1]
    sbul = {}
    sbul['Product name'] = soup.find("h1", {'class': 'page-title'}).get_text()

    if not soup.find('p', {'class': 'currently-out-of-stock'}):
        sbul['Price'] = float(df[0]['Check / Wire'][0].split("$")[1].replace(",",""))
        sbul['Crypto Price'] = float(df[0]['Bitcoin'][0].split("$")[1].replace(",",""))
        sbul['Credit/Paypal Price'] = float(df[0]['Credit / PayPal'][0].split("$")[1].replace(",",""))
        sbul['Stock'] = "In stock"
    else:
        sbul['Price'] = None
        sbul['Crypto Price'] = None
        sbul['Credit/Paypal Price'] = None
        sbul['Stock'] = "Out of Stock"
    sbul['Metal content'] = df[-1][1][3]
    wz = 0
    unit_price = 0
    try:
        if 'Troy Oz' in sbul['Metal content']:
            wz = float(sbul['Metal content'].split('Troy Oz')[0].strip())
            unit_price = wz * spot
        elif 'Grams' in sbul['Metal content']:
            wz = float(sbul['Metal content'].split('Grams')[0]) / 31.103
            unit_price = wz * spot
        elif 'Gram' in sbul['Metal content']:
            wz = float(sbul['Metal content'].split('Gram')[0]) / 31.103
            unit_price = wz * spot
        else:
            sbul['Metal content'] = None
        if sbul['Price'] and unit_price != 0:
            difference = abs(int(sbul['Price']) - unit_price)
            sbul['Premium'] = round((difference / unit_price) * 100, 2)
        else:
            sbul['Premium'] = None    
    except:
        sbul['Premium'] = None
    try:
        sbul['Purity'] = df[-1][1][5]
    except:
        sbul['Purity'] = None
    sbul['Metal type'] = df[-1][1][0]
    sbul['Product URL'] = url
    sbul['Manufacture'] = None
    sbul['Supplier Country'] = "USA"
    return sbul

def sdbullion():
    products = ['https://sdbullion.com/gold/american-gold-eagle-coins/1-oz-gold-eagle-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/1-2-oz-gold-eagle-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/1-4-oz-gold-eagle-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/1-10-oz-gold-eagle-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/graded-american-gold-eagle-coins?product_list_limit=50',
                'https://sdbullion.com/gold/american-gold-eagle-coins/graded-american-gold-eagle-coins?p=2&product_list_limit=50',
                'https://sdbullion.com/gold/american-gold-eagle-coins/pre-1933-us-mint-gold-coins?product_list_limit=50',
                'https://sdbullion.com/gold/american-gold-eagle-coins/american-gold-eagle-proof-coins/mint-box-and-coa?product_list_limit=50',
                'https://sdbullion.com/gold/american-gold-eagle-coins/american-gold-eagle-proof-coins/ngc-graded-american-gold-eagle-proof-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/american-gold-eagle-proof-coins/pcgs-graded-american-gold-eagle-proofs-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/american-gold-eagle-proof-coins/american-gold-eagle-proof-sets',
                'https://sdbullion.com/gold/american-gold-eagle-coins/us-mint-gold-commemorative-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-2-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-4-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-10-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-20-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-gram-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/call-of-the-wild-gold-coins',
                'https://sdbullion.com/gold/american-gold-buffalo-coins?product_list_limit=50',
                'https://sdbullion.com/gold/british-royal-mint-gold-coins/gold-britannia-coins',
                'https://sdbullion.com/gold/british-royal-mint-gold-coins/royal-mint-tudor-beast-gold-coins',
                'https://sdbullion.com/gold/british-royal-mint-gold-coins/gold-queen-s-beast-coins',
                'https://sdbullion.com/gold/british-royal-mint-gold-coins/other-british-gold-coins',
                'https://sdbullion.com/gold/chinese-gold-panda-coins?product_list_limit=50',
                'https://sdbullion.com/gold/south-african-gold-krugerrand-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/australian-gold-kangaroo-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/australian-kookaburra-gold-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-iii-gold-coins/perth-mint-year-of-the-ox-gold-coins-lunar-series-3',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-iii-gold-coins/perth-mint-year-of-the-mouse-gold-coins-lunar-series-3',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-iii-gold-coins/perth-mint-year-of-the-tiger-gold-coins-lunar-series-3',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-2-gold-coins/perth-mint-lunar-year-of-the-snake-gold-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-2-gold-coins/perth-mint-lunar-year-of-the-pig-gold-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-2-gold-coins/perth-mint-lunar-year-of-the-dog-gold-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-1-gold-coins',
                'https://sdbullion.com/gold/mexican-gold-libertad-coins?product_list_limit=50',
                'https://sdbullion.com/gold/austrian-gold-philharmonic-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/pre-1933-us-mint-gold-coins?product_list_limit=50',
                'https://sdbullion.com/gold/other-gold-products?product_list_limit=50',
                'https://sdbullion.com/gold/other-gold-products?p=2&product_list_limit=50',
                'https://sdbullion.com/gold/gold-bars?product_list_limit=50',
                'https://sdbullion.com/gold/gold-bars?p=2&product_list_limit=50',
                'https://sdbullion.com/gold/ira-approved-gold?product_list_limit=50',
                'https://sdbullion.com/gold/ira-approved-gold?p=2&product_list_limit=50']
    all_prod = []
    for prod in products:
        data = scraping(prod)
        df = data[0]
        soup = data[1]
        links = soup.find_all('a', 'product-item-photo')
        for link in links:
            all_prod.append(sdb(link.get('href')))
    return all_prod

data_set = sdbullion()
df_final = pd.DataFrame(data_set)
df_final['Fees'] = 0.8
df_final['Commissions'] = 0.5
df_final['Final Price'] = df_final['Price'] + df_final['Price'] * (df_final['Fees']/100) + df_final['Price'] * (df_final['Commissions']/100)

df_final.fillna('NA',inplace=True)
cg = CoinGeckoAPI()
crypto_price = cg.get_price(ids='bitcoin,tether,ethereum', vs_currencies='usd')
df_final['Price'] = df_final['Price'].replace('NA',0)
df_final['Crypto Price'] = df_final['Crypto Price'].replace('NA',0)
df_final['Credit/Paypal Price'] = df_final['Credit/Paypal Price'].replace('NA',0)
df_final['Final Price'] = df_final['Final Price'].replace('NA',0)
df_final['Price'] = df_final['Price'].astype(float).astype(int)
df_final['Crypto Price'] = df_final['Crypto Price'].astype(int)
df_final['Credit/Paypal Price'] = df_final['Credit/Paypal Price'].astype(int)
df_final['Final Price'] = df_final['Final Price'].astype(int)
df_final['Price'] = df_final['Price'].replace(0,'NA')
df_final['Crypto Price'] = df_final['Crypto Price'].replace(0,'NA')
df_final['Credit/Paypal Price'] = df_final['Credit/Paypal Price'].replace(0,'NA')
df_final['Purity'] = df_final['Purity'].replace('','NA')
df_final['Bitcoin Price'] = round(df_final['Final Price'] / crypto_price['bitcoin']['usd'], 4)
df_final['Ethereum Price'] = round(df_final['Final Price'] / crypto_price['ethereum']['usd'], 4)
df_final['Tether Price'] = round(df_final['Final Price'] / crypto_price['tether']['usd'], 4)
df_final['Final Price'] = df_final['Final Price'].replace(0,'NA')
df_final['Bitcoin Price'] = df_final['Bitcoin Price'].replace(0,'NA')
df_final['Ethereum Price'] = df_final['Ethereum Price'].replace(0,'NA')
df_final['Tether Price'] = df_final['Tether Price'].replace(0,'NA')

Sheet_name = "Gold Data"
API_key_file = "/root/gold-data/crypto-sheet-324805-ece76fbce54b.json"
gc = gspread.service_account(filename=API_key_file)
sh = gc.open(Sheet_name)

worksheet = sh.get_worksheet(5)
worksheet.update([df_final.columns.values.tolist()] + df_final.values.tolist())