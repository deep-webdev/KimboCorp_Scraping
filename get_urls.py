import mysql.connector
import requests
import pandas as pd
from forex_python.converter import CurrencyRates
from bs4 import BeautifulSoup
from lxml.html import fromstring
from urllib.request import Request, urlopen
import concurrent.futures

MAX_THREADS = 30


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



def urlSdbullion():
    products = ['https://sdbullion.com/gold/american-gold-eagle-coins/1-oz-gold-eagle-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/1-2-oz-gold-eagle-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/1-4-oz-gold-eagle-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/1-10-oz-gold-eagle-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/graded-american-gold-eagle-coins?product_list_limit=50',
                'https://sdbullion.com/gold/american-gold-eagle-coins/graded-american-gold-eagle-coins?p=2&product_list_limit=50',
                'https://sdbullion.com/gold/american-gold-eagle-coins/pre-1933-us-mint-gold-coins?product_list_limit=50',
                'https://sdbullion.com/gold/american-gold-eagle-coins/american-gold-eagle-proof-coins/mint-box-and-coa?product_list_limit=50',
                'https://sdbullion.com/gold/american-gold-eagle-coins/american-gold-eagle-proof-coins/ngc-graded-american-gold-eagle-proof-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/american-gold-eagle-proof-coins/pcgs-graded-american-gold-eagle-proofs-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/american-gold-eagle-proof-coins/american-gold-eagle-proof-sets',
                'https://sdbullion.com/gold/american-gold-eagle-coins/us-mint-gold-commemorative-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-2-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-4-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-10-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-20-oz-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/gold-maple-leaf-coins/1-gram-gold-maple-leaf-coins',
                'https://sdbullion.com/gold/royal-canadian-mint-gold-coins/call-of-the-wild-gold-coins',
                'https://sdbullion.com/gold/american-gold-buffalo-coins?product_list_limit=50',
                'https://sdbullion.com/gold/british-royal-mint-gold-coins/gold-britannia-coins',
                'https://sdbullion.com/gold/british-royal-mint-gold-coins/royal-mint-tudor-beast-gold-coins',
                'https://sdbullion.com/gold/british-royal-mint-gold-coins/gold-queen-s-beast-coins',
                'https://sdbullion.com/gold/british-royal-mint-gold-coins/other-british-gold-coins',
                'https://sdbullion.com/gold/chinese-gold-panda-coins?product_list_limit=50',
                'https://sdbullion.com/gold/south-african-gold-krugerrand-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/australian-gold-kangaroo-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/australian-kookaburra-gold-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-iii-gold-coins/perth-mint-year-of-the-ox-gold-coins-lunar-series-3',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-iii-gold-coins/perth-mint-year-of-the-mouse-gold-coins-lunar-series-3',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-iii-gold-coins/perth-mint-year-of-the-tiger-gold-coins-lunar-series-3',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-2-gold-coins/perth-mint-lunar-year-of-the-snake-gold-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-2-gold-coins/perth-mint-lunar-year-of-the-pig-gold-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-2-gold-coins/perth-mint-lunar-year-of-the-dog-gold-coins',
                'https://sdbullion.com/gold/perth-mint-gold-coins/perth-mint-lunar-series-1-gold-coins',
                'https://sdbullion.com/gold/mexican-gold-libertad-coins?product_list_limit=50',
                'https://sdbullion.com/gold/austrian-gold-philharmonic-coins',
                'https://sdbullion.com/gold/american-gold-eagle-coins/pre-1933-us-mint-gold-coins?product_list_limit=50',
                'https://sdbullion.com/gold/other-gold-products?product_list_limit=50',
                'https://sdbullion.com/gold/other-gold-products?p=2&product_list_limit=50',
                'https://sdbullion.com/gold/gold-bars?product_list_limit=50',
                'https://sdbullion.com/gold/gold-bars?p=2&product_list_limit=50',
                'https://sdbullion.com/gold/ira-approved-gold?product_list_limit=50',
                'https://sdbullion.com/gold/ira-approved-gold?p=2&product_list_limit=50']
    all_prod = []
    for prod in products:
        data = scraping(prod)
        df = data[0]
        soup = data[1]
        links = soup.find_all('a', 'product-item-photo')
        for link in links:
            all_prod.append(link.get('href'))
    return all_prod


def silverbullion():
    products = ['https://www.silverbullion.com.sg/Shop/Buy/Gold_Coins?CurrentDeptUrl=Gold_Coins&ProductFilter=&SortBy=1&PageNo=1&CurrentBranch=',
                'https://www.silverbullion.com.sg/Shop/Buy/Gold_Bars?CurrentDeptUrl=Gold_Bars&ProductFilter=&SortBy=1&PageNo=1&CurrentBranch=',
                'https://www.silverbullion.com.sg/Shop/Buy/Gold_Bars?CurrentDeptUrl=Gold_Bars&ProductFilter=&SortBy=1&PageNo=2&CurrentBranch=']
    all_prod = []
    final_links = []
    for prod in products:
        data = scraping(prod)
        df = data[0]
        soup = data[1]
        pro = soup.find_all('h3')
        for i in pro:
            if i.find_all('a'):
                link = i.find_all('a')[0].get('href')
                final_links.append('https://www.silverbullion.com.sg' + link)
    final = set(final_links)
    return final


def urlsGoldcentral():
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


def urlsKitco():
    header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
    }
    req = Request("https://online.kitco.com/gold",headers=header)
    html_page = urlopen(req)
    soup = BeautifulSoup(html_page, "lxml")
    link_class = soup.find_all('div', 'product_description')
    links = []
    for link in link_class:
        links.append(link.find('a').get('href'))
    return links


def urlsIndigo():
    products = ['https://www.indigopreciousmetals.com/bullion-products/gold/gold-bars.html',
                'https://www.indigopreciousmetals.com/bullion-products/gold/gold-coins.html']
    data_set = []            
    for prod in products:
        data = scraping(prod)
        df = data[0]
        soup = data[1]
        pro = soup.find_all('a', 'product-image')

        for i in pro:
            url = i.get('href')
            data_set.append(url)
    return data_set


def urlsApmex():
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
            all_data.append(data_link)
            j += 1
    return all_data  

def main():
    print("IN main")
    suplier_list = [('Silverbullion','silverbullion'),('Goldcentral','urlsGoldcentral'),
    ('Kitco','urlsKitco'),('Indigo','urlsIndigo'),('Apmex','urlsApmex'),('Sdbullion','urlSdbullion')]
    threads = min(MAX_THREADS, len(suplier_list))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(download_url, suplier_list)

def download_url(final):
    suplier_name = final[0]
    urls = eval(final[1]+'()')
    connection,cursor = get_cursor()
    print("Downloading....", len(urls),"URLs of ", suplier_name)
    for rec in urls:
        my_query = """INSERT INTO url_and_supp (url, supplier) VALUES (%s, %s);""";
        record = (rec, suplier_name)
        cursor.execute(my_query, record)
        connection.commit()
main()