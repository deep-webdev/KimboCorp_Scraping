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


def kitco(url):
    try:
        spot = troy_to_price()

        data = scraping('https://online.kitco.com' + url[0])
        kitco = {}
        soup = data[1]

        kitco['Product Name'] = soup.find("div", {"id": "prod_title"}).get_text().split('\n')[1].split('Buying')[0].replace('Buy','')
        try:
            dfs = data[0][0]
            kitco['Price'] = float(dfs['Wire/Check'][0].split('$')[1].replace(",", ""))
            kitco['Crypto Price'] = None

            try:
                kitco['CC/PayPal Price'] = float(dfs['MC/Visa/PayPal'][0].split('$')[1].replace(",", ""))
            except:
                kitco['CC/PayPal Price'] = None
            kitco['Stock'] = 'In Stock'
            
        except:
            kitco['Price'] = 0
            kitco['Crypto Price'] = 0

            kitco['CC/PayPal Price'] = 0
            kitco['Stock'] = 'Out of Stock'

        kitco['Product Id'] = None

        kitco['Metal Content'] = soup.find("ul", {"id": "prod_details_list"}).get_text().split(':')[1].strip().split('\r')[0]

        if 'oz' in kitco['Metal Content'].split():
            content = kitco['Metal Content'].split()[0]
        elif 'g' in kitco['Metal Content'].split():
            content = convert_to_float(kitco['Metal Content'].split()[0]) * 0.035274

        kitco['Weight'] = str(round(float(convert_to_float(content)) * (1/0.035274))) + ' grams'
        unit_price = float(spot) * float(convert_to_float(content))
        if kitco['Price']: 
            difference = abs(int(kitco['Price']) - unit_price)
            kitco['Premium'] = round((difference / unit_price) * 100, 2)
        else:   
            kitco['Premium'] = 'NA'
        
        kitco['Purity'] = soup.find("ul", {"id": "prod_details_list"}).get_text().split('Fineness:')[1].strip().split('\r')[0]
    
        kitco['Manufacture'] = None

        kitco['Product URL'] = "https://online.kitco.com" + url[0]
        kitco['Supplier name'] = "Kitco"
        kitco['Supplier Country'] = "USA"
    except Exception as e: 
        print('line 106 ------'+str(e))    
    try:
        connection,cursor = get_cursor()
        cursor.execute("SELECT * FROM gold_data WHERE Product_Name=%s" , [kitco['Product Name']] );
        data = cursor.fetchall()
    except Exception as e:
        print('line 111 ------'+str(e))    

    if(data):
        try:
            my_query = """UPDATE gold_data SET Price=%s,Crypto_Price=%s,CC_PayPal_Price=%s,Stock=%s,Premium=%s,Weight=%s WHERE Product_Name=%s ;""";
            record = [kitco['Price'], kitco['Crypto Price'], kitco['CC/PayPal Price'], kitco['Stock'],kitco['Premium'],kitco['Weight'],kitco['Product Name']]
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
            record = list(kitco.values())
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

    cursor.execute("SELECT url FROM url_and_supp WHERE supplier='kitco'");
    data = cursor.fetchall()
    
    # suplier_list = [('Silverbullion','silverbullion'),('Goldcentral','urlsGoldcentral'),
    # ('Kitco','urlsKitco'),('Indigo','urlsIndigo'),('Apmex','urlsApmex'),('Sdbullion','urlSdbullion')]
    threads = min(MAX_THREADS, len(data))

    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(kitco, data)

main()