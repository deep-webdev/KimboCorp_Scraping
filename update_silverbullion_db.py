from cmath import e
import mysql.connector
import requests
import pandas as pd
from forex_python.converter import CurrencyRates
from bs4 import BeautifulSoup
from lxml.html import fromstring
from urllib.request import Request, urlopen
import concurrent.futures
import math

MAX_THREADS = 300


def get_cursor():
    connection = mysql.connector.connect(user='gold_scrap', database='gold_scrap', host='localhost', password="Gold_scrap@123", port='3306', auth_plugin='mysql_native_password')
    if connection.is_connected():
        print("CONECTTEDDDDDDDDDDD!!!!!!!")
        cursor = connection.cursor()
        return (connection,cursor)

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


def silverbul(url):
    try:
        data = scraping(url[0])
        dfs = data[0]
        soup = data[1]
        silverbullion = {}
        c = CurrencyRates()
        spot = troy_to_price()
        Currency = c.get_rate('SGD', 'USD')
        silverbullion['Product Name'] = soup.find('title').get_text().split('|')[0]
        try:
            silverbullion['Price'] = float(dfs[10]['Price(SGD)'][0].split(' ')[0].replace(",", ""))
            silverbullion['Price'] = Currency* silverbullion['Price']
            silverbullion['Crypto Price'] = None
            silverbullion['CC/PayPal Price'] = None
        except:
            silverbullion['Price'] = None
            silverbullion['Crypto Price'] = None
            silverbullion['CC/PayPal Price'] = None
        if silverbullion['Price']:
            silverbullion['Stock'] = "In Stock"
        else:
            silverbullion['Stock'] = "Out Of Stock"
        silverbullion['Product Id'] = None
        silverbullion['Metal Content'] = None
        try:
            silverbullion['W tz'] = dfs[8][0][0].split('oz')[0].strip().split('(')[1].strip()
        except:
            silverbullion['W tz'] = dfs[8][0][0].split('oz')[0].strip()
            if '|' in silverbullion['W tz'].split():
                silverbullion['W tz'] = dfs[8][0][0].split('oz')[0].split('|')[1].strip()
        if 'tolas' in silverbullion['W tz'].split():
            silverbullion['W tz'] = silverbullion['W tz'].split('tolas')[0].strip()
            tz = float(silverbullion['W tz'])
        else:      
            tz = convert_to_float(silverbullion['W tz'])
        try:
            if silverbullion['W tz'].split('/'):
                silverbullion['Weight'] = str(int(math.floor(tz * 31.103))) + " " + "grams"
        except:
            silverbullion['Weight'] = str(int(math.floor(silverbullion['W tz'] * 31.103))) + " " + "grams"
        unit_price = spot * tz
        difference = abs(int(silverbullion['Price']) - unit_price)
        silverbullion['Premium'] = round((difference / unit_price) * 100, 2)
        silverbullion['Purity'] = soup.find("p", {"class": "sgi-size-material hidden-xs"}).get_text().strip().split('.')[1].split('Purity')[0]
        silverbullion['Manufacture'] = soup.find("p", {"class": "sgi-size-material hidden-xs"}).get_text().strip().split('.')[1].split('Refiner:')[1]
        silverbullion['Product URL'] = url[0]
        silverbullion['Supplier name'] = "Silver Bullion"
        silverbullion['Supplier Country'] = "Singapore"
        del silverbullion['W tz']
    except Exception as e: 
        print('line 106 ------'+str(e))    
    try:
        connection,cursor = get_cursor()
        cursor.execute("SELECT * FROM gold_data WHERE Product_Name=%s" , [silverbullion['Product Name']] );
        data = cursor.fetchall()
    except Exception as e:
        print('line 111 ------'+str(e))

    if(data):
        try:
            my_query = """UPDATE gold_data SET Price=%s,Crypto_Price=%s,CC_PayPal_Price=%s,Stock=%s,Premium=%s WHERE Product_Name=%s ;""";
            record = [silverbullion['Price'], silverbullion['Crypto Price'], silverbullion['CC/PayPal Price'], silverbullion['Stock'],silverbullion['Premium'],silverbullion['Product Name']]
            connection,cursor = get_cursor()

            cursor.execute(my_query, record)
            connection.commit()
            cursor.close()
            connection.close()
            print(record)
            print("Update Sucess !!")
        except Exception as e:
            print('line 124 ------'+str(e))    
    
    else:
        try:
            my_query = """INSERT INTO gold_data (Product_Name,Price,Crypto_Price,CC_PayPal_Price,Stock,Product_Id,Metal_Content,Weight,Premium,Purity,Manufacture,Product_URL,Supplier_name,Supplier_Country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""";
            record = list(silverbullion.values())
            connection,cursor = get_cursor()
            cursor.execute(my_query, record)
            connection.commit()
            cursor.close()
            connection.close()
            print("Sucess !!")
        except Exception as e:
            print('line 137 ------'+str(e))


def main():
    print("IN main")
    connection,cursor = get_cursor()

    cursor.execute("SELECT url FROM url_and_supp WHERE supplier='Silverbullion'");
    data = cursor.fetchall()
    print(">>>>>>>>>>>>>>>>>", len(data), data[0][0])
    
    # suplier_list = [('Silverbullion','silverbullion'),('Goldcentral','urlsGoldcentral'),
    # ('Kitco','urlsKitco'),('Indigo','urlsIndigo'),('Apmex','urlsApmex'),('Sdbullion','urlSdbullion')]
    threads = min(MAX_THREADS, len(data))

    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(silverbul, data)

main()