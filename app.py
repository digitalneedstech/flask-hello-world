from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/test')
def hello_world():
    return 'Hello, World!'
@app.route('/home', methods=["GET"])
def hello_world():
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
                "api_key": "a254798bb6084fbf95cb1e5512c2781d",
                "api_secret_key": "35919b6920f742b891c69b32e34545c4",
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
