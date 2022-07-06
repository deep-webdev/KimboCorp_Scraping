from forex_python.converter import CurrencyRates
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from lxml.html import fromstring
import unicodedata
from gold_scrap.models import Extracted
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

def troy_to_price():
    data = scraping('https://www.monex.com/gold-prices/')
    dfs = data[0]
    soup = data[1]
    spot = float(dfs[0]['Today'][0].replace('$','').replace(',',''))
    return spot

spot = troy_to_price()

def apmex():
  data = scraping('https://www.apmex.com/product/11934/1-kilo-gold-bar-various-mints')
  df = data[0][-1]
  soup = data[1]
  apmex_data = {}
  apmex_data['Product Name'] = soup.find("h1", {"class": "product-title"}).get_text().strip()
  try:
    apmex_data['Price'] = float(list(df[df.keys()[1]])[0].split('$')[1].replace(",", ""))
    apmex_data['Crypto Price'] = float(list(df[df.keys()[2]])[0].split('$')[1].replace(",", ""))
    apmex_data['CC/PayPal Price'] = float(list(df[df.keys()[3]])[0].split('$')[1].replace(",", ""))
    unit_price = spot * 32.15
    difference = abs(int(apmex_data['Price']) - unit_price)
    apmex_data['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    apmex_data['Price'] = None
    apmex_data['Crypto Price'] = None
    apmex_data['CC/PayPal Price'] = None
    apmex_data['Premium'] = None
  apmex_data['Product Id']=soup.find("ul", {"class": "product-table left"}).get_text().split("\n")[1].split(":")[1].strip()
  apmex_data['Metal Content']=soup.find("ul", {"class": "product-table left"}).get_text().split("\n")[6].split(":")[1].strip()
  apmex_data['Purity'] = soup.find_all("ul", {"class": "product-table"})[1].get_text().split("\n")[1].split(":")[1].strip()
  apmex_data['Manufacture'] = None
  apmex_data['Product URL'] = 'https://www.apmex.com/product/11934/1-kilo-gold-bar-various-mints'
  apmex_data['Supplier name'] = 'APMEX'
  apmex_data['Supplier Country'] = 'Singapore'
  apmex_data['Weight'] = '1000 G'

  return apmex_data

def jmbullion():
  data = scraping('https://www.jmbullion.com/1-kilo-valcambi-cast-gold-bar/')
  dfs = data[0]
  soup = data[1]
  print(dfs[0][1][3])
  jmbullion_data = {}
  jmbullion_data['Product Name'] = soup.find("div", {"class": "title-area"}).get_text().strip()
  unit_price = spot * 32.15
  try:
    jmbullion_data['Price'] = float(list(dfs[1][dfs[1].keys()[1]])[0].split('$')[1].replace(",", ""))
    jmbullion_data['Crypto Price'] = float(list(dfs[1][dfs[1].keys()[2]])[0].split('$')[1].replace(",", ""))
    jmbullion_data['CC/PayPal Price'] = float(list(dfs[1][dfs[1].keys()[3]])[0].split('$')[1].replace(",", ""))
    jmbullion_data['Product Id']=list(dfs[2][dfs[2].keys()[1]])[0]
    difference = abs(int(jmbullion_data['Price']) - unit_price)
    jmbullion_data['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    jmbullion_data['Price'] = None
    jmbullion_data['Crypto Price'] = None
    jmbullion_data['CC/PayPal Price'] = None
    jmbullion_data['Product Id'] = None
  jmbullion_data['Metal Content'] = math.ceil(float(dfs[0][1][9].split()[0]) * 31.103)
  jmbullion_data['Purity'] = dfs[0][1][2]
  jmbullion_data['Manufacture'] = dfs[0][1][3]
  jmbullion_data['Product URL'] = 'https://www.jmbullion.com/1-kilo-valcambi-cast-gold-bar/'
  jmbullion_data['Supplier name'] = 'JMBullion'
  jmbullion_data['Supplier Country'] = 'USA'
  jmbullion_data['Weight'] = '1000 G'

  return jmbullion_data


def achat():
  data = scraping('https://www.achat-or-et-argent.fr/or/lingot-1kg/38')
  dfs = data[0]
  soup = data[1]
  achat_data = {}
  c = CurrencyRates()
  Currency = c.get_rate('EUR', 'USD')
  try:
    achat_data['Price'] = round(float(dfs[1]['Prix unitaire net'][0].replace(" ", "")), 2)
    achat_data['Price'] = Currency * achat_data['Price']
    achat_data['Crypto Price'] = None
    achat_data['CC/PayPal Price'] = None
    unit_price = spot * 32.15
    difference = abs(int(achat_data['Price']) - unit_price)
    achat_data['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    achat_data['Price'] = None
    achat_data['Crypto Price'] = None
    achat_data['CC/PayPal Price'] = None
    achat_data['Premium'] = None
  achat_data['Product Id']=None
  achat_data['Metal Content']=None
  achat_data['Purity'] = dict(dfs[0][1])[2]
  achat_data['Manufacture'] = None
  achat_data['Product URL'] = 'https://www.achat-or-et-argent.fr/or/lingot-1kg/38'
  achat_data['Supplier name'] = 'achat'
  achat_data['Supplier Country'] = 'USA'
  achat_data['Product Name']='LINGOT 1KG OR'
  achat_data['Weight'] = '1000 G'

  return achat_data


def bullionstar():
  data = scraping('https://www.bullionstar.com/buy/product/gold-bar-abc-cast-1kg')
  df = data[0][-1]
  soup = data[1]
  bullionstar_data = {}
  #use selenium for price scrap remove class div default hide and fetch price from td class price
  bullionstar_data['Product Name'] = soup.find("div", {"class": "prices"}).get_text().strip().split("\n")[0]
  price = requests.get('https://services.bullionstar.com/product/v2/prices?currency=USD&locationId=1&productIds=4429&_=1651425210368')
  stock = soup.find("p", {"class": "status"}).get_text(strip=True)
  unit_price = spot * 32.15
  if stock != "OUT OF STOCK":
    bullionstar_data['Price'] = price.json()['products'][0]['price'].split(' ')[1].replace(',','')
    bullionstar_data['Crypto Price'] = None
    bullionstar_data['CC/PayPal Price'] = None
    difference = abs(float(bullionstar_data['Price']) - unit_price)
    bullionstar_data['Premium'] = round((difference / unit_price) * 100, 2)
  else:
    bullionstar_data['Price'] = None
    bullionstar_data['Crypto Price'] = None
    bullionstar_data['CC/PayPal Price'] = None
    bullionstar_data['Premium'] = None
  bullionstar_data['Product Id']= None
  bullionstar_data['Metal Content']= None
  bullionstar_data['Purity'] = soup.find("div", {"class": "product-highlight"}).get_text().split('Purity:')[1].split('\n')[0].strip()
  bullionstar_data['Manufacture'] = None
  bullionstar_data['Product URL'] = 'https://www.bullionstar.com/buy/product/gold-bar-abc-cast-1kg'
  bullionstar_data['Supplier name'] = 'Bullion Star'
  bullionstar_data['Supplier Country'] = 'Singapore'
  bullionstar_data['Weight'] = '1000 G'

  return bullionstar_data

def indigopreciousmetals():
  data = scraping('https://www.indigopreciousmetals.com/bullion-products/gold/gold-bars/1-kilo-gold-lbma-good-delivery-bars-indigo-precious-metals.html')
  df = data[0][-1]
  soup = data[1]
  indigo = {}
  indigo['Product Name'] = soup.find("div", {"class": "product-name"}).get_text().split("\n")[1]
  try:
    indigo['Crypto Price'] = None
    indigo['Price'] = float(soup.find("span", {"id": "product-minimal-price-1805"}).get_text(strip=True).split(" ")[0].replace(",", ""))
    indigo['CC/PayPal Price'] = None
    unit_price = spot * 32.15
    difference = abs(int(indigo['Price']) - unit_price)
    indigo['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    indigo['Crypto Price'] = None
    indigo['Price'] = None
    indigo['CC/PayPal Price'] = None
    indigo['Premium'] = None
  indigo['Product Id']= None
  indigo['Metal Content']= None
  indigo['Manufacture'] = None
  indigo['Purity'] = soup.find("div", {"class": "specifications"}).get_text().split("\n")[18].split("\t")[2].strip()
  indigo['Product URL'] = 'https://www.indigopreciousmetals.com/bullion-products/gold/gold-bars/1-kilo-gold-lbma-good-delivery-bars-indigo-precious-metals.html'
  indigo['Supplier name'] = 'Indigo precious metals'
  indigo['Supplier Country'] = 'Singapore'
  indigo['Weight'] = '1000 G'

  return indigo

def sdbullion():
  data = scraping('https://sdbullion.com/generic-gold-kilo-bar')
  df = data[0][-1]
  soup = data[1]
  sdbullion = {}
  sdbullion['Product Name'] = soup.find("div", {"class": "page-title-wrapper"}).get_text()
  try:
    sdbullion['Price'] = float(data[0][0]['Check / Wire'][0].split("$")[1].replace(",",""))
    sdbullion['Crypto Price'] = float(data[0][0]['Bitcoin'][0].split("$")[1].replace(",",""))
    sdbullion['CC/PayPal Price'] = float(data[0][0]['Credit / PayPal'][0].split("$")[1].replace(",",""))
    unit_price = spot * 32.15
    difference = abs(int(sdbullion['Price']) - unit_price)
    sdbullion['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    sdbullion['Price'] = None
    sdbullion['Crypto Price'] = None
    sdbullion['CC/PayPal Price'] = None
    sdbullion['Premium'] = None
  sdbullion['Product Id']= None
  sdbullion['Metal Content']=list(data[0][-1][1])[3]
  sdbullion['Purity'] = list(data[0][-1][1])[5]
  sdbullion['Product URL'] = 'https://sdbullion.com/generic-gold-kilo-bar'
  sdbullion['Manufacture'] = None
  sdbullion['Supplier name'] = 'SDbullion'
  sdbullion['Supplier Country'] = 'USA'
  sdbullion['Weight'] = '1000 G'

  return sdbullion

def bullion():
  data = scraping('https://www.bullionbypost.eu/gold-bars/1-kilo-gold-bar/1kg-gold-bar-value/')
  soup = data[1]
  c = CurrencyRates()
  Currency = c.get_rate('EUR', 'USD')
  bullion = {}
  bullion['Manufacture'] = soup.find("div", {"class": "col product-specifications"}).get_text().split(':')[1].split('\n')[0]
  bullion['Purity'] = soup.find("div", {"class": "col product-specifications"}).get_text().split('\n')[4].split(':')[1]
  try:
    bullion['Price'] = soup.find("td", {"id": "price-per-unit-1"}).get_text(strip=True)
    bullion['Price'] = unicodedata.normalize("NFKD",bullion['Price']).split('€')[0].strip()
    bullion['Price'] = float(bullion['Price'].replace(" ", ""))
    bullion['Price'] = Currency * bullion['Price']
    unit_price = spot * 32.15
    difference = abs(int(bullion['Price']) - unit_price)
    bullion['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    bullion['Price'] = None
    bullion['Premium'] = None
  bullion['Crypto Price'] = None
  bullion['CC/PayPal Price'] = None
  bullion['Product Name'] = soup.find("h1", {"class": "page-title"}).get_text()
  bullion['Supplier Country'] = "France"
  bullion['Product URL'] = "https://www.bullionbypost.eu/gold-bars/1-kilo-gold-bar/1kg-gold-bar-value/"
  bullion['Metal Content'] = None
  bullion['Product Id'] = None
  bullion['Supplier name'] = "bullionbypost"
  bullion['Weight'] = '1000 G'

  return bullion

def goldcentral():
  data = scraping('https://www.goldsilvercentral.com.sg/shop/buy-gold/lbma-good-delivery-gold-bar-1kg/')
  dfs = data[0][3]
  soup = data[1]
  c = CurrencyRates()
  Currency = c.get_rate('SGD', 'USD')
  goldcentral = {}
  try:
    goldcentral['Price'] = float(dfs['Price'][0].split("$")[1].replace(",", ""))
    goldcentral['Price'] = Currency * goldcentral['Price']
    unit_price = spot * 32.15
    difference = abs(int(goldcentral['Price']) - unit_price)
    goldcentral['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    goldcentral['Price'] = None
    goldcentral['Premium'] = None
  goldcentral['Crypto Price'] = None
  goldcentral['CC/PayPal Price'] = None
  goldcentral['Product Name'] = soup.find("h1", {"class": "product_title entry-title"}).get_text()
  goldcentral['Supplier Country'] = "Singapore"
  goldcentral['Product URL'] = "https://www.goldsilvercentral.com.sg/shop/buy-gold/lbma-good-delivery-gold-bar-1kg/"
  goldcentral['Manufacture'] = None
  purity = soup.find("div", {"class":"kw-details-desc"}).get_text().split('purity of')[1].split('%')[0]
  goldcentral['Purity'] = float(purity.strip()) * 100
  goldcentral['Supplier name'] = "Gold Silver Central"
  goldcentral['Metal Content'] = None
  goldcentral['Product Id'] = None
  goldcentral['Weight'] = '1000 G'

  return goldcentral

def kitco():
  data = scraping('https://online.kitco.com/buy/2014/1-kg-Gold-Good-Delivery-List-Bar-9999-2014')
  dfs = data[0][0]
  soup = data[1]
  kitco = {}
  try:
    kitco['Price'] = float(dfs['Wire/Check'][0].split('$')[1].replace(",", ""))
    unit_price = spot * 32.15
    difference = abs(int(kitco['Price']) - unit_price)
    kitco['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    kitco['Price'] = None
    kitco['Premium'] = None
  kitco['Product Name'] = soup.find("section", {"id": "prod_desc_section"}).get_text().split('\n')[1].split('Buying')[0]
  kitco['Crypto Price'] = None
  kitco['CC/PayPal Price'] = None
  kitco['Metal Content'] = soup.find("ul", {"id": "prod_details_list"}).get_text().split(':')[1].strip().split('\r')[0]
  kitco['Product Id'] = None
  kitco['Product URL'] = "https://online.kitco.com/buy/2014/Buy-Back-1-kg-Gold-Bar-9999-2014B"
  kitco['Supplier Country'] = "USA"
  kitco['Supplier name'] = "Kitco"
  kitco['Manufacture'] = None
  kitco['Purity'] = soup.find("ul", {"id": "prod_details_list"}).get_text().split('Fineness:')[1].strip().split('\r')[0]
  kitco['Weight'] = '1000 G'

  return kitco

def silverbullion():
  data = scraping('https://www.silverbullion.com.sg/Product/Detail/Gold_1_kg_Metalor_bar')
  dfs = data[0]
  soup = data[1]
  silverbullion = {}
  c = CurrencyRates()
  Currency = c.get_rate('SGD', 'USD')
  silverbullion['Product Name'] = soup.find('title').get_text().split('|')[0]
  try:
    silverbullion['Price'] = float(dfs[10]['Price(SGD)'][0].split(' ')[0].replace(",", ""))
    silverbullion['Price'] = Currency* silverbullion['Price']
    unit_price = spot * 32.15
    difference = abs(int(silverbullion['Price']) - unit_price)
    silverbullion['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    silverbullion['Price'] = None
    silverbullion['Premium'] = None
  silverbullion['Crypto Price'] = None
  silverbullion['CC/PayPal Price'] = None
  silverbullion['Product Id'] = None
  silverbullion['Metal Content'] = None
  silverbullion['Purity'] = soup.find("p", {"class": "sgi-size-material hidden-xs"}).get_text().strip().split('.')[1].split('Purity')[0]
  silverbullion['Manufacture'] = soup.find("p", {"class": "sgi-size-material hidden-xs"}).get_text().strip().split('.')[1].split('Refiner:')[1]
  silverbullion['Product URL'] = "https://www.silverbullion.com.sg/Product/Detail/Gold_1_kg_Metalor_bar"
  silverbullion['Supplier Country'] = "Singapore"
  silverbullion['Supplier name'] = "Silver Bullion"
  silverbullion['Weight'] = "1000 G"

  return silverbullion

def acheter():
  data = scraping('https://www.acheter-or-argent.fr/lingot-or-1000-g.html')
  dfs = data[0]
  soup = data[1]
  acheter = {}
  c = CurrencyRates()
  Currency = c.get_rate('EUR', 'USD')
  acheter['Product Name'] = soup.find("span", {"class": "fond"}).get_text(strip=True)
  acheter['Product Name'] = unicodedata.normalize("NFKD",acheter['Product Name'])
  try:
    acheter['Price'] = float(soup.find("span", {"class": "prixProduit"}).get_text(strip=True).split(" ")[0])
    acheter['Price'] = Currency * acheter['Price']
    unit_price = spot * 32.15
    difference = abs(int(acheter['Price']) - unit_price)
    acheter['Premium'] = round((difference / unit_price) * 100, 2)
  except:
    acheter['Price'] = None
    acheter['Premium'] = None
  acheter['Crypto Price'] = None
  acheter['CC/PayPal Price'] = None
  acheter['Product Id'] = None
  acheter['Metal Content'] = None
  acheter['Purity'] = soup.find("div", {"class": "description"}).get_text().split(':')[4].strip().split('/')[0]
  acheter['Manufacture'] = None
  acheter['Product URL'] = "https://www.acheter-or-argent.fr/lingot-or-1000-g.html"
  acheter['Supplier name'] = "Acheter-or-Argent"
  acheter['Supplier Country'] = "France"
  acheter['Weight'] = '1000 G'

  return acheter


def main_update():
  print("in Extracted")
  df_final = pd.DataFrame([apmex(),jmbullion(),achat(),bullionstar(),indigopreciousmetals(),sdbullion(), goldcentral(),kitco(),silverbullion(), acheter()])
  cols = df_final.columns.tolist()
  cols = cols[0:2] + [cols[9]] + cols[2:9] + cols[10:12] + [cols[12]]
  df_final = df_final[cols]
  df_final.fillna('NA',inplace=True)
  df_final.loc[df_final['Price'] == "NA", 'Stock'] = 'Out of Stock'
  df_final.loc[df_final['Price'] != "NA", 'Stock'] = 'In Stock'
  df_records = df_final.to_dict('records')
  model_instances = [Extracted(
      product_name=record['Product Name'],
      price_usd=record['Price'],
      crypto_price=record['Crypto Price'],
      paypal_price=record['CC/PayPal Price'], 
      weight = record['Weight'],
      premium = record['Premium'],
      product_id = record['Product Id'],
      metal_content = record['Metal Content'],
      purity = record['Purity'],
      manufacture = record['Manufacture'],
      product_url = record['Product URL'],
      supplier_name= record['Supplier name'],
      supplier_country = record['Supplier Country'],
      stock = record['Stock']
  ) for record in df_records]

  Extracted.objects.all().delete()

  Extracted.objects.bulk_create(model_instances)



