from flask import Flask, request 
import requests

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
@app.route('/home', methods=["GET"])
def get_hello_world():
    if request.method == "GET":
        print(request.args)
        requestToken = request.args.get("requestToken")
        print(requestToken)
        url = 'https://developer.paytmmoney.com/accounts/v2/gettoken'
        headers = {
            "Content-Type": "application/json"
        }
        try:
            # Make a GET request to the API endpoint using requests.get()
            response = requests.post(url, headers=headers, json={
                "api_key": "xxx",
                "api_secret_key": "xxx",
                "request_token": requestToken
            })
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                response_json = response.json()
                return {"token": requestToken, "response": response_json}
            else:
                print(response.text)
        except Exception:
            print("Exception encountered")
        finally:
            print("in finally block")
