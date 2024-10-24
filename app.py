from http.client import responses
import json
import requests
from flask import Flask, request, json, Response, jsonify
import os
import yfinance as yf
from sympy import timed, symbols
from yahoofinance import HistoricalPrices
from datetime import datetime,timedelta, date
import pandas as pd

from model.etf_model import ListOfETFModel
from model.inital_data import InitialData
from service.data_loader import load_initial_data

msft = yf.Ticker("MSFT")
app = Flask(__name__)

@app.route('/hello',methods=["GET"])
def hello_world():
    return 'Hello, World!'

@app.route('/ticker',methods=["GET"])
def get_ticker_price():
    stock=request.args.get("stock")
    print(stock)
    stock_data=yf.Ticker(stock)
    #print(stock_data.info)
    return {"price":stock_data.info}


@app.route('/historical',methods=["GET"])
def get_historical_price():
    stock=request.args.get("stock")
    stock_data=yf.Ticker(stock)
    #hist = msft.history(period="3mo")
    #print("hist",hist)
    historical_prices = HistoricalPrices(stock,
                                         start_date=(datetime.today()-timedelta(days=60)).strftime('%Y-%m-%d'),end_date=datetime.today().strftime('%Y-%m-%d'))
    return {"historical_data":historical_prices}


@app.route('/home', methods=["GET"])
def get_hello_world():
    if request.method == "GET":
        print(request.args)
        requestToken = request.args.get("requestToken")
        url = 'https://developer.paytmmoney.com/accounts/v2/gettoken'
        headers = {
            "Content-Type": "application/json"
        }
        try:
            # Make a GET request to the API endpoint using requests.get()
            response = requests.post(url, headers=headers, json={
                "api_key": os.getenv("API_KEY"),
                "api_secret_key": os.getenv("API_SECRET"),
                "request_token": requestToken
            })
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                response_json = response.json()
                print("token:"+requestToken)
                print(response_json)
                return {"token": requestToken, "response": response_json}
            else:
                print(response.text)
                return {"status":"failed"}
        except Exception:
            print("Exception encountered")
        finally:
            print("in finally block")

@app.route('/funds', methods=["GET"])
def get_funds_info():
    token= request.headers.get("token")
    if request.method == "GET":
        url = 'https://developer.paytmmoney.com/accounts/v1/funds/summary?config=true'
        headers = {
            "x-jwt-token": token
        }
        try:
            # Make a GET request to the API endpoint using requests.get()
            response = requests.get(url, headers=headers)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                response_json = response.json()
                print("yes")
                return {"balance": response_json["data"]["funds_summary"]["trade_balance"]}
            else:
                print("no")
                return {"balance":0.0}
        except Exception as e:
            print(e)
            print("Exception encountered")
        finally:
            print("in finally block")

@app.route('/order', methods=["POST"])
def place_order():
    token= request.headers["token"]
    if request.method == 'POST':
        stock_nse_id = request.get_json()['stock_nse_id']
        stock_sec_id = request.get_json()['stock_sec_id']
        quantity = request.get_json()['quantity']
        url = 'https://developer.paytmmoney.com/orders/v1/place/regular'
        headers = {
            "x-jwt-token": token,
            "Content-Type": "application/json"
        }
        try:
            print(os.getenv("API"))
            funds_response=requests.get(os.getenv("API")+"/funds",headers={
                "token":token
            })
            print("funds ",funds_response.json())
            stock_price=requests.get(os.getenv("API")+"/ticker?stock="+stock_nse_id)
            if funds_response.status_code ==200 and stock_price.status_code==200:
                if funds_response.json()["balance"] > stock_price.json()["price"]["ask"]*quantity:
                    response = requests.post(url, headers=headers, json={
                        "txn_type": "B",
                        "exchange": "NSE",
                        "segment": "E",
                        "product": "C",
                        "security_id": stock_sec_id,
                        "quantity": quantity,
                        "validity": "DAY",
                        "order_type": "MKT",
                        "price":0,
                        "source": "N",
                        "off_mkt_flag": "false"
                    })
                    print("response", response.text)
                    # Check if the request was successful (status code 200)
                    if response.status_code == 200:
                        response_json = response.json()

                        if response_json["status"]=="success":
                            return {"status":"0"}
                        else:
                            print(response.text)
                            return {"status":"3"}
                    else:
                        print(response.text)
                        return {"status": "3"}
                else:
                    print("balance not available")
                    return {"status":"2"}
            else:
                return {"status": "1"}
        except Exception as e:
            print("Exception:", e )
            return {"status": "3"}
        finally:
            print("in finally block")

