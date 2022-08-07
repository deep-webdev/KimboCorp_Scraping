import mysql.connector
import requests
import pandas as pd
from forex_python.converter import CurrencyRates
from bs4 import BeautifulSoup
from lxml.html import fromstring
from urllib.request import Request, urlopen
import concurrent.futures

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


def sdb(url):
    try:
        data = scraping(url[0])
        df = data[0]
        soup = data[1]
        sbul = {}
        spot = troy_to_price()
        try:
            sbul['Product Name'] = soup.find("h1", {'class': 'page-title'}).get_text()
        except:
            sbul['Product Name'] = "NA"
        try:
            if not soup.find('p', {'class': 'currently-out-of-stock'}):
                sbul['Price'] = float(df[0]['Check / Wire'][0].split("$")[1].replace(",",""))
                sbul['Crypto Price'] = float(df[0]['Bitcoin'][0].split("$")[1].replace(",",""))
                sbul['CC/PayPal Price'] = float(df[0]['Credit / PayPal'][0].split("$")[1].replace(",",""))
                sbul['Stock'] = "In stock"
            else:
                sbul['Price'] = None
                sbul['Crypto Price'] = None
                sbul['CC/PayPal Price'] = None
                sbul['Stock'] = "Out of Stock"
        except:
            sbul['Price'] = None
            sbul['Crypto Price'] = None
            sbul['CC/PayPal Price'] = None
            sbul['Stock'] = "Out of Stock"
        sbul['Product Id'] = None
        sbul['Metal content'] = df[-1][1][3]
        wz = 0
        unit_price = 0
        try:
            if 'Troy Oz' in sbul['Metal content']:
                wz = float(sbul['Metal content'].split('Troy Oz')[0].strip())
                sbul['Weight'] = str(int(wz * 31.103)) + " " + "grams"
                unit_price = wz * spot
            elif 'Grams' in sbul['Metal content']:
                wz = float(sbul['Metal content'].split('Grams')[0]) / 31.103
                sbul['Weight'] = str(int(wz * 31.103)) + " " + "grams"
                unit_price = wz * spot
            elif 'Gram' in sbul['Metal content']:
                wz = float(sbul['Metal content'].split('Gram')[0]) / 31.103
                sbul['Weight'] = str(int(wz * 31.103)) + " " + "grams"
                unit_price = wz * spot
            else:
                sbul['Metal content'] = None
                sbul['Weight'] = None
            if sbul['Price'] and unit_price != 0:
                difference = abs(int(sbul['Price']) - unit_price)
                sbul['Premium'] = round((difference / unit_price) * 100, 2)
            else:
                sbul['Premium'] = None    
        except:
            sbul['Weight'] = None
            sbul['Premium'] = None
        try:
            sbul['Purity'] = df[-1][1][5]
        except:
            sbul['Purity'] = None
        sbul['Manufacture'] = None
        sbul['Product URL'] = url[0]
        sbul['Supplier Country'] = "USA"
        sbul['Supplier name'] = "SD Bullion"
    except Exception as e: 
        print('line 106 ------'+str(e))    
    try:
        connection,cursor = get_cursor()
        cursor.execute("SELECT * FROM gold_data WHERE Product_Name=%s" , [sbul['Product Name']] );
        data = cursor.fetchall()
    except Exception as e:
        print('line 111 ------'+str(e))    

    if(data):
        try:
            my_query = """UPDATE gold_data SET Price=%s,Crypto_Price=%s,CC_PayPal_Price=%s,Stock=%s,Premium=%s WHERE Product_Name=%s ;""";
            record = [sbul['Price'], sbul['Crypto Price'], sbul['CC/PayPal Price'], sbul['Stock'],sbul['Premium'],sbul['Product Name']]
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
            record = list(sbul.values())
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

    cursor.execute("SELECT url FROM url_and_supp WHERE supplier='Sdbullion'");
    data = cursor.fetchall()
    print(">>>>>>>>>>>>>>>>>", len(data), data[0][0])
    
    # suplier_list = [('Silverbullion','silverbullion'),('Goldcentral','urlsGoldcentral'),
    # ('Kitco','urlsKitco'),('Indigo','urlsIndigo'),('Apmex','urlsApmex'),('Sdbullion','urlSdbullion')]
    threads = min(MAX_THREADS, len(data))

    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(sdb, data)

main()