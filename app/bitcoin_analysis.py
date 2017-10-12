# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 19:21:24 2017

@author: Edmilson Santana
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
defaultConfig = config['default']

client = MongoClient(defaultConfig['DBHost'], int(defaultConfig['DBPort']))

db = client['bitcoin_database']

FIGURE_PATH = "./plot.png"

def plot(attr, freq):
    
    collection = db.historical_data
    historical_data = list(collection.find())
    
    df = pd.DataFrame(historical_data)
    df.set_index('date', inplace=True)
    df = df.resample(rule=freq).mean()
    
    df['4-EMA'] = df[attr].ewm(span=4).mean()
    df['8-EMA'] = df[attr].ewm(span=8).mean()
    df['12-EMA'] = df[attr].ewm(span=12).mean()
    
    ax  = df[[attr,'4-EMA', '8-EMA', '12-EMA']].plot(figsize=(10,8))
    fig = ax.get_figure()
    plt.savefig(FIGURE_PATH)
    plt.close(fig)
    
    return FIGURE_PATH
    
