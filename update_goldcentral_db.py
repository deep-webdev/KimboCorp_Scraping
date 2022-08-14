from cmath import e
import mysql.connector
import requests
import pandas as pd
from forex_python.converter import CurrencyRates
from bs4 import BeautifulSoup
from lxml.html import fromstring
from urllib.request import Request, urlopen
import concurrent.futures
import re

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


def goldcentral(url):
    try:
        data = scraping(url[0])
        dfs = data[0][3]
        soup = data[1]
        spot = troy_to_price()
        c = CurrencyRates()
        Currency = c.get_rate('SGD', 'USD')
        goldcentral = {}
        goldcentral['Product Name'] = soup.find("h1", {"class": "product_title entry-title"}).get_text()
        try:
            goldcentral['Price'] = float(soup.find("span", {"class":"amount"}).get_text().replace('$','').replace(',',''))
            goldcentral['Price'] = round(Currency * goldcentral['Price'])
        except:  
            goldcentral['Price'] = None
        goldcentral['Crypto Price'] = None
        goldcentral['CC/PayPal Price'] = None
        if goldcentral['Price']:
            goldcentral['Stock'] = "In Stock"
        else:
            goldcentral['Stock'] = "Out Of Stock"
        goldcentral['Product Id'] = None
        try:
            goldcentral['Metal Content'] = soup.find("td", {"class":"product_weight"}).get_text()
            content = convert_to_float(goldcentral['Metal Content'].split()[0])
        except:  
            goldcentral['Metal Content'] = None
            content = 0
        try:
            goldcentral['Weight'] = soup.find("td", {"class":"product_weight"}).get_text()
            goldcentral['Weight'] = str(round(float(goldcentral['Weight'].split('oz')[0]) * 31.103, 2)) + " " + "grams"
        except: 
            goldcentral['Weight'] = None
        unit_price = float(spot) * float(convert_to_float(content))
        if goldcentral['Price'] and content != 0: 
            difference = abs(int(goldcentral['Price']) - unit_price)
            goldcentral['Premium'] = round((difference / unit_price) * 100, 2)
        else:   
            goldcentral['Premium'] = 'NA'
        try:
            purity = soup.find("div", {"class":"kw-details-desc"}).get_text().split('purity of')[1].split('%')[0]
            goldcentral['Purity'] = float(purity.strip()) * 100
        except:
            goldcentral['Purity'] = None
        goldcentral['Manufacture'] = None
        goldcentral['Product URL'] = url[0]
        goldcentral['Supplier name'] = "Gold Silver Central"
        goldcentral['Supplier Country'] = "Singapore"
    except Exception as e: 
        print('line 106 ------'+str(e))    
    try:
        connection,cursor = get_cursor()
        cursor.execute("SELECT * FROM gold_data WHERE Product_Name=%s" , [goldcentral['Product Name']] );
        data = cursor.fetchall()
    except Exception as e:
        print('line 111 ------'+str(e))

    if(data):
        try:
            my_query = """UPDATE gold_data SET Price=%s,Crypto_Price=%s,CC_PayPal_Price=%s,Stock=%s,Premium=%s WHERE Product_Name=%s ;""";
            record = [goldcentral['Price'], goldcentral['Crypto Price'], goldcentral['CC/PayPal Price'], goldcentral['Stock'],goldcentral['Premium'],goldcentral['Product Name']]
            connection,cursor = get_cursor()

            cursor.execute(my_query, record)
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            print('line 124 ------'+str(e))    
    
    else:
        try:
            my_query = """INSERT INTO gold_data (Product_Name,Price,Crypto_Price,CC_PayPal_Price,Stock,Product_Id,Metal_Content,Weight,Premium,Purity,Manufacture,Product_URL,Supplier_name,Supplier_Country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""";
            record = list(goldcentral.values())
            connection,cursor = get_cursor()
            cursor.execute(my_query, record)
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            print('line 137 ------'+str(e))


def main():
    print("IN main")
    connection,cursor = get_cursor()

    cursor.execute("SELECT url FROM url_and_supp WHERE supplier='Goldcentral'");
    data = cursor.fetchall()
    
    # suplier_list = [('Silverbullion','silverbullion'),('Goldcentral','urlsGoldcentral'),
    # ('Kitco','urlsKitco'),('Indigo','urlsIndigo'),('Apmex','urlsApmex'),('Sdbullion','urlSdbullion')]
    threads = min(MAX_THREADS, len(data))

    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(goldcentral, data)

main()