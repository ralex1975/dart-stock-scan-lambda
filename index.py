import pandas as pd
import time as _time
import requests
import numpy as np
import datetime
from dateutil import tz

from talib import EMA,SMA, WMA
# from finta import TA
import sys
import math

# from yahoo_finance_api import YahooFinance as yf

class YahooFinance:
    def __init__(self, ticker, result_range='1mo', start=None, end=None, interval='15m', dropna=True):
        """
        Return the stock data of the specified range and interval
        Note - Either Use result_range parameter or use start and end
        Note - Intraday data cannot extend last 60 days
        :param ticker:  Trading Symbol of the stock should correspond with yahoo website
        :param result_range: Valid Ranges "1d","5d","1mo","3mo","6mo","1y","2y","5y","10y","ytd","max"
        :param start: Starting Date
        :param end: End Date
        :param interval:Valid Intervals - Valid intervals: [1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo]
        :return:
        """
        if result_range is None:
            start = int(_time.mktime(_time.strptime(start, '%d-%m-%Y')))
            end = int(_time.mktime(_time.strptime(end, '%d-%m-%Y')))
            # defining a params dict for the parameters to be sent to the API
            params = {'period1': start, 'period2': end, 'interval': interval}

        else:
            params = {'range': result_range, 'interval': interval}

        # sending get request and saving the response as response object
        url = "https://query1.finance.yahoo.com/v8/finance/chart/{}".format(ticker)
        r = requests.get(url=url, params=params)
        data = r.json()
        # Getting data from json
        error = data['chart']['error']
        if error:
            raise ValueError(error['description'])
        self._result = self._parsing_json(data)
        if dropna:
            self._result.dropna(inplace=True)

    @property
    def result(self):
        return self._result

    def _parsing_json(self, data):
        timestamps = data['chart']['result'][0]['timestamp']
        # Formatting date from epoch to local time
        timestamps = [_time.strftime('%a, %d %b %Y %H:%M:%S', _time.gmtime(x)) for x in timestamps]
        volumes = data['chart']['result'][0]['indicators']['quote'][0]['volume']
        opens = data['chart']['result'][0]['indicators']['quote'][0]['open']
        opens = self._round_of_list(opens)
        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = self._round_of_list(closes)
        lows = data['chart']['result'][0]['indicators']['quote'][0]['low']
        lows = self._round_of_list(lows)
        highs = data['chart']['result'][0]['indicators']['quote'][0]['high']
        highs = self._round_of_list(highs)
        df_dict = {'Open': opens, 'High': highs, 'Low': lows, 'Close': closes, 'Volume': volumes}
        df = pd.DataFrame(df_dict, index=timestamps)
        df.index = pd.to_datetime(df.index)
        return df

    def _round_of_list(self, xlist):
        temp_list = []
        for x in xlist:
            if isinstance(x, float):
                temp_list.append(round(x, 2))
            else:
                temp_list.append(pd.np.nan)
        return temp_list

    def to_csv(self, file_name):
        self.result.to_csv(file_name)


def fetch_data(symbol, period, interval):
    pd.options.display.max_rows = 2000
    fin_prod_data = YahooFinance(symbol, result_range=period, interval=interval).result
    return fin_prod_data

def myHMACalc(ohlc, period):
    half_length = int(round((period / 2),0))
    sqrt_length = int(round(math.sqrt(period),0))
    # ohlc = df['close'].values
    wmaf = WMA(ohlc, timeperiod=half_length)
    wmas = WMA(ohlc, timeperiod=period)
    deltawma = 2 * wmaf - wmas
    # deltawma = ohlc['deltawma'].values
    hma = WMA(deltawma, timeperiod=sqrt_length)
    return pd.Series(hma, name="{0} period HMA.".format(period))


# def handler(event, context):
def main():
    print(sys.version)
    # data = {
    #     'output': 'Hello World 11',
    #     'timestamp': datetime.datetime.utcnow().isoformat()
    # }
    # return {'statusCode': 200,
    #         'body': json.dumps(data),
    #         'headers': {'Content-Type': 'application/json'}}

