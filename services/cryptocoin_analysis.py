# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 19:21:24 2017

@author: Edmilson Santana
"""

from plotly import offline, figure_factory
from plotly.graph_objs import Scatter, Line
import pandas as pd
from enum import Enum
from cryptocoin_data import get_data_source, Indicators

data_source = get_data_source()

PEAK_POINT_LABEL = "peak-point"
TROUGH_POINT_LABEL = "trough-point"

FAST_MA_VALUE = 17
FAST_MA_LABEL = str(FAST_MA_VALUE) + "-EMA"

SLOW_MA_VALUE = 72
SLOW_MA_LABEL = str(SLOW_MA_VALUE) + "-EMA"

class Trend(Enum):
    SUBIDA = 1
    DESCIDA = 2
    
def get_trend(freq, periods=None, currency):

    df = get_analysis(freq, periods, data_source.get_historical_data(
            freq, periods, currency))

    slow_ma = df[SLOW_MA_LABEL][-2:]
    fast_ma = df[FAST_MA_LABEL][-2:]
    
    trend = None
    
    if(fast_ma[0] >= slow_ma[0] and fast_ma[1] < slow_ma[1]):
        trend = Trend.DESCIDA
    elif(fast_ma[0] <= slow_ma[0] and fast_ma[1] > slow_ma[1]):
        trend = Trend.SUBIDA
    
    return trend
    
def get_analysis(freq, periods=None, currency, historical_data=None):
    
    if(historical_data is None):
        historical_data = data_source.get_historical_data(
            freq, periods, currency)
        
    #df = historical_data.ohlc()
    df.fillna(method='ffill', inplace=True)
    
    if periods is not None:
        df = df.tail(periods)
        
    df[FAST_MA_LABEL] = df[Indicators.OHLC_CLOSE].ewm(span=FAST_MA_VALUE).mean()
    df[SLOW_MA_LABEL] = df[Indicators.OHLC_CLOSE].ewm(span=SLOW_MA_VALUE).mean()
    
    shift_high =  df[Indicators.OHLC_HIGH].shift(-1)
    shift_low  =  df[Indicators.OHLC_LOW].shift(-1)

    df[TROUGH_POINT_LABEL] = ((shift_high > df[Indicators.OHLC_HIGH]) & 
                               (shift_low > df[Indicators.OHLC_LOW]))
    df[PEAK_POINT_LABEL] = ((shift_high < df[Indicators.OHLC_HIGH]) & 
                               (shift_low  < df[Indicators.OHLC_LOW]))
                               
    return df