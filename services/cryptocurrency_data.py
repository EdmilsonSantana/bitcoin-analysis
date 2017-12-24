from abc import ABCMeta, abstractmethod
from pymongo import MongoClient
import configparser
import requests
import pandas as pd
from enum import Enum

config = configparser.ConfigParser()
config.read('config.ini')
defaultConfig = config['default']

class Indicators(Enum):
    TIME_STAMP = "date"
    OHLC_CLOSE = "close"
    OHLC_OPEN = "open"
    OHLC_HIGH = "high"
    OHLC_LOW = "low"
    VOLUME = "volume"

class TimeFrame(Enum):
    MINUTE = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    HOUR = "1h"
    DAY = "1d"

class DataSource(object):
    __metaclass__ = ABCMeta
         
    @abstractmethod
    def get_historical_data(self, time_frame, periods, currency):
        pass
    
    @abstractmethod
    def get_currencies(self):
        pass

class Foxbit(DataSource):

    def __init__(self):
        self.host = defaultConfig['DBHost']
        self.port = int(defaultConfig['DBPort'])
        self.client = MongoClient(self.host, self.port)
        self.db = self.client['bitcoin_database']

    def get_historical_data(self, time_frame, periods, currency):
        pass
    
    def get_currencies(self):
        pass

class Bitfinex(DataSource):

    bitfinex_time_frames = {
        TimeFrame.MINUTE : '1m',
        TimeFrame.MINUTE_5 : '5m',
        TimeFrame.MINUTE_15 : '15m',
        TimeFrame.HOUR : '1h',
        TimeFrame.DAY: '1D'
    }

    def __init__(self):
        self.url = defaultConfig['BitfinexEndpoint']

    def get_historical_data(self, time_frame, periods, currency):
        
        request_url = self.url.format(
                TimeFrame=Bitfinex.bitfinex_time_frames[time_frame],
                Currency=currency, Periods=periods)
        
        tickers = requests.get(request_url).json()  
        
        df = pd.DataFrame(self.data_to_candles(tickers))
        if not df.empty:                    	
            df['date'] = pd.to_datetime(df['date'], unit='ms')
            df.set_index('date', inplace=True)
            df.fillna(method='ffill', inplace=True)
    
        return df
    
    def get_currencies(self):
        response = requests.get(defaultConfig['CurrenciesEndpoint']).json()
        currencies = [{currency: 't' + currency.upper()} for currency in response]
        return currencies
 
    def data_to_candles(self,tickers):
        candles = []
        if not 'error' in tickers:
            for ticker in tickers:
                candles.append(self.create_candle(ticker))
        return candles

    def create_candle(self, ticker):
        candle = {}
        candle[Indicators.TIME_STAMP.value] = ticker[0]
        candle[Indicators.OHLC_OPEN.value] = ticker[1]
        candle[Indicators.OHLC_CLOSE.value] = ticker[2]
        candle[Indicators.OHLC_HIGH.value] = ticker[3]
        candle[Indicators.OHLC_LOW.value] = ticker[4]
        return candle

def get_data_source():
    return Bitfinex()
