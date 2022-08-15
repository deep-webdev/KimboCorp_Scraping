from posixpath import split
import requests
import pandas as pd
import mysql.connector

def get_cursor():
    connection = mysql.connector.connect(user='gold_scrap', database='gold_scrap', host='localhost', password="Gold_scrap@123", port='3306', auth_plugin='mysql_native_password')
    if connection.is_connected():
        cursor = connection.cursor()
        return (connection,cursor)
    
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

def update_data():
    print("in bulilionstar...")
    all_products = []
    for i in range(1,10): 
        data = requests.get('https://services.bullionstar.com/product/filter/desktop?locationId=1&apg=-1&name=gold&sortType=popular&sortDirection=desc&page='+str(i)+'&currency=USD')
        if(len(data.json()['result']['groups']) == 0):
            break
        for product in data.json()['result']['groups']:
            all_products.extend(product['products'])
            
    df = pd.DataFrame(all_products)
    df_final = df[['id','name','url','title','price','pricePremium','purity','manufacturer','fineWeight','country','status']]
    df_final.columns = ['Id','Name','Url','Title','Price','Premium','Purity','Manufacturer','Weight','Country','Status']
    df_final['Weight'] = df_final['Weight'].str.split("(").str[0]
    df_final['Price'].fillna('USD 0',inplace=True)
    df_final['Price'] = df_final['Price'].str.split().str[1].str.replace(",",'')
    df_final['Price'] = df_final['Price'].astype(float)
    df_final['SGD Price'] = 'NA'
    df_final['Crypto Price'] = 'NA'
    df_final['CC/PayPal Price'] = 'NA'
    df_final['Supplier name'] = "Bullion Star"
    if 'gram' in df_final['Weight'].str.split()[1]:
        df_final['Weight'] = df_final['Weight'].replace({'gram': 'grams'}, regex=True)
    elif 'g' in df_final['Weight'].str.split()[1]:
        df_final['Weight'] = df_final['Weight'].replace({'g': 'grams'}, regex=True)
    df_final['Status'].replace(to_replace="IN_STOCK",value="In Stock",inplace=True)
    df_final['Status'].replace(to_replace="UNAVAILABLE",value="Out of Stock",inplace=True)
    df_final.fillna('NA',inplace=True)
    df_records = df_final.to_dict('records')
    connection,cursor = get_cursor()
    for i in df_records:
        try:
            cursor.execute("SELECT * FROM gold_data WHERE Product_Id=" + i['Id']);
            data = cursor.fetchall()
        except Exception as e:
            print(e)
        if 'troy' in i['Weight'].split():
            i['Weight'] = str(int((convert_to_float(i['Weight'].split()[0]) * 31.103))) + " grams"
        if(data):
            try:
                my_query = """UPDATE gold_data SET Price=%s,Crypto_Price=%s,CC_PayPal_Price=%s,Stock=%s,Premium=%s,Weight=%s WHERE Product_Id=%s ;""";
                record = [i['Price'], i['Crypto Price'], i['CC/PayPal Price'], i['Status'],i['Premium'],i['Weight'],i['Id']]
                cursor.execute(my_query, record)
                connection.commit()
            except Exception as e:
                print(e)
        else:
            try:
                my_query = """INSERT INTO gold_data (Product_Name,Price,Crypto_Price,CC_PayPal_Price,Stock,Product_Id,Metal_Content,Weight,Premium,Purity,Manufacture,Product_URL,Supplier_name,Supplier_Country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""";
                record = [i['Name'], i['Price'], i['Crypto Price'], i['CC/PayPal Price'],i['Status'], i['Id'], i['Weight'],i['Weight'], i['Premium'], i['Purity'], i['Manufacturer'], i['Url'], i['Supplier name'], i['Country']]
                cursor.execute(my_query, record)
                connection.commit()
            except Exception as e:
                print(e)
    cursor.close()
    connection.close()
    
update_data()
