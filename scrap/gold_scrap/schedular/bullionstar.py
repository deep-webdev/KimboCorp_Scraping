import requests
import pandas as pd
import gspread

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
df_final['Fees'] = 0.8
df_final['Commissions'] = 0.5
df_final['Final Price'] = df_final['Price'] + df_final['Price'] * (df_final['Fees']/100) + df_final['Price'] * (df_final['Commissions']/100)

df_final['Final Price'] = df_final['Final Price'].astype(int)
df_final['Price'] = df_final['Price'].astype(int)
df_final.fillna('NA',inplace=True)

Sheet_name = "Gold Data"
API_key_file = "/root/gold-data/crypto-sheet-324805-ece76fbce54b.json"
gc = gspread.service_account(filename=API_key_file)
sh = gc.open(Sheet_name)

worksheet = sh.get_worksheet(8)
worksheet.update([df_final.columns.values.tolist()] + df_final.values.tolist())