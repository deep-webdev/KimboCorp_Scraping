from forex_python.converter import CurrencyRates
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from lxml.html import fromstring
import unicodedata
from gold_scrap.models import IndigoPrecious

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
    indigo['Weight'] = indigo['Metal Content']
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

def update_data():
    data_set = indigo()
    df_final = pd.DataFrame(data_set)
    cols = df_final.columns.tolist()
    cols = cols[0:4] + cols[6:8] + [cols[4]] + [cols[5]] + [cols[8]] + [cols[10]] + [cols[9]] + cols[11:] 
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
    df_final['Purity'] = df_final['Purity'].replace('','NA')
    df_final['SGD Price'] = "NA"

    df_records = df_final.to_dict('records')
    model_instances = [IndigoPrecious(
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
    
    IndigoPrecious.objects.all().delete()
    
    IndigoPrecious.objects.bulk_create(model_instances)