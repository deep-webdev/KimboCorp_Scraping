from forex_python.converter import CurrencyRates
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from lxml.html import fromstring
import unicodedata
from gold_scrap.models import Extracted


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

def apmex(url):
  # data = scraping('https://www.apmex.com/product/11934/1-kilo-gold-bar-various-mints')
  data = scraping(url)
  df = data[0][-1]
  soup = data[1]
  apmex_data = {}
  apmex_data['Product Name'] = soup.find("h1", {"class": "product-title"}).get_text().strip()
  apmex_data['Price'] = float(list(df[df.keys()[1]])[0].split('$')[1].replace(",", ""))
  apmex_data['Crypto Price'] = float(list(df[df.keys()[2]])[0].split('$')[1].replace(",", ""))
  apmex_data['CC/PayPal Price'] = float(list(df[df.keys()[3]])[0].split('$')[1].replace(",", ""))
  apmex_data['Product Id']=soup.find("ul", {"class": "product-table left"}).get_text().split("\n")[1].split(":")[1].strip()
  apmex_data['Metal Content']=soup.find("ul", {"class": "product-table left"}).get_text().split("\n")[6].split(":")[1].strip()
  apmex_data['Purity'] = soup.find_all("ul", {"class": "product-table"})[1].get_text().split("\n")[1].split(":")[1].strip()
  apmex_data['Manufacture'] = None
  #apmex_data['Product URL'] = 'https://www.apmex.com/product/11934/1-kilo-gold-bar-various-mints'
  apmex_data['Product URL'] = url
  apmex_data['Supplier name'] = 'APMEX'
  apmex_data['Supplier Country'] = 'Singapore'
  apmex_data['Weight'] = '1000 G'
  # apmex_data['Weight'] = soup.find("ul", {"class":"product-table left"}).get_text().split('Denomination:')[1].split('\n')[0].strip()
  return apmex_data

def jmbullion():
  data = scraping('https://www.jmbullion.com/1-kilo-valcambi-cast-gold-bar/')
  dfs = data[0]
  soup = data[1]
  jmbullion_data = {}
  jmbullion_data['Product Name'] = soup.find("div", {"class": "title-area"}).get_text().strip()
  jmbullion_data['Price'] = float(list(dfs[1][dfs[1].keys()[1]])[0].split('$')[1].replace(",", ""))
  jmbullion_data['Crypto Price'] = float(list(dfs[1][dfs[1].keys()[2]])[0].split('$')[1].replace(",", ""))
  jmbullion_data['CC/PayPal Price'] = float(list(dfs[1][dfs[1].keys()[3]])[0].split('$')[1].replace(",", ""))
  jmbullion_data['Product Id']=list(dfs[2][dfs[2].keys()[1]])[0]
  jmbullion_data['Metal Content']=list(dfs[2][dfs[2].keys()[1]])[9]
  jmbullion_data['Purity'] = list(dfs[2][dfs[2].keys()[1]])[2]
  jmbullion_data['Manufacture'] = list(dfs[2][dfs[2].keys()[1]])[3]
  jmbullion_data['Product URL'] = 'https://www.jmbullion.com/1-kilo-valcambi-cast-gold-bar/'
  jmbullion_data['Supplier name'] = 'JMBullion'
  jmbullion_data['Supplier Country'] = 'USA'
  jmbullion_data['Weight'] = '1000 G'

  # jmbullion_data['Weight'] = soup.find("div", {"class": "specification-detail"}).get_text().split('Today,')[1].split('Valcambi')[0].strip()
  return jmbullion_data


