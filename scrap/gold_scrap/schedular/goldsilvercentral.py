from forex_python.converter import CurrencyRates
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from lxml.html import fromstring
from gold_scrap.models import GoldCentral


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
    
def urls():
    header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
    }
    req = Request("https://www.goldsilvercentral.com.sg/product-category/buy-gold/",headers=header)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")
    link_class = soup.find_all('div', 'product-list-item')
    links = []
    for link in link_class:
        links.append(link.find('a').get('href'))
    return links

spot = troy_to_price()
def goldcentral(url):
    data = scraping(url)
    dfs = data[0][3]
    soup = data[1]
    c = CurrencyRates()
    Currency = c.get_rate('SGD', 'USD')
    goldcentral = {}
    goldcentral['Product Name'] = soup.find("h1", {"class": "product_title entry-title"}).get_text()

    try:
        goldcentral['Price'] = float(soup.find("span", {"class":"amount"}).get_text().replace('$','').replace(',',''))
        goldcentral['SGD Price'] =  goldcentral['Price']
        goldcentral['Price'] = Currency * goldcentral['Price']
    except:  
        goldcentral['Price'] = None
        goldcentral['SGD Price'] = None
    goldcentral['Crypto Price'] = None
    goldcentral['CC/PayPal Price'] = None
    try:
        goldcentral['Metal Content'] = soup.find("td", {"class":"product_weight"}).get_text()
        content = convert_to_float(goldcentral['Metal Content'].split()[0])
    except:  
        goldcentral['Metal Content'] = None
        content = 0
    unit_price = float(spot) * float(convert_to_float(content))
    
    if goldcentral['Price'] and content != 0: 
        difference = abs(int(goldcentral['Price']) - unit_price)
        goldcentral['Premium'] = round((difference / unit_price) * 100, 2)
    else:   
        goldcentral['Premium'] = 'NA'

    if goldcentral['Price']:
        goldcentral['Stock'] = "In Stock"
    else:
        goldcentral['Stock'] = "Out Of Stock"

    goldcentral['Supplier Country'] = "Singapore"
    goldcentral['Product URL'] = url
    goldcentral['Manufacture'] = None
    try:
        purity = soup.find("div", {"class":"kw-details-desc"}).get_text().split('purity of')[1].split('%')[0]
        goldcentral['Purity'] = float(purity.strip()) * 100
    except:
        goldcentral['Purity'] = None
    goldcentral['Supplier name'] = "Gold Silver Central"
    goldcentral['Product Id'] = None
    try:
        goldcentral['Weight'] = soup.find("td", {"class":"product_weight"}).get_text()
        goldcentral['Weight'] = str(round(float(goldcentral['Weight'].split('oz')[0]) * 31.103, 2)) + " " + "grams"
    except:  
        goldcentral['Weight'] = None
    return goldcentral


def update_data():
    url_S = urls()
    data_set = []
    for url in url_S:
        data_set.append(goldcentral(url))

    df_final = pd.DataFrame(data_set)
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
    
    df_records = df_final.to_dict('records')
    model_instances = [GoldCentral(
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
    
    GoldCentral.objects.all().delete()

    GoldCentral.objects.bulk_create(model_instances)

