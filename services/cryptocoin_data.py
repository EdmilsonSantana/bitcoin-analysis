from abc import ABCMeta, abstractmethod
from pymongo import MongoClient
import configparser
import requests

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
    def get_historical(self, freq, periods, currency):
    	pass

class Foxbit(DataSource):

	def __init__(self):
		self.host = defaultConfig['DBHost']
		self.port = int(defaultConfig['DBPort'])
		self.client = MongoClient(self.host, self.port)
		self.db = client['bitcoin_database']

	def get_historical(self, freq, periods, currency):
		fields = { "date": 1, 'buy': 1, "_id": 0}
		collection = self.db.historical_data
		historical_data = list(collection.find({},fields))
		df = pd.DataFrame(historical_data)
		df.set_index('date', inplace=True)
		return df

class Bitfinex(DataSource):

	bitfinex_time_frames = {
		TimeFrame.MINUTE : '1m',
		TimeFrame.MINUTE_5 : '5m',
		TimeFrame.MINUTE_15 : '15m',
		TimeFrame.HOUR : '1h',
		TimeFrame.DAY : '1D'
	}

	def __init__(self):
		base_url = defaultConfig['BitfinexEndpoint']
		self.url = 'candles/trade:{TimeFrame}:{Currency}/hist?limit={Periods}'

	def get_historical(self, freq, periods, currency):
		
		request_url = self.url.format(
			TimeFrame=Bitfinex.bitfinex_time_frames[freq],
			Currency=currency,
			Periods=periods)

		print(request_url)

		response = requests.get(request_url).json()

		df = pd.DataFrame(self.data_to_candles(response.json()))
    	df.set_index('date', inplace=True)
    
    	return df

	def data_to_candles(tickers):
		candles = []
		for ticker in tickers:
			candles.append(create_candle(ticker))
		return candles

	def create_candle(ticker):
		candle = {}
		candle[Indicators.TIME_STAMP] = ticker[0]
		candle[Indicators.OHLC_OPEN] = ticker[1]
		candle[Indicators.OHLC_CLOSE] = ticker[2]
		candle[Indicators.OHLC_HIGH] = ticker[3]
		candle[Indicators.OHLC_LOW] = ticker[4]
		candle[Indicators.VOLUME] = ticker[5]
		return candle

print(data_source.get_historical(TimeFrame.MINUTE, 1000, 'tBTCUSD'))
