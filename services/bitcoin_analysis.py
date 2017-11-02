# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 19:21:24 2017

@author: Edmilson Santana
"""

from plotly import offline, figure_factory
from plotly.graph_objs import Scatter, Line
import pandas as pd
from pymongo import MongoClient
import configparser
from enum import Enum 

config = configparser.ConfigParser()
config.read('config.ini')
defaultConfig = config['default']

client = MongoClient(defaultConfig['DBHost'], int(defaultConfig['DBPort']))

db = client['bitcoin_database']

PLOT_PATH = "./plot.html"

BITCOIN_ATTR = "buy"
OHLC_CLOSE = "close"
OHLC_OPEN = "open"
OHLC_HIGH = "high"
OHLC_LOW = "low"
PEAK_POINT_LABEL = "peak-point"
TROUGH_POINT_LABEL = "trough-point"

FAST_MA_VALUE = 17
FAST_MA_LABEL = str(FAST_MA_VALUE) + "-EMA"

SLOW_MA_VALUE = 72
SLOW_MA_LABEL = str(SLOW_MA_VALUE) + "-EMA"

class Trend(Enum):
    SUBIDA = 1
    DESCIDA = 2
    

def plot(freq, periods):
    
    historical_data = get_historical_data()
    
    offline.plot(get_candlestick(freq, periods, historical_data), 
                 PLOT_PATH, auto_open=True)
    
    return PLOT_PATH
    

def get_candlestick(historical_data, freq, periods):
    
    df = get_analysis(freq, periods, historical_data)
    
    fig = figure_factory.create_candlestick(df[OHLC_OPEN], 
                                            df[OHLC_HIGH], 
                                            df[OHLC_LOW], 
                                            df[OHLC_CLOSE], 
                                            dates=df.index)

    slow_ma = Scatter(x=df.index,y=df[SLOW_MA_LABEL],
                                  name= SLOW_MA_LABEL,line=Line(color='orange'))
    
    fast_ma = Scatter(x=df.index,y=df[FAST_MA_LABEL],
                                  name=FAST_MA_LABEL,line=Line(color='purple'))
    
    fig.data.extend([slow_ma, fast_ma])
    
    return fig
    
def get_trend(freq, periods=None):
    df = get_analysis(freq, periods, get_historical_data())
    slow_ma = df[SLOW_MA_LABEL][-2:]
    fast_ma = df[FAST_MA_LABEL][-2:]
    
    trend = None
    
    if(fast_ma[0] >= slow_ma[0] and fast_ma[1] < slow_ma[1]):
        trend = Trend.DESCIDA
    elif(fast_ma[0] <= slow_ma[0] and fast_ma[1] > slow_ma[1]):
        trend = Trend.SUBIDA
    
    return trend
    
def get_analysis(freq, periods=None, historical_data=None):
    
    if(historical_data is None):
        historical_data = get_historical_data()
        
    df = historical_data[BITCOIN_ATTR].resample(rule=freq).ohlc()
    df.fillna(method='ffill', inplace=True)
    
 
    if periods is not None:
        df = df.tail(periods)
        
    df[FAST_MA_LABEL] = df[OHLC_CLOSE].ewm(span=FAST_MA_VALUE).mean()
    df[SLOW_MA_LABEL] = df[OHLC_CLOSE].ewm(span=SLOW_MA_VALUE).mean()
    
    shift_high =  df[OHLC_HIGH].shift(-1)
    shift_low  =  df[OHLC_LOW].shift(-1)

    df[TROUGH_POINT_LABEL] = ((shift_high > df[OHLC_HIGH]) & 
                               (shift_low > df[OHLC_LOW]))
    df[PEAK_POINT_LABEL] = ((shift_high < df[OHLC_HIGH]) & 
                               (shift_low  < df[OHLC_LOW]))
                               
    return df

def get_historical_data():
    
    fields = { "date": 1, BITCOIN_ATTR: 1, "_id": 0}
    
    collection = db.historical_data
    historical_data = list(collection.find({},fields))
    
    df = pd.DataFrame(historical_data)
    df.set_index('date', inplace=True)
    
    return df