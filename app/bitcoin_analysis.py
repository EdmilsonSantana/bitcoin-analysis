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
from enum import Enum 

config = configparser.ConfigParser()
config.read('config.ini')
defaultConfig = config['default']

client = MongoClient(defaultConfig['DBHost'], int(defaultConfig['DBPort']))

db = client['bitcoin_database']

FIGURE_PATH = "./plot.png"

class Trend(Enum):
    SUBIDA = 1
    DESCIDA = 2

def plot(attr, freq, periods):
    
    df = get_analysis(attr, freq, periods)
    
    ax  = df[[attr,'4-EMA', '8-EMA', '12-EMA', '24-MA']].plot(figsize=(10,8))
    fig = ax.get_figure()
    plt.savefig(FIGURE_PATH)
    plt.close(fig)
    
    return FIGURE_PATH

def get_trend(attr, freq, 
              moving_averages=("12-EMA", "4-EMA"), 
              periods=None):
    df = get_analysis(attr, freq, periods)
    slow_ma = df[moving_averages[0]][-2:]
    fast_ma = df[moving_averages[1]][-2:]
    
    trend = None
    
    if(fast_ma[0] >= slow_ma[0] and fast_ma[1] < slow_ma[1]):
        trend = Trend.DESCIDA
    elif(fast_ma[0] <= slow_ma[0] and fast_ma[1] > slow_ma[1]):
        trend = Trend.SUBIDA
    
    return trend
    
def get_analysis(attr, freq, periods=None):
    collection = db.historical_data
    historical_data = list(collection.find())
    
    df = pd.DataFrame(historical_data)
    
    df.set_index('date', inplace=True)
    df = df.resample(rule=freq).mean()
    df.fillna(method='ffill', inplace=True)
 
    if periods is not None:
        df = df.tail(periods)
        
    df['4-EMA'] = df[attr].ewm(span=4).mean()
    df['8-EMA'] = df[attr].ewm(span=8).mean()
    df['12-EMA'] = df[attr].ewm(span=12).mean()
    df['24-MA'] = df[attr].rolling(24).mean()
    return df
