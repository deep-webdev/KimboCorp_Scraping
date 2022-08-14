import mysql.connector
import requests
import pandas as pd
from forex_python.converter import CurrencyRates
from bs4 import BeautifulSoup
from lxml.html import fromstring
from urllib.request import Request, urlopen
import concurrent.futures

MAX_THREADS = 500


def get_cursor():
    connection = mysql.connector.connect(user='gold_scrap', database='gold_scrap', host='localhost', password="Gold_scrap@123", port='3306', auth_plugin='mysql_native_password')
    if connection.is_connected():
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


def apmex(url):
    data = scraping(url[0])
    df = data[0][-1]
    soup = data[1]
    apmex_data = {}
    spot = troy_to_price()
    connection,cursor = get_cursor()

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
        apmex_data['Price'] = 0
        apmex_data['Crypto Price'] = 0
        apmex_data['CC/PayPal Price'] = 0
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
    apmex_data['Product URL'] = url[0]
    apmex_data['Supplier name'] = 'APMEX'
    apmex_data['Supplier Country'] = 'Singapore'
    try:
        cursor.execute("SELECT * FROM gold_data WHERE Product_Id=" + apmex_data['Product Id'] );
        data = cursor.fetchall()
    except Exception as e:
        print(e)    
    
    if(data):
        try:
            my_query = """UPDATE gold_data SET Price=%s,Crypto_Price=%s,CC_PayPal_Price=%s,Stock=%s,Premium=%s WHERE Product_Id=%s ;""";
            record = [apmex_data['Price'], apmex_data['Crypto Price'], apmex_data['CC/PayPal Price'], apmex_data['Stock'],apmex_data['Premium'],apmex_data['Product Id']]
            cursor.execute(my_query, record)
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            print(e)
    
    else:
        try:
            my_query = """INSERT INTO gold_data (Product_Name,Price,Crypto_Price,CC_PayPal_Price,Stock,Product_Id,Metal_Content,Weight,Premium,Purity,Manufacture,Product_URL,Supplier_name,Supplier_Country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""";
            record = list(apmex_data.values())
            cursor.execute(my_query, record)
            connection.commit()
            cursor.close()
            connection.close()
        except Exception as e:
            print(e)

def main():
    print("IN main")
    connection,cursor = get_cursor()

    cursor.execute("SELECT url FROM url_and_supp WHERE supplier='Apmex'");
    data = cursor.fetchall()
    
    # suplier_list = [('Silverbullion','silverbullion'),('Goldcentral','urlsGoldcentral'),
    # ('Kitco','urlsKitco'),('Indigo','urlsIndigo'),('Apmex','urlsApmex'),('Sdbullion','urlSdbullion')]
    threads = min(MAX_THREADS, len(data))

    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(apmex, data)

main()