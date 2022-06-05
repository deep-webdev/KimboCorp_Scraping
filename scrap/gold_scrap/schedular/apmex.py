from forex_python.converter import CurrencyRates
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from lxml.html import fromstring
import unicodedata
from gold_scrap.models import Apmex

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
    
def apmex(url):
    data = scraping(url)
    df = data[0][-1]
    soup = data[1]
    apmex_data = {}
    spot = troy_to_price()
    try:
        apmex_data['Product Name'] = soup.find("h1", {"class": "product-title"}).get_text().strip()
    except:
        apmex_data['Product Name'] = None
    try:
        apmex_data['Price'] = float(list(df[df.keys()[1]])[0].split('$')[1].replace(",", ""))
        apmex_data['Crypto Price'] = float(list(df[df.keys()[2]])[0].split('$')[1].replace(",", ""))
        apmex_data['CC/PayPal Price'] = float(list(df[df.keys()[3]])[0].split('$')[1].replace(",", ""))
        apmex_data['Stock'] = 'In Stock'
    except:
        apmex_data['Price'] = None
        apmex_data['Crypto Price'] = None
        apmex_data['CC/PayPal Price'] = None
        apmex_data['Stock'] = 'Out Of Stock'

    try:
        apmex_data['Product Id']=soup.find("ul",{"class":"product-table left"}).get_text().split("Product ID: ")[1].split("\n")[0].strip()
    except:
        apmex_data['Product Id']= None
    try:
        apmex_data['Metal Content'] = soup.find("ul",{"class":"product-table left"}).get_text().split("Metal Content: ")[1].strip()
        content = convert_to_float(apmex_data['Metal Content'].split()[0])
        apmex_data['Weight'] = str(int(float(apmex_data['Metal Content'].split('troy')[0].strip()) * 31.103)) + " " + "grams"
    except:
        apmex_data['Metal Content'] = None
        apmex_data['Weight'] = None

    unit_price = float(spot) * float(convert_to_float(content))

    if apmex_data['Price'] and content != 0: 
        difference = abs(int(apmex_data['Price']) - unit_price)
        apmex_data['Premium'] = round((difference / unit_price) * 100, 2)
    else:   
        apmex_data['Premium'] = 'NA'


    try:
        apmex_data['Purity'] = soup.find_all("ul", {"class": "product-table"})[1].get_text().split("Purity: ")[1].split("\n")[0].strip()
    except:
        apmex_data['Purity'] = None
    apmex_data['Manufacture'] = None
    apmex_data['Product URL'] = url
    apmex_data['Supplier name'] = 'APMEX'
    apmex_data['Supplier Country'] = 'Singapore'
    return apmex_data

def apmex_data():
    all_data = []
    j = 0
    for i in range(1,50):
        data = scraping('https://www.apmex.com/category/10000/gold/all?vt=g&f_metalname=Gold&page='+ str(i))
        df = data[0]
        soup = data[1]
        all_links = soup.find_all('a', {'class':'item-link'})
        basic_url = 'https://www.apmex.com'
        for link in all_links:
            data_link = basic_url + link.get('href')
            get_data = apmex(data_link)
            all_data.append(get_data)
            j += 1
    return all_data  

def update_data():
    all_data = apmex_data()
    df_final = pd.DataFrame(all_data)
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
    model_instances = [Apmex(
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
    
    Apmex.objects.all().delete()
    
    Apmex.objects.bulk_create(model_instances)