def achat():
  data = scraping('https://www.achat-or-et-argent.fr/or/lingot-1kg/38')
  dfs = data[0]
  soup = data[1]
  achat_data = {}
  c = CurrencyRates()
  Currency = c.get_rate('EUR', 'USD')
  achat_data['Price'] = float(dfs[1]['Prix unitaire net'][0].replace(" ", ""))
  achat_data['Price'] = Currency * achat_data['Price']
  achat_data['Crypto Price'] = None
  achat_data['CC/PayPal Price'] = None
  achat_data['Product Id']=None
  achat_data['Metal Content']=None
  achat_data['Purity'] = dict(dfs[0][1])[2]
  achat_data['Manufacture'] = None
  achat_data['Product URL'] = 'https://www.achat-or-et-argent.fr/or/lingot-1kg/38'
  achat_data['Supplier name'] = 'achat'
  achat_data['Supplier Country'] = 'USA'
  achat_data['Product Name']='LINGOT 1KG OR'
  achat_data['Weight'] = '1000 G'

  # achat_data['Weight'] =  dict(dfs[0][1])[1]

  return achat_data


def bullionstar():
  data = scraping('https://www.bullionstar.com/buy/product/gold-bar-abc-cast-1kg')
  df = data[0][-1]
  soup = data[1]
  bullionstar_data = {}
  #use selenium for price scrap remove class div default hide and fetch price from td class price
  bullionstar_data['Product Name'] = soup.find("div", {"class": "prices"}).get_text().strip().split("\n")[0]
  price = requests.get('https://services.bullionstar.com/product/v2/prices?currency=USD&locationId=1&productIds=4429&_=1651425210368')
  bullionstar_data['Price'] = price.json()['products'][0]['price'].split(' ')[1].replace(',','')

  bullionstar_data['Crypto Price'] = None
  bullionstar_data['CC/PayPal Price'] = None
  bullionstar_data['Product Id']= None
  bullionstar_data['Metal Content']= None
  bullionstar_data['Purity'] = soup.find("div", {"class": "product-highlight"}).get_text().split('Purity:')[1].split('\n')[0].strip()
  bullionstar_data['Manufacture'] = None
  bullionstar_data['Product URL'] = 'https://www.bullionstar.com/buy/product/gold-bar-abc-cast-1kg'
  bullionstar_data['Supplier name'] = 'Bullion Star'
  bullionstar_data['Supplier Country'] = 'Singapore'
  bullionstar_data['Weight'] = '1000 G'

  # bullionstar_data['Weight'] = soup.find("div",{"class": "product-highlight"}).get_text().split('Weight:')[1].split('(')[0].strip()
  return bullionstar_data

def indigopreciousmetals():
  data = scraping('https://www.indigopreciousmetals.com/bullion-products/gold/gold-bars/1-kilo-gold-lbma-good-delivery-bars-indigo-precious-metals.html')
  df = data[0][-1]
  soup = data[1]
  indigo = {}
  indigo['Product Name'] = soup.find("div", {"class": "product-name"}).get_text().split("\n")[1]
  indigo['Crypto Price'] = None
  indigo['Price'] = float(soup.find("span", {"id": "product-minimal-price-1805"}).get_text(strip=True).split(" ")[0].replace(",", ""))
  indigo['CC/PayPal Price'] = None
  indigo['Product Id']= None
  indigo['Metal Content']= None
  indigo['Manufacture'] = None
  indigo['Purity'] = soup.find("div", {"class": "specifications"}).get_text().split("\n")[18].split("\t")[2]
  indigo['Product URL'] = 'https://www.indigopreciousmetals.com/bullion-products/gold/gold-bars/1-kilo-gold-lbma-good-delivery-bars-indigo-precious-metals.html'
  indigo['Supplier name'] = 'Indigo precious metals'
  indigo['Supplier Country'] = 'Singapore'
  indigo['Weight'] = '1000 G'

  # indigo['Weight'] = soup.find("div", {"class":"specifications"}).get_text(strip=True).split('Country')[0].split('Weight')[1]  
  return indigo

