# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 17:38:27 2017

@author: Edmilson Santana
"""

import requests
import time
import datetime
from pymongo import MongoClient
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
defaultConfig = config['default']

client = MongoClient(defaultConfig['DBHost'], int(defaultConfig['DBPort']))

db = client['bitcoin_database']

collection = db.historical_data
#collection.delete_many({})

API_URL = "https://api.blinktrade.com/api/v1/BRL/ticker"
TIMEOUT = 60
DATE_ATTR = 'date'

if __name__ == "__main__":
    while True:
        response = requests.get(API_URL);
        
        ticker = response.json()
        ticker[DATE_ATTR] = datetime.datetime.now()
        
        collection.insert_one(ticker)
        
        time.sleep(TIMEOUT)


    
