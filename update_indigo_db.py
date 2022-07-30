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
    connection = mysql.connector.connect(user='root', database='gold_scrap', host='127.0.0.1', password="", port='3306')
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


def indigofetch(url):
    try:
        spot = troy_to_price()
        data = scraping(url[0])
        df = data[0]
        soup = data[1]
        indigo = {}
        indigo['Product Name'] = soup.find("div", {"class": "product-name"}).get_text().split("\n")[1]
        try:
            indigo['Price'] = float(df[0]['Prices'][0].split('USD')[0].strip().replace(",",""))
            indigo['Crypto Price'] = None
        except:
            indigo['Price'] = float(soup.find_all('span','price')[5].get_text().split()[0].replace(",",""))
            indigo['Crypto Price'] = None
        indigo['CC/PayPal Price'] = None
        if indigo['Price']:
            indigo['Stock'] = "In Stock"
        else:
            indigo['Stock'] = "Out Of Stock"
        indigo['Product Id']= None
        indigo['Metal Content']= soup.find("div", {"class":"specifications"}).get_text(strip=True).split('Country')[0].split('Weight')[1]

        if 'KG' in indigo['Metal Content'].split():
            content = convert_to_float(indigo['Metal Content'].split()[0]) * 0.035274 *1000
        elif 'grams' in indigo['Metal Content'].split():
            content = convert_to_float(indigo['Metal Content'].split()[0]) * 0.035274
        indigo['Weight'] = indigo['Metal Content']
        # indigo['Weight'] = str(float(convert_to_float(content)) * (1/0.035274)) + 'grams'
        unit_price = float(spot) * float(convert_to_float(content))
        if indigo['Price']: 
            difference = abs(int(indigo['Price']) - unit_price)
            indigo['Premium'] = round((difference / unit_price) * 100, 2)
        else:   
            indigo['Premium'] = 'NA'
        try:
            line = soup.find("ul", {"class": "spec-list"}).get_text(strip=True)
            regex = re.compile('Purity([0-9]*)')
            indigo['Purity'] = regex.findall(line)[0]
        except:
            indigo['Purity'] = None
        indigo['Manufacture'] = None
        indigo['Product URL'] = url[0]
        indigo['Supplier name'] = 'Indigo precious metals'
        indigo['Supplier Country'] = 'Singapore'
        # print("-----------------Indigo---------", indigo)
    except Exception as e: 
        print('line 106 ------'+str(e))   
    try:
        connection,cursor = get_cursor()
        cursor.execute("SELECT * FROM gold_data WHERE Product_Name=%s" , [indigo['Product Name']] );
        data = cursor.fetchall()
    except Exception as e:
        print('line 111 ------'+str(e))

    if(data):
        try:
            my_query = """UPDATE gold_data SET Price=%s,Crypto_Price=%s,CC_PayPal_Price=%s,Stock=%s,Premium=%s WHERE Product_Name=%s ;""";
            record = [indigo['Price'], indigo['Crypto Price'], indigo['CC/PayPal Price'], indigo['Stock'],indigo['Premium'],indigo['Product Name']]
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
            record = list(indigo.values())
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

    cursor.execute("SELECT url FROM url_and_supp WHERE supplier='Indigo'");
    data = cursor.fetchall()
    print(">>>>>>>>>>>>>>>>>", len(data), data[0][0])
    
    # suplier_list = [('Silverbullion','silverbullion'),('Goldcentral','urlsGoldcentral'),
    # ('Kitco','urlsKitco'),('Indigo','urlsIndigo'),('Apmex','urlsApmex'),('Sdbullion','urlSdbullion')]
    threads = min(MAX_THREADS, len(data))

    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(indigofetch, data)

main()