def sdbullion():
  data = scraping('https://sdbullion.com/generic-gold-kilo-bar')
  df = data[0][-1]
  soup = data[1]
  sdbullion = {}
  sdbullion['Product Name'] = soup.find("div", {"class": "page-title-wrapper"}).get_text()
  sdbullion['Price'] = float(data[0][0]['Check / Wire'][0].split("$")[1].replace(",",""))
  sdbullion['Crypto Price'] = float(data[0][0]['Bitcoin'][0].split("$")[1].replace(",",""))
  sdbullion['CC/PayPal Price'] = float(data[0][0]['Credit / PayPal'][0].split("$")[1].replace(",",""))
  sdbullion['Product Id']= None
  sdbullion['Metal Content']=list(data[0][-1][1])[3]
  sdbullion['Purity'] = list(data[0][-1][1])[5]
  sdbullion['Product URL'] = 'https://sdbullion.com/generic-gold-kilo-bar'
  sdbullion['Manufacture'] = None
  sdbullion['Supplier name'] = 'SDbullion'
  sdbullion['Supplier Country'] = 'USA'
  sdbullion['Weight'] = '1000 G'

  # sdbullion['Weight'] = soup.find("h1", {"class":"page-title"}).get_text().split("Gold")[0].strip()
  return sdbullion

def bullion():
  data = scraping('https://www.bullionbypost.eu/gold-bars/1-kilo-gold-bar/1kg-gold-bar-value/')
  # dfs = data[0][-1]
  soup = data[1]
  c = CurrencyRates()
  Currency = c.get_rate('EUR', 'USD')
  bullion = {}
  bullion['Manufacture'] = soup.find("div", {"class": "col product-specifications"}).get_text().split(':')[1].split('\n')[0]
  bullion['Purity'] = soup.find("div", {"class": "col product-specifications"}).get_text().split('\n')[4].split(':')[1]
  bullion['Price'] = soup.find("td", {"id": "price-per-unit-1"}).get_text(strip=True)
  bullion['Price'] = unicodedata.normalize("NFKD",bullion['Price']).split('€')[0].strip()
  bullion['Price'] = float(bullion['Price'].replace(" ", ""))
  bullion['Price'] = Currency * bullion['Price']
  bullion['Crypto Price'] = None
  bullion['CC/PayPal Price'] = None
  bullion['Product Name'] = soup.find("h1", {"class": "page-title"}).get_text()
  bullion['Supplier Country'] = "France"
  # bullion['stock'] = soup.find("div", {"class": "col product-specifications"}).get_text().split(':')[6].split('\n')[1]
  bullion['Product URL'] = "https://www.bullionbypost.eu/gold-bars/1-kilo-gold-bar/1kg-gold-bar-value/"
  bullion['Metal Content'] = None
  bullion['Product Id'] = None
  bullion['Supplier name'] = "bullionbypost"
  bullion['Weight'] = '1000 G'

  # bullion['Weight'] = soup.find("div", {"class":"col product-specifications"}).get_text().split('(grams):')[1].split('\n')[0]
  return bullion

def goldcentral():
  data = scraping('https://www.goldsilvercentral.com.sg/shop/buy-gold/lbma-good-delivery-gold-bar-1kg/')
  dfs = data[0][3]
  soup = data[1]
  c = CurrencyRates()
  Currency = c.get_rate('SGD', 'USD')
  goldcentral = {}
  goldcentral['Price'] = float(dfs['Price'][0].split("$")[1].replace(",", ""))
  goldcentral['Price'] = Currency * goldcentral['Price']
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

  # goldcentral['Weight'] = soup.find("h1", {"class":"product_title entry-title"}).get_text().split(" ")[5]
  return goldcentral

