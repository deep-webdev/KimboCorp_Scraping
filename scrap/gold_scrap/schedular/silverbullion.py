from forex_python.converter import CurrencyRates
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from lxml.html import fromstring
import unicodedata
import math
from gold_scrap.models import SilverBullion

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

def silverbullion():
    products = ['https://www.silverbullion.com.sg/Shop/Buy/Gold_Coins?CurrentDeptUrl=Gold_Coins&ProductFilter=&SortBy=1&PageNo=1&CurrentBranch=',
              'https://www.silverbullion.com.sg/Shop/Buy/Gold_Bars?CurrentDeptUrl=Gold_Bars&ProductFilter=&SortBy=1&PageNo=1&CurrentBranch=',
              'https://www.silverbullion.com.sg/Shop/Buy/Gold_Bars?CurrentDeptUrl=Gold_Bars&ProductFilter=&SortBy=1&PageNo=2&CurrentBranch=']
    all_prod = []
    final_links = []
    for prod in products:
        data = scraping(prod)
        df = data[0]
        soup = data[1]
        pro = soup.find_all('h3')
        for i in pro:
            if i.find_all('a'):
                link = i.find_all('a')[0].get('href')
                final_links.append('https://www.silverbullion.com.sg' + link)
        final = set(final_links)
        data_set = []
        for j in final:
            data_set.append(silverbul(j))        
    return data_set

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

def silverbul(url):
    data = scraping(url)
    dfs = data[0]
    soup = data[1]
    silverbullion = {}
    c = CurrencyRates()
    spot = troy_to_price()
    Currency = c.get_rate('SGD', 'USD')
    silverbullion['Product Name'] = soup.find('title').get_text().split('|')[0]
    silverbullion['Price'] = float(dfs[10]['Price(SGD)'][0].split(' ')[0].replace(",", ""))
    silverbullion['SGD Price'] = silverbullion['Price']
    silverbullion['Price'] = Currency* silverbullion['Price']
    silverbullion['Crypto Price'] = None
    silverbullion['CC/PayPal Price'] = None
    try:
        silverbullion['W tz'] = dfs[8][0][0].split('oz')[0].strip().split('(')[1].strip()
    except:
        silverbullion['W tz'] = dfs[8][0][0].split('oz')[0].strip()
        if '|' in silverbullion['W tz'].split():
            silverbullion['W tz'] = dfs[8][0][0].split('oz')[0].split('|')[1].strip()
            
    tz = convert_to_float(silverbullion['W tz'])
    
    try:
        if silverbullion['W tz'].split('/'):
            silverbullion['Weight'] = str(int(math.floor(tz * 31.103))) + " " + "grams"
    except:
        silverbullion['Weight'] = str(int(math.floor(silverbullion['W tz'] * 31.103))) + " " + "grams"
        
    unit_price = spot * tz
    difference = abs(int(silverbullion['Price']) - unit_price)
    silverbullion['Premium'] = round((difference / unit_price) * 100, 2)
    silverbullion['Product Id'] = None
    silverbullion['Metal Content'] = None
    if silverbullion['Price']:
        silverbullion['Stock'] = "In Stock"
    else:
        silverbullion['Stock'] = "Out Of Stock"
    silverbullion['Purity'] = soup.find("p", {"class": "sgi-size-material hidden-xs"}).get_text().strip().split('.')[1].split('Purity')[0]
    silverbullion['Manufacture'] = soup.find("p", {"class": "sgi-size-material hidden-xs"}).get_text().strip().split('.')[1].split('Refiner:')[1]
    silverbullion['Product URL'] = url
    silverbullion['Supplier Country'] = "Singapore"
    silverbullion['Supplier name'] = "Silver Bullion"
    del silverbullion['W tz']
    return silverbullion

def update_data():
    data_set =silverbullion()
    df_final = pd.DataFrame(data_set)
    df_final.fillna('NA',inplace=True)
    df_final['Price'] = df_final['Price'].replace('NA',0)
    df_final['SGD Price'] = df_final['SGD Price'].replace('NA',0)

    df_final['Crypto Price'] = df_final['Crypto Price'].replace('NA',0)
    df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace('NA',0)


    df_final['Price'] = df_final['Price'].astype(float).astype(int)
    df_final['SGD Price'] = df_final['SGD Price'].astype(float).astype(int)
    df_final['Crypto Price'] = df_final['Crypto Price'].astype(int)
    df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].astype(int)
    df_final['Price'] = df_final['Price'].replace(0, 'NA')
    df_final['SGD Price'] = df_final['SGD Price'].replace(0, 'NA')
    df_final['Crypto Price'] = df_final['Crypto Price'].replace(0, 'NA')
    df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace(0, 'NA')

    df_records = df_final.to_dict('records')
    model_instances = [SilverBullion(
        product_name=record['Product Name'],
        price_usd=record['Price'],
        price_sgd=record['SGD Price'],
        crypto_price=record['Crypto Price'],
        paypal_price=record['CC/PayPal Price'], 
        weight = record['Weight'],
        premium = record['Premium'],
        product_id = record['Product Id'],
        metal_content = record['Metal Content'],
        stock=record['Stock'],
        purity = record['Purity'],
        manufacture = record['Manufacture'],
        product_url = record['Product URL'],
        supplier_name= record['Supplier name'],
        supplier_country = record['Supplier Country']
    ) for record in df_records]
    
    SilverBullion.objects.all().delete()
    
    SilverBullion.objects.bulk_create(model_instances)