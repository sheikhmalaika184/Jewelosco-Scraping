import requests 
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import warnings
warnings.filterwarnings('ignore', message=".*A value is trying to be set on a copy of a slice from a DataFrame.*")

# path to input file 
CSVFILE = "stock-in-list.csv"
ERROR_FILE = f"Error_file {CSVFILE}"
error_file = open(ERROR_FILE,"w")

# starting a browser 
options = Options()
options.add_argument("--window-size=1920,1200")
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options) # delete the executable path as there is no need of chrome driver in latest version of sleenium
# Changes made
# removed ambiquity in oz and fl.oz
# Error capture file error_file
def conversion(original_unit, converted_unit, unit_price, qty):
  if((original_unit == "oz" or original_unit == "ounce") and converted_unit == "kg"):
    one_kg_price = 35.274 * unit_price
    total_price = qty * one_kg_price
  if((original_unit == "oz"  or original_unit == "ounce") and (converted_unit == "grams" or converted_unit == "g")):
    one_gram_price = 0.035274 * unit_price
    total_price = qty * one_gram_price
  if((original_unit == "lb" or original_unit == "pound") and converted_unit == "kg"):
    kg_price = 0.453592 * unit_price
    total_price = qty * kg_price
  if((original_unit == "lb" or original_unit == "pound") and (converted_unit == "grams" or converted_unit == "g")):
    g_price = 453.592 * unit_price
    total_price = qty * g_price
  if((original_unit == "fl.oz") and converted_unit == "ml"):
    one_ml_price = 0.033814 * unit_price
    total_price = qty * one_ml_price
  if((original_unit == "fl.oz") and converted_unit == "liter"):
    one_litre_price = 33.814 * unit_price
    total_price = qty * one_litre_price
  return total_price

def make_request(url):
  try:
    ppo = None
    driver.get(url)
    time.sleep(2)
    '''
    # locating button for dropdown menu
    search_tag = driver.find_element(By.ID,'search-sort_0')
    dropdown_button = search_tag.find_element(By.ID, 'sortDropdown')
    dropdown_button.click()
    time.sleep(1)
    # selecting drop menu option
    dropdown_menu = driver.find_element(By.ID,'sortDropdownMenu')
    a_tag = dropdown_menu.find_element(By.ID,'sortRule-1')
    a_tag.click()
    time.sleep(2) '''

    # finding list of products
    div_tag = driver.find_element(By.CLASS_NAME,'product-level-4')
    products = div_tag.find_elements(By.TAG_NAME, "product-item-v2") # finding products list using tags names
    for p in products:
      ppo = p.find_element(By.CLASS_NAME, "product-title__qty").text
      if("count" in ppo.lower() or "each" in ppo.lower() or "stick" in ppo.lower() or "ct" in ppo.lower() or "pack" in ppo.lower()):
        continue
      else:
        break 
  except Exception as e:
    pass
  return ppo


def read_csv():
    df = pd.read_csv(CSVFILE) # read csv file and store data in a dataframe name df
    df.insert(8,"original unit", '')
    product_list = df['ingredient'] # read a column with name 'Item Name' form df
    for i in range(0, len(product_list)): # loop through all items
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
          df['original unit'][i] = original_unit
          converted_unit = df['unit'][i].strip().lower()
          qty = df['qty'][i]
          total_price = conversion(original_unit, converted_unit, unit_price, qty)
          df['price'][i] = round(total_price,2)
          print("Original Unit: ",original_unit)
          print("Unit price: ",unit_price)
          print("Total Price: ",total_price)
          print("")
      except Exception as e:
        continue
    df.to_csv("output.csv", index=False) # write updated df in output csv file 


read_csv()