def kitco():
  data = scraping('https://online.kitco.com/buy/2014/1-kg-Gold-Good-Delivery-List-Bar-9999-2014')
  dfs = data[0][0]
  soup = data[1]
  kitco = {}
  kitco['Price'] = float(dfs['Wire/Check'][0].split('$')[1].replace(",", ""))
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
  # kitco['Weight'] = soup.find("section", {"id": "prod_desc_section"}).get_text().split('Gold')[0].split('Buy')[1].strip()
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
  silverbullion['Price'] = float(dfs[10]['Price(SGD)'][0].split(' ')[0].replace(",", ""))
  silverbullion['Price'] = Currency* silverbullion['Price']
  silverbullion['Crypto Price'] = None
  silverbullion['CC/PayPal Price'] = None
  silverbullion['Product Id'] = None
  silverbullion['Metal Content'] = None
  silverbullion['Purity'] = soup.find("p", {"class": "sgi-size-material hidden-xs"}).get_text().strip().split('.')[1].split('Purity')[0]
  silverbullion['Manufacture'] = soup.find("p", {"class": "sgi-size-material hidden-xs"}).get_text().strip().split('.')[1].split('Refiner:')[1]
  silverbullion['Product URL'] = "https://www.silverbullion.com.sg/Product/Detail/Gold_1_kg_Metalor_bar"
  silverbullion['Supplier Country'] = "Singapore"
  silverbullion['Supplier name'] = "Silver Bullion"
  # silverbullion['Stock'] = soup.find("p", {"class": "item-available"}).get_text().split(':')[1]
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
  acheter['Price'] = float(soup.find("span", {"class": "prixProduit"}).get_text(strip=True).split(" ")[0])
  acheter['Price'] = Currency * acheter['Price']
  acheter['Crypto Price'] = None
  acheter['CC/PayPal Price'] = None
  acheter['Product Id'] = None
  acheter['Metal Content'] = None
  acheter['Purity'] = soup.find("div", {"class": "description"}).get_text().split(':')[4].strip().split('/')[0]
  acheter['Manufacture'] = None
  acheter['Product URL'] = "https://www.acheter-or-argent.fr/lingot-or-1000-g.html"
  acheter['Supplier name'] = "Acheter-or-Argent"
  acheter['Supplier Country'] = "France"
  # acheter['Weight'] = soup.find("div", {"class": "description"}).get_text().split('Poids :')[1].split('\n')[0].strip()
  acheter['Weight'] = '1000 G'

  return acheter


def main_update():
    df_final = pd.DataFrame([apmex('https://www.apmex.com/product/11934/1-kilo-gold-bar-various-mints'),jmbullion(),achat(),bullionstar(),indigopreciousmetals(),sdbullion(), goldcentral(),kitco(),silverbullion(), acheter()])
    cols = df_final.columns.tolist()
    cols = cols[0:2] + [cols[9]] + cols[2:9] + cols[10:12]
    df_final = df_final[cols]
    df_final.fillna('NA',inplace=True)
    df_final['Price'] = df_final['Price'].replace(' ',0)
    df_final['Crypto Price'] = df_final['Crypto Price'].replace('NA',0)
    df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace('NA',0)
    df_final['Price'] = df_final['Price'].astype(float).astype(int)
    df_final['Crypto Price'] = df_final['Crypto Price'].astype(int)
    df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].astype(int)
    df_final['Price'] = df_final['Price'].replace(0,'NA')
    df_final['Crypto Price'] = df_final['Crypto Price'].replace(0,'NA')
    df_final['CC/PayPal Price'] = df_final['CC/PayPal Price'].replace(0,'NA')
    df_records = df_final.to_dict('records')
    print(df_final.keys())
    model_instances = [Extracted(
        product_name=record['Product Name'],
        price_usd=record['Price'],
        crypto_price=record['Crypto Price'],
        paypal_price=record['CC/PayPal Price'], 
        weight = record['Weight'],
        product_id = record['Product Id'],
        metal_content = record['Metal Content'],
        purity = record['Purity'],
        manufacture = record['Manufacture'],
        product_url = record['Product URL'],
        supplier_name= record['Supplier name'],
        supplier_country = record['Supplier Country']
    ) for record in df_records]

    Extracted.objects.bulk_create(model_instances)



