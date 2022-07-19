from posixpath import split
import requests
import pandas as pd
from gold_scrap.models import BullionStar

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
    model_instances = [BullionStar(
        product_name=record['Name'],
        price_usd=record['Price'],
        price_sgd=record['SGD Price'],
        crypto_price=record['Crypto Price'],
        paypal_price=record['CC/PayPal Price'], 
        weight = record['Weight'],
        premium = record['Premium'],
        product_id = record['Id'],
        metal_content = record['Weight'],
        stock=record['Status'],
        purity = record['Purity'],
        manufacture = record['Manufacturer'],
        product_url = record['Url'],
        supplier_name= record['Supplier name'],
        supplier_country = record['Country']
    ) for record in df_records]

    BullionStar.objects.all().delete()

    BullionStar.objects.bulk_create(model_instances)