@app.route('/book', methods=["GET"])
def get_order_book():
        if request.method == "GET":
            order = request.args.get("order_no")
            token = request.headers["token"]
            url = 'https://developer.paytmmoney.com/orders/v1/trade-details?leg_no=1&segment=D&order_no='+order
            headers = {
                "Content-Type": "application/json",
                "x-jwt-token":token
            }
            try:
                # Make a GET request to the API endpoint using requests.get()
                response = requests.get(url,headers=headers)
                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    response_json = response.json()
                    return {"response": response_json}
                else:
                    print(response.text)
                    return {"status": "failed"}
            except Exception:
                print("Exception encountered")
            finally:
                print("in finally block")


@app.before_request
def before_first_request():
    load_initial_data()
    #pandas_df = pd.read_csv("etf_security_master.csv")
    #symbols = pandas_df["symbol"].tolist()
    #InitialData.symbols_with_prices=symbols
@app.route('/ranks', methods=["GET"])
def get_historical_prices():
    list_etf_models=load_initial_data()
    symbols = list_etf_models.etfs
    symbols=list(filter(lambda symbol: "Nifty" in symbol.name, symbols))
    #print("symbols", InitialData.symbols_with_prices)
    symbol_pricing_map={}
    stock = request.args.get("stock")
    if stock:
        get_stock_information = yf.Ticker(stock)
        if "ask" in get_stock_information.info:
            current_price = get_stock_information.info["ask"]
        else:
            current_price = get_stock_information.info["previousClose"]

        if "fiftyDayAverage" in get_stock_information.info:
            price_percentage = ((current_price - get_stock_information.info["fiftyDayAverage"]) * 100.0) / \
                                              get_stock_information.info["fiftyDayAverage"]
        else:
            startDate = (datetime.today() - timedelta(days=60)).strftime('%Y-%m-%d')
            endDate = datetime.today()
            df = get_stock_information.history(start=startDate, end=endDate)
            sixty_day_average_close = df["Close"].astype("int64").mean()
            price_percentage = ((current_price - sixty_day_average_close) * 100.0) / sixty_day_average_close
        print(price_percentage)
        return {"price":price_percentage}
    else:
        for symbol in symbols:
            symbol_name=symbol.symbol+".NS"
            get_stock_information = yf.Ticker(symbol_name)
            if "ask" in get_stock_information.info:
                current_price=get_stock_information.info["ask"]
            else:
                current_price = get_stock_information.info["previousClose"]

            if "fiftyDayAverage" in get_stock_information.info:
                symbol.percentage=((current_price-get_stock_information.info["fiftyDayAverage"]) * 100.0) / get_stock_information.info["fiftyDayAverage"]
                symbol_pricing_map[symbol_name]=((current_price-get_stock_information.info["fiftyDayAverage"]) * 100.0) / get_stock_information.info["fiftyDayAverage"]
            '''
            else:
                startDate = (datetime.today() - timedelta(days=60)).strftime('%Y-%m-%d')
                endDate = datetime.today()
                df = get_stock_information.history(start=startDate, end=endDate)
                sixty_day_average_close=df["Close"].astype("int64").mean()
                symbol_pricing_map[symbol_name] = ((current_price - sixty_day_average_close) * 100.0) / sixty_day_average_close
            '''
        print(len(symbols))
        symbols=list(filter(lambda symbol: symbol.percentage!=0.0, symbols))
        print(len(symbols))
        symbols.sort(key=lambda symbol:symbol.percentage)
        '''
        sorted_symbol_pricing_map={k: v for k, v in sorted(symbol_pricing_map.items(), key=lambda item: item[1])}
        print("map", sorted_symbol_pricing_map)
        list_final_symbols=sorted_symbol_pricing_map.keys()
        print("sorted",sorted_symbol_pricing_map)
        '''
        return Response(
        response=json.dumps({
            "data": {
                "data": [etf.to_dict() for etf in symbols]
            }
        }),
        status=201,
        mimetype="application/json"
    )

    '''
    GetFacebookInformation = yf.Ticker("SMALLCAP.NS")

    pd.set_option('display.max_rows', None)
    startDate = (datetime.today()-timedelta(days=60)).strftime('%Y-%m-%d')
    endDate = datetime.today()
    df=GetFacebookInformation.history(start=startDate,end=endDate)
    print("close",df["Close"].astype("int64").mean())

    stock_data = yf.Ticker("SMALLCAP.NS")
    print(stock_data.info["ask"])

    per = ((stock_data.info["ask"]-df["Close"].astype("int64").mean()) * 100.0) / df["Close"].astype("int64").mean()
    print("20DMA",per)
    print("Daily", ((stock_data.info["ask"]-stock_data.info["fiftyDayAverage"]) * 100.0) / stock_data.info["fiftyDayAverage"])
    print("max",df["Close"].max())
    print("min", df["Close"].min())
    '''
if __name__ == '__main__':
    app.run()
    #get_historical_prices()
    '''
   app.run()
   n=0
   while n==0:
       print("hi")
       stock_price=requests.get(os.getenv("API")+"/ticker?stock=NIFTYETF.NS")
       print("stock",stock_price.json())
    '''


