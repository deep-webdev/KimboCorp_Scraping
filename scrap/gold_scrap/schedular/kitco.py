from forex_python.converter import CurrencyRates
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from lxml.html import fromstring
import unicodedata
import math
from gold_scrap.models import Kitco

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

    kitco['Weight'] = float(convert_to_float(content)) * (1/0.035274) + 'grams'
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
     
    return kitco

def update_data():
    url_S = urls()
    data_set = []
    for url in url_S:
        data_set.append(kitco(url))

    df_final = pd.DataFrame(data_set)
    cols = df_final.columns.tolist()
    cols = cols[0:2] + [cols[4]] + [cols[2]] + cols[6:9] + [cols[5]] + [cols[3]] + cols[9:]
    df_final = df_final[cols]
    df_final.fillna('NA',inplace=True)
    df_final['Price'] = df_final['Price'].replace('NA',0)
    df_final['Crypto Price'] = df_final['Crypto Price'].replace('NA',0)
    df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace('NA',0)
    df_final['Price'] = df_final['Price'].astype(float).astype(int)
    df_final['Crypto Price'] = df_final['Crypto Price'].astype(int)
    df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].astype(int)
    df_final['Price'] = df_final['Price'].replace(0,'NA')
    df_final['Crypto Price'] = df_final['Crypto Price'].replace(0,'NA')
    df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace(0,'NA')
    df_final['SGD Price'] = "NA"
    
    df_records = df_final.to_dict('records')
    model_instances = [Kitco(
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
    
    Kitco.objects.all().delete()
    
    Kitco.objects.bulk_create(model_instances)