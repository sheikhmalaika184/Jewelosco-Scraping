import requests 
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# path to input file 
CSVFILE = "input-master-bulk.csv"
ERROR_FILE = f"Error_file {CSVFILE}"
error_file = open(ERROR_FILE,"w")

# path to chrome driver
DRIVER_PATH = '/Users/malaikasheikh/python/chromedriver'
# starting a browser 
driver = webdriver.Chrome(executable_path=DRIVER_PATH)
options = Options()
options.add_argument("--window-size=1920,1200")
options.add_argument('--disable-blink-features=AutomationControlled')
#options.add_argument('--headless')
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

def conversion(original_unit, converted_unit, unit_price, stock_quantity):
  total_price = None
  if((original_unit == "ounce") and (converted_unit == "kg" or converted_unit == "kilograms")):
    one_kg_price = 35.274 * unit_price
    total_price = stock_quantity * one_kg_price
  if((original_unit == "ounce") and (converted_unit == "grams" or converted_unit == "g")):
    one_gram_price = 0.035274 * unit_price
    total_price = stock_quantity * one_gram_price
  if((original_unit == "lb" or original_unit == "pound") and (converted_unit == "kg" or converted_unit == "kilograms")):
    kg_price = 2.20462 * unit_price
    total_price = stock_quantity * kg_price
  if((original_unit == "lb" or original_unit == "pound") and (converted_unit == "grams" or converted_unit == "g")):
    g_price = 0.00220462 * unit_price
    total_price = stock_quantity * g_price
  if((original_unit == "fl.oz") and converted_unit == "ml"):
    one_ml_price = 0.033814 * unit_price
    total_price = stock_quantity * one_ml_price
  if((original_unit == "fl.oz") and (converted_unit == "litres" or converted_unit == "litre" or converted_unit == "liter" or converted_unit == "liters")):
    one_litre_price = 33.814 * unit_price
    total_price = stock_quantity * one_litre_price
  return total_price

def make_request(url):
  try:
    ppo = None
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'lxml') #convert the result into lxml
    div_tag = soup.find("div", class_ = "product-level-4")
    products = div_tag.find_all("product-item-v2")
    for p in products:
      ppo = p.find("div", class_="product-title__qty").text
      if("count" in ppo.lower() or "each" in ppo.lower() or "stick" in ppo.lower() or "ct" in ppo.lower()):
        continue
      else:
        break
  except:
    pass
  return ppo

def read_csv():
    df = pd.read_csv(CSVFILE) # read csv file and store data in a dataframe name df
    df.insert(8,"original unit", '')
    product_list = df['ingredient'] # read a column with name 'Item Name' form df
    for i in range(len(product_list)): # loop through all items
      try:
        product_name = product_list[i].lower().replace(" ","%20") #replace spaces in item name with '%20' so that we could use in url
        print(i,": ",product_list[i])
        url = f"https://www.jewelosco.com/shop/search-results.html?q={product_name}" # url for each item name
        ppo = make_request(url)
        if(ppo == None):
          df['original unit'][i] = "None"
          error_file.write(product_list[i]+"\n")
        else:
          ppo = ppo.replace("$","")
          ppo = ppo.replace("(","")
          ppo = ppo.replace(")","")
          ppo = ppo.split("/")
          original_unit = ppo[1].strip().lower()
          unit_price = float(ppo[0].strip())
          print(unit_price)
          df['original unit'][i] = original_unit.strip().lower()
          converted_unit = df['unit'][i].strip().lower()
          stock_quantity = df['Estimated Total Qty'][i]
          total_price = conversion(original_unit, converted_unit, unit_price, stock_quantity)
          if(total_price == None):
            error_file.write(product_list[i]+"\n")
          else:
            df['price'][i] = round(total_price,2)
          
      except:
        continue
    df.to_csv(f"output  {CSVFILE}", index=False) # write updated df in output csv file 

read_csv()
error_file.close()