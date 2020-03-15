import pandas as pd
import time as _time
import requests
import numpy as np
import datetime
import boto3
import json
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

def sendAWSMail(recipeint,subject,body_text):
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "dartconsultants.hyd@gmail.com"
    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = recipeint
    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-west-2"
    # The subject line for the email.
    SUBJECT = subject

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = body_text

    # The HTML body of the email.
    # BODY_HTML = """<html>
    # <head></head>
    # <body>
    #   <h1>Amazon SES Test (SDK for Python)</h1>
    #   <p>This email was sent with
    #     <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
    #     <a href='https://aws.amazon.com/sdk-for-python/'>
    #       AWS SDK for Python (Boto)</a>.</p>
    # </body>
    # </html>
    #             """
    # The character encoding for the email.
    # Test comment to check in
    CHARSET = "UTF-8"
    # Create a new SES resource and specify a region.
    client = boto3.client('ses', region_name=AWS_REGION)
    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])



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

# def main():
def handler(event, context):
    print(sys.version)


# def main():
#     print(sys.version)

    # stock = input('Stock to plot: ')
    outputDf = pd.DataFrame()
    
    # symbolList = ['^NSEI','^NSEBANK']
    symbolList=['3MINDIA.NS','ACC.NS','AIAENG.NS','APLAPOLLO.NS','AUBANK.NS','AARTIIND.NS','AAVAS.NS','ABBOTINDIA.NS','ADANIGAS.NS','ADANIGREEN.NS','ADANIPORTS.NS','ADANIPOWER.NS','ADANITRANS.NS','ABCAPITAL.NS','ABFRL.NS','ADVENZYMES.NS','AEGISCHEM.NS','AJANTPHARM.NS','AKZOINDIA.NS','APLLTD.NS','ALKEM.NS','ALLCARGO.NS','AMARAJABAT.NS','AMBER.NS','AMBUJACEM.NS','APOLLOHOSP.NS','APOLLOTYRE.NS','ARVINDFASN.NS','ASAHIINDIA.NS','ASHOKLEY.NS','ASHOKA.NS','ASIANPAINT.NS','ASTERDM.NS','ASTRAZEN.NS','ASTRAL.NS','ATUL.NS','AUROPHARMA.NS','AVANTIFEED.NS','DMART.NS','AXISBANK.NS','BASF.NS','BEML.NS','BSE.NS','BAJAJ-AUTO.NS','BAJAJCON.NS','BAJAJELEC.NS','BAJFINANCE.NS','BAJAJFINSV.NS','BAJAJHLDNG.NS','BALKRISIND.NS','BALMLAWRIE.NS','BALRAMCHIN.NS','BANDHANBNK.NS','BANKBARODA.NS','BANKINDIA.NS','MAHABANK.NS','BATAINDIA.NS','BAYERCROP.NS','BERGEPAINT.NS','BDL.NS','BEL.NS','BHARATFORG.NS','BHEL.NS','BPCL.NS','BHARTIARTL.NS','INFRATEL.NS','BIOCON.NS','BIRLACORPN.NS','BSOFT.NS','BLISSGVS.NS','BLUEDART.NS','BLUESTARCO.NS','BBTC.NS','BOMDYEING.NS','BOSCHLTD.NS','BRIGADE.NS','BRITANNIA.NS','CARERATING.NS','CCL.NS','CESC.NS','CRISIL.NS','CADILAHC.NS','CANFINHOME.NS','CANBK.NS','CAPLIPOINT.NS','CGCL.NS','CARBORUNIV.NS','CASTROLIND.NS','CEATLTD.NS','CENTRALBK.NS','CDSL.NS','CENTURYPLY.NS','CERA.NS','CHALET.NS','CHAMBLFERT.NS','CHENNPETRO.NS','CHOLAHLDNG.NS','CHOLAFIN.NS','CIPLA.NS','CUB.NS','COALINDIA.NS','COCHINSHIP.NS','COLPAL.NS','CONCOR.NS','COROMANDEL.NS','CREDITACC.NS','CROMPTON.NS','CUMMINSIND.NS','CYIENT.NS','DBCORP.NS','DCBBANK.NS','DCMSHRIRAM.NS','DLF.NS','DABUR.NS','DALBHARAT.NS','DEEPAKNTR.NS','DELTACORP.NS','DHFL.NS','DBL.NS','DISHTV.NS','DCAL.NS','DIVISLAB.NS','DIXON.NS','LALPATHLAB.NS','DRREDDY.NS','EIDPARRY.NS','EIHOTEL.NS','EDELWEISS.NS','EICHERMOT.NS','ELGIEQUIP.NS','EMAMILTD.NS','ENDURANCE.NS','ENGINERSIN.NS','EQUITAS.NS','ERIS.NS','ESCORTS.NS','ESSELPACK.NS','EXIDEIND.NS','FDC.NS','FEDERALBNK.NS','FMGOETZE.NS','FINEORG.NS','FINCABLES.NS','FINPIPE.NS','FSL.NS','FORTIS.NS','FCONSUMER.NS','FLFL.NS','FRETAIL.NS','GAIL.NS','GEPIL.NS','GET&D.NS','GHCL.NS','GMRINFRA.NS','GALAXYSURF.NS','GARFIBRES.NS','GAYAPROJ.NS','GICRE.NS','GILLETTE.NS','GLAXO.NS','GLENMARK.NS','GODFRYPHLP.NS','GODREJAGRO.NS','GODREJCP.NS','GODREJIND.NS','GODREJPROP.NS','GRANULES.NS','GRAPHITE.NS','GRASIM.NS','GESHIP.NS','GREAVESCOT.NS','GRINDWELL.NS','GUJALKALI.NS','GUJGASLTD.NS','GMDCLTD.NS','GNFC.NS','GPPL.NS','GSFC.NS','GSPL.NS','GULFOILLUB.NS','HEG.NS','HCLTECH.NS','HDFCAMC.NS','HDFCBANK.NS','HDFCLIFE.NS','HFCL.NS','HATSUN.NS','HAVELLS.NS','HEIDELBERG.NS','HERITGFOOD.NS','HEROMOTOCO.NS','HEXAWARE.NS','HSCL.NS','HIMATSEIDE.NS','HINDALCO.NS','HAL.NS','HINDCOPPER.NS','HINDPETRO.NS','HINDUNILVR.NS','HINDZINC.NS','HONAUT.NS','HUDCO.NS','HDFC.NS','ICICIBANK.NS','ICICIGI.NS','ICICIPRULI.NS','ISEC.NS','ICRA.NS','IDBI.NS','IDFCFIRSTB.NS','IDFC.NS','IFBIND.NS','IFCI.NS','IIFL.NS','IRB.NS','IRCON.NS','ITC.NS','ITDCEM.NS','ITI.NS','INDIACEM.NS','ITDC.NS','IBULHSGFIN.NS','IBULISL.NS','IBREALEST.NS','IBVENTURES.NS','INDIANB.NS','IEX.NS','INDHOTEL.NS','IOC.NS','IOB.NS','INDOSTAR.NS','IGL.NS','INDUSINDBK.NS','INFIBEAM.NS','NAUKRI.NS','INFY.NS','INOXLEISUR.NS','INTELLECT.NS','INDIGO.NS','IPCALAB.NS','JBCHEPHARM.NS','JKCEMENT.NS','JKLAKSHMI.NS','JKPAPER.NS','JKTYRE.NS','JMFINANCIL.NS','JSWENERGY.NS','JSWSTEEL.NS','JAGRAN.NS','JAICORPLTD.NS','JISLJALEQS.NS','J&KBANK.NS','JAMNAAUTO.NS','JINDALSAW.NS','JSLHISAR.NS','JSL.NS','JINDALSTEL.NS','JCHAC.NS','JUBLFOOD.NS','JUBILANT.NS','JUSTDIAL.NS','JYOTHYLAB.NS','KPRMILL.NS','KEI.NS','KNRCON.NS','KPITTECH.NS','KRBL.NS','KAJARIACER.NS','KALPATPOWR.NS','KANSAINER.NS','KTKBANK.NS','KARURVYSYA.NS','KSCL.NS','KEC.NS','KIRLOSENG.NS','KOLTEPATIL.NS','KOTAKBANK.NS','L&TFH.NS','LTTS.NS','LICHSGFIN.NS','LAXMIMACH.NS','LAKSHVILAS.NS','LTI.NS','LT.NS','LAURUSLABS.NS','LEMONTREE.NS','LINDEINDIA.NS','LUPIN.NS','LUXIND.NS','MASFIN.NS','MMTC.NS','MOIL.NS','MRF.NS','MAGMA.NS','MGL.NS','MAHSCOOTER.NS','MAHSEAMLES.NS','M&MFIN.NS','M&M.NS','MAHINDCIE.NS','MHRIL.NS','MAHLOG.NS','MANAPPURAM.NS','MRPL.NS','MARICO.NS','MARUTI.NS','MFSL.NS','METROPOLIS.NS','MINDTREE.NS','MINDACORP.NS','MINDAIND.NS','MIDHANI.NS','MOTHERSUMI.NS','MOTILALOFS.NS','MPHASIS.NS','MCX.NS','MUTHOOTFIN.NS','NATCOPHARM.NS','NBCC.NS','NCC.NS','NESCO.NS','NHPC.NS','NIITTECH.NS','NLCINDIA.NS','NMDC.NS','NTPC.NS','NH.NS','NATIONALUM.NS','NFL.NS','NBVENTURES.NS','NAVINFLUOR.NS','NESTLEIND.NS','NETWORK18.NS','NILKAMAL.NS','NAM-INDIA.NS','OBEROIRLTY.NS','ONGC.NS','OIL.NS','OMAXE.NS','OFSS.NS','ORIENTCEM.NS','ORIENTELEC.NS','ORIENTREF.NS','PCJEWELLER.NS','PIIND.NS','PNBHOUSING.NS','PNCINFRA.NS','PTC.NS','PVR.NS','PAGEIND.NS','PARAGMILK.NS','PERSISTENT.NS','PETRONET.NS','PFIZER.NS','PHILIPCARB.NS','PHOENIXLTD.NS','PIDILITIND.NS','PEL.NS','POLYCAB.NS','PFC.NS','POWERGRID.NS','PRAJIND.NS','PRESTIGE.NS','PRSMJOHNSN.NS','PGHL.NS','PGHH.NS','PNB.NS','QUESS.NS','RBLBANK.NS','RECLTD.NS','RITES.NS','RADICO.NS','RVNL.NS','RAIN.NS','RAJESHEXPO.NS','RALLIS.NS','RCF.NS','RATNAMANI.NS','RAYMOND.NS','REDINGTON.NS','RELAXO.NS','RELCAPITAL.NS','RELIANCE.NS','RELINFRA.NS','RPOWER.NS','REPCOHOME.NS','RESPONIND.NS','SHK.NS','SBILIFE.NS','SJVN.NS','SKFINDIA.NS','SRF.NS','SADBHAV.NS','SANOFI.NS','SCHAEFFLER.NS','SIS.NS','SFL.NS','SHILPAMED.NS','SHOPERSTOP.NS','SHREECEM.NS','RENUKA.NS','SHRIRAMCIT.NS','SRTRANSFIN.NS','SIEMENS.NS','SOBHA.NS','SOLARINDS.NS','SONATSOFTW.NS','SOUTHBANK.NS','STARCEMENT.NS','SBIN.NS','SAIL.NS','STRTECH.NS','STAR.NS','SUDARSCHEM.NS','SPARC.NS','SUNPHARMA.NS','SUNTV.NS','SUNCLAYLTD.NS','SUNDARMFIN.NS','SUNDRMFAST.NS','SUNTECK.NS','SUPRAJIT.NS','SUPREMEIND.NS','SUZLON.NS','SWANENERGY.NS','SYMPHONY.NS','SYNGENE.NS','TCIEXP.NS','TCNSBRANDS.NS','TTKPRESTIG.NS','TVTODAY.NS','TV18BRDCST.NS','TVSMOTOR.NS','TAKE.NS','TASTYBITE.NS','TCS.NS','TATAELXSI.NS','TATAINVEST.NS','TATAMTRDVR.NS','TATAMOTORS.NS','TATAPOWER.NS','TATASTLBSL.NS','TATASTEEL.NS','TEAMLEASE.NS','TECHM.NS','TECHNOE.NS','NIACL.NS','RAMCOCEM.NS','THERMAX.NS','THYROCARE.NS','TIMETECHNO.NS','TIMKEN.NS','TITAN.NS','TORNTPHARM.NS','TORNTPOWER.NS','TRENT.NS','TRIDENT.NS','TRITURBINE.NS','TIINDIA.NS','UCOBANK.NS','UFLEX.NS','UPL.NS','UJJIVAN.NS','ULTRACEMCO.NS','UNIONBANK.NS','UBL.NS','MCDOWELL-N.NS','VGUARD.NS','VMART.NS','VIPIND.NS','VRLLOG.NS','VSTIND.NS','WABAG.NS','VAIBHAVGBL.NS','VAKRANGEE.NS','VTL.NS','VARROC.NS','VBL.NS','VEDL.NS','VENKEYS.NS','VINATIORGA.NS','IDEA.NS','VOLTAS.NS','WABCOINDIA.NS','WELCORP.NS','WELSPUNIND.NS','WHIRLPOOL.NS','WIPRO.NS','WOCKPHARMA.NS','YESBANK.NS','ZEEL.NS','ZENSARTECH.NS','ZYDUSWELL.NS','ECLERX.NS']
    for symbol in symbolList:
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
    dtString = datetime.datetime.now(tz=india_tz).strftime("%d-%m-%Y")
    # print(outputDf)
    tmpPath = '/tmp/daily_MA_HMA_{}.csv'.format(dtString)
    uploadBucket = 'dart-analytics-dnd'
    outputDf.to_csv(tmpPath)

    s3_client = boto3.client('s3')
    s3_client.upload_file(tmpPath, uploadBucket, 'daily/daily_MA_HMA_{}.csv'.format(dtString))
    
    above2002percentNoCross = outputDf[(outputDf['Close'] >= outputDf['200SMA']) & (outputDf['Close'] <= 1.02 * outputDf['200SMA']) & (outputDf['ARB-200SMA'] == outputDf['ARB-200SMAprev1'])]
    below2002percentNoCross = outputDf[(outputDf['Close'] < outputDf['200SMA']) & (outputDf['Close'] >= 0.98 * outputDf['200SMA']) & (outputDf['ARB-200SMA'] == outputDf['ARB-200SMAprev1'])]
    above2002percentCross = outputDf[(outputDf['Close'] >= outputDf['200SMA']) & (outputDf['Close'] <= 1.02 * outputDf['200SMA']) & (outputDf['ARB-200SMA'] != outputDf['ARB-200SMAprev1'])]
    below2002percentCross = outputDf[(outputDf['Close'] < outputDf['200SMA']) & (outputDf['Close'] >= 0.98 * outputDf['200SMA']) & (outputDf['ARB-200SMA'] != outputDf['ARB-200SMAprev1'])]    
    
    # print(above2002percentNoCross['Symbol'].tolist())
    # print("\n".join(above2002percentNoCross['Symbol'].tolist()[0:]))
    
    SUBJECT = "Daily stock tracker"
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = "List of stocks aobve 200 SMA - within 2 percent"
    BODY_TEXT = BODY_TEXT + "\n\n" + "\n".join(above2002percentNoCross['Symbol'].tolist()[0:])
    BODY_TEXT = BODY_TEXT + "\n\n" + "List of stocks below 200 SMA - within 2 percent"
    BODY_TEXT = BODY_TEXT + "\n\n" + "\n".join(below2002percentNoCross['Symbol'].tolist()[0:])
    BODY_TEXT = BODY_TEXT + "\n\n" + "List of stocks aobve 200 SMA and corssed 200 SMA"
    BODY_TEXT = BODY_TEXT + "\n\n" + "\n".join(above2002percentCross['Symbol'].tolist()[0:])
    BODY_TEXT = BODY_TEXT + "\n\n" + "List of stocks below 200 SMA and crossed 200 SMA"
    BODY_TEXT = BODY_TEXT + "\n\n" + "\n".join(below2002percentCross['Symbol'].tolist()[0:])
    sendAWSMail('dartconsultants.hyd@gmail.com',SUBJECT,BODY_TEXT)
    # sendAWSMail(SUBJECT, BODY_TEXT)
    
    # above2002percentNoCross['Symbol'].series.to_csv('/home/ec2-user/environment/dart-stock-scan-lambda/above2002percentNoCross')
    # below2002percentNoCross['Symbol'].series.to_csv('/home/ec2-user/environment/dart-stock-scan-lambda/below2002percentNoCross')
    # above2002percentCross['Symbol'].series.to_csv('/home/ec2-user/environment/dart-stock-scan-lambda/above2002percentCross')
    # below2002percentCross['Symbol'].series.to_csv('/home/ec2-user/environment/dart-stock-scan-lambda/below2002percentCross')
    
    # print(above2002percent)
    # print(below2002percent)

    data = {
        'output': 'Hello World 11',
        'timestamp': datetime.datetime.utcnow().isoformat()
    }
    return {'statusCode': 200,
            'body': json.dumps(data),
            'headers': {'Content-Type': 'application/json'}}

    print("Hello")

if __name__== "__main__":
  main()







