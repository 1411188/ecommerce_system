from .utils import generate_access_token
import requests

def initiate_stk_push(amount, phone_number, account_reference, transaction_desc):
    access_token = generate_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    stk_data = {
        "BusinessShortCode": "174379",
        "Password": "Base64EncodedPassword",
        "Timestamp": "20241209120100",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": "174379",
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/shop/daraja/callback/",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }
    
    response = requests.post(api_url, json=stk_data, headers=headers)
    return response.json()

