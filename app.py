import json
import requests
import boto3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root(requestToken):
    print(requestToken)
    url = 'https://developer.paytmmoney.com/accounts/v2/gettoken'
    headers = {
        "Content-Type": "application/json"
    }
    response_json = ""
    try:
        # Make a GET request to the API endpoint using requests.get()
        response = requests.post(url, headers=headers, data={
            "api_key": "a254798bb6084fbf95cb1e5512c2781d",
            "api_secret_key": "35919b6920f742b891c69b32e34545c4",
            "request_token": requestToken
        })
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            response_json = response.json()
            print(response_json)
            return response_json
        else:
            print('Error:', response.status_code)
    finally:
        print("in finally block")
    return {"token": requestToken, "response": response_json}
