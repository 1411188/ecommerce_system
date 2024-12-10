import requests
from requests.auth import HTTPBasicAuth

def generate_access_token():
    consumer_key = "your_consumer_key"
    consumer_secret = "your_consumer_secret"
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise Exception("Failed to generate access token: " + response.text)

