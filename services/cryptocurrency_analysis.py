# -*- coding: utf-8 -*-
"""
Created on Wed Oct 11 19:21:24 2017

@author: Edmilson Santana
"""
from enum import Enum
from cryptocurrency_data import get_data_source, Indicators, TimeFrame

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
    
def get_trend(time_frame, periods, currency):

    df = get_analysis(TimeFrame(time_frame), periods, currency)
   
    trend = None
    
    if df.empty:
        raise ValueError("Não foram encontrados dados para a análise.")
        
    slow_ma = df[SLOW_MA_LABEL][-2:]
    fast_ma = df[FAST_MA_LABEL][-2:]
    
    if(fast_ma[0] >= slow_ma[0] and fast_ma[1] < slow_ma[1]):
        trend = Trend.DESCIDA
    elif(fast_ma[0] <= slow_ma[0] and fast_ma[1] > slow_ma[1]):
        trend = Trend.SUBIDA
    
    return trend
    
def get_analysis(time_frame, periods, currency):
    
    df = data_source.get_historical_data(TimeFrame(time_frame), periods, currency)
    
    if not df.empty:
        df[FAST_MA_LABEL] = df[Indicators.OHLC_CLOSE.value].ewm(span=FAST_MA_VALUE).mean()
        df[SLOW_MA_LABEL] = df[Indicators.OHLC_CLOSE.value].ewm(span=SLOW_MA_VALUE).mean()
    
        shift_high =  df[Indicators.OHLC_HIGH.value].shift(-1)
        shift_low  =  df[Indicators.OHLC_LOW.value].shift(-1)

        df[TROUGH_POINT_LABEL] = ((shift_high > df[Indicators.OHLC_HIGH.value]) & 
                               (shift_low > df[Indicators.OHLC_LOW.value]))
        df[PEAK_POINT_LABEL] = ((shift_high < df[Indicators.OHLC_HIGH.value]) & 
                               (shift_low  < df[Indicators.OHLC_LOW.value]))
                               
    return df

def get_currencies():
    return data_source.get_currencies()
    