# def main():
#     print(sys.version)

    # stock = input('Stock to plot: ')
    outputDf = pd.DataFrame()

    # for symbol in ['^NSEI', '^NSEBANK', 'ADANIPORTS.NS', 'ASIANPAINT.NS', 'AXISBANK.NS', 'BAJFINANCE.NS', 'BPCL.NS',
    #                    'BHARTIARTL.NS', 'CIPLA.NS', 'COALINDIA.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'GAIL.NS',
    #                    'GRASIM.NS', 'HCLTECH.NS', 'HDFCBANK.NS', 'HDFC.NS', 'HEROMOTOCO.NS', 'HINDALCO.NS', 'HINDPETRO.NS',
    #                    'HINDUNILVR.NS','INFRATEL.NS', 'ITC.NS', 'ICICIBANK.NS', 'IBULHSGFIN.NS', 'IOC.NS', 'INDUSINDBK.NS',
    #                    'INFY.NS', 'JSWSTEEL.NS', 'KOTAKBANK.NS', 'LT.NS', 'MARUTI.NS', 'NTPC.NS', 'ONGC.NS', 'POWERGRID.NS',
    #                    'RELIANCE.NS', 'SBIN.NS', 'SUNPHARMA.NS', 'TCS.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'TECHM.NS',
    #                    'TITAN.NS', 'UPL.NS', 'ULTRACEMCO.NS', 'VEDL.NS', 'WIPRO.NS', 'YESBANK.NS', 'ZEEL.NS']:
    for symbol in ['^NSEI','^NSEBANK']:
        print(symbol)
        period = '2y'
        pd.options.display.max_rows = 2000
        # period = '6mo'

        # fetching 2 year 1h data as that is the limiit for 1 hr
        content = fetch_data(symbol, period, '1d')

        content = content.tz_localize(tz='Etc/UTC')
        content = content.tz_convert(tz='Asia/Kolkata')
        content.reset_index(inplace=True)
        content.rename(columns = {'index':'startTime'},inplace=True)
        # hma = myHMACalc(content, 21)
        # content['21HMA'] = hma.values
        # ohlc = content["close"].resample("1h").ohlc()
        # print("Dummy")
        content['Symbol'] = symbol

        close = content['Close'].values
        # up, mid, low = BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        for hmaperiod in [5,8,15,21,50,100,200]:
            hma = myHMACalc(close, hmaperiod)
            hma = np.round(hma,2)

            se = pd.Series(hma)
            content["{0}HMA".format(hmaperiod)] = se.values

        for emaperiod in [5,8,15,22,50,100,200]:
            ema = EMA(close, timeperiod=emaperiod)
            ema = np.round(ema,2)

            se = pd.Series(ema)
            content["{0}EMA".format(emaperiod)] = se.values

        for smaperiod in [5,8,15,22,50,100,200]:
            sma = SMA(close, timeperiod=smaperiod)
            sma = np.round(sma,2)

            se = pd.Series(sma)
            content["{0}SMA".format(smaperiod)] = se.values

        # populating a column if it is index or stock
        if symbol in ['^NSEI','^NSEBANK']:
            content['Type'] = "Index"
        else:
            content['Type'] = "Stock"

        # GEt just the last 2 lines
        content = content.tail(2)

        # The last 2 lines is the data we operate on
        # Create multiple lists based on the criteria, like close to 200, crossed etc
        # then consolidate each to its own output
        # then alert mail or SNS or what not


        # Based on the columnval create a new column and populate all B
        # cloumnval-ARB - meaning above or below the columnval with the diff percent
        # however dilemma is if diffpercent  non 0 then it can neither be above or below
        # for now default 0 and can address later
        columnval = "200SMA"
        diffPercent = 0.0
        ARBcolumnval = 'ARB-{}'.format(columnval)
        content[ARBcolumnval] = 'B'

        # If condition is above set A for the rows

        content[ARBcolumnval][
            content[content['Close'] >= (1.0 + (0.01 * diffPercent)) * content[columnval]].index] = 'A'

        # if content[columnval] >= (1.0 + (0.01 * diffPercent)) * content['Close']:
        #     content['{}-ARB'.format(columnval)] = 'A'
        # else:
        #     content['{}-ARB'.format(columnval)] = 'B'



        # Below block gets prev N rows val of a column and create a column
        # It will create column for the chose columnval and also the close
        nrowsback = 1
        columnvalback = ARBcolumnval


        # Create empty columns equal to n previos rows
        for itervar in range(1, nrowsback + 1, 1):
            content["{0}prev{1}".format(columnvalback, itervar)] = ''

        # Populating the above created columns
        for indexval, row in content.iterrows():
            for itervar in range(1, nrowsback + 1, 1):
                content["{0}prev{1}".format(columnvalback, itervar)] = content.tail(itervar+1).head(1)[columnvalback].values[0]

        # tail the last line and append to the outputDf
        # Then from that filter 4 lists as per criteria
        # essential idea is one row with all data for all stocks and then filer and mail
        # That is the model for additional criteria
        content = content.tail(1)


        # Iterating through the list of index/stock and then appending the processed data to outputDf
        outputDf = outputDf.append(content, ignore_index=True)

    india_tz= tz.gettz('Asia/Kolkata')
    dtString = datetime.datetime.now(tz=india_tz).strftime("%d-%m-%Y-%H-%M")
    # outputDf.to_csv('/home/bharath/IT/dart_analysis/output_hourly_MA_HMA_{}.csv'.format(dtString))
    print("Hello")

if __name__== "__main__":
  main()







