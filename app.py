from http.client import responses

import requests
from flask import Flask, request
import os
import yfinance as yf

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
    print(stock_data.info)
    return {"price":stock_data.info["open"]}


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
                print("response:"+response_json)
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
            "x-jwt-token:": token,
            "Content-Type": "application/json"
        }
        try:
            print(os.getenv("API"))
            funds_response=requests.get(os.getenv("API")+"/funds",headers={
                "token":token
            })
            stock_price=requests.get(os.getenv("API")+"/ticker?stock="+stock_nse_id)
            if funds_response.status_code ==200 and stock_price.status_code==200:
                if funds_response.json()["balance"] > stock_price.json()["price"]*quantity:
                    response = requests.post(url, headers=headers, json={
                        "txn_type": "B",
                        "exchange": "BSE",
                        "segment": "E",
                        "product": "I",
                        "security_id": stock_sec_id,
                        "quantity": quantity,
                        "validity": "DAY",
                        "order_type": "MKT",
                        "price": 0,
                        "source": "N",
                        "off_mkt_flag": "false"
                    })
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
        except Exception:
            print("Exception encountered")
            return {"status": "3"}
        finally:
            print("in finally block")

if __name__ == '__main__':
   app.run()