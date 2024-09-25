# STRADDLE PREMIUM IN CSV FILE LIVE


import credentials as crs
import time
import pandas as pd
from datetime import datetime
from fyers_api import fyersModel, accessToken

# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
import webbrowser

# Replace these values with your actual API credentials
client_id = crs.client_id
secret_key = crs.secret_key
redirect_uri = crs.redirect_uri
response_type = "code"  
state = "sample_state"

# Create a session model with the provided credentials
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type

)

# Generate the auth code using the session model
response = session.generate_authcode()

# Print the auth code received in the response
print(response)

webbrowser.open(response,new=1)


newurl = input("Enter the url: ")
auth_code = newurl[newurl.index('auth_code=')+10:newurl.index('&state')]
print(auth_code)


grant_type = "authorization_code" 
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key, 
    redirect_uri=redirect_uri, 
    response_type=response_type, 
    grant_type=grant_type
)

# Set the authorization code in the session object
session.set_token(auth_code)

# Generate the access token using the authorization code
response = session.generate_token()

# Print the response, which should contain the access token and other details
print(response)


# There can be two cases over here you can successfully get the acccessToken over the request or you might get some error over here. so to avoid that have this in try except block
try: 
    access_token = response["access_token"]
    with open('access.txt','w') as k:
        k.write(access_token)
except Exception as e:
    print(e,response)  ## This will help you in debugging then and there itself like what was the error and also you would be able to see the value you got in response variable. instead of getting key_error for unsuccessfull response.


fyers = fyersModel.FyersModel(client_id=client_id, token=access_token, log_path='log/')

# THIS CODE USE FOR NIFTY50 INDEX

symbol = 'NSE:NIFTY50-INDEX'

def fetch_atm_premiums():
    quote = fyers.quotes({"symbols": symbol})
    print("Underlying Quote Response:", quote)  # Debugging
    if quote['s'] == 'ok':
        data = quote['d'][0]
        ltp = data['v']['lp']  # Last traded price
        
        # Assuming strike prices are rounded to the nearest 50
        strike_price = round(ltp / 50) * 50
        print(strike_price)
        
        # Correct format: DDMMMYYYY (e.g., 29AUG2024)
        expiry = '24822'  # Use the correct expiry date "symbol":"NSE:NIFTY2451622000PE"
        call_symbol = f'NSE:NIFTY{expiry}{strike_price}CE'
        put_symbol = f'NSE:NIFTY{expiry}{strike_price}PE'

        # Fetch Call Premium
        call_quote = fyers.quotes({"symbols": call_symbol})
        print("Call Option Quote Response:", call_quote)  # Debugging
        call_premium = None
        if call_quote['s'] == 'ok' and 'd' in call_quote and 'lp' in call_quote['d'][0]['v']:
            call_premium = call_quote['d'][0]['v']['lp']
        else:
            print(f"Failed to fetch call premium for symbol {call_symbol}. Error: {call_quote}")

        # Fetch Put Premium
        put_quote = fyers.quotes({"symbols": put_symbol})
        print("Put Option Quote Response:", put_quote)  # Debugging
        put_premium = None
        if put_quote['s'] == 'ok' and 'd' in put_quote and 'lp' in put_quote['d'][0]['v']:
            put_premium = put_quote['d'][0]['v']['lp']
        else:
            print(f"Failed to fetch put premium for symbol {put_symbol}. Error: {put_quote}")

        return strike_price, call_premium, put_premium
    else:
        print("Failed to get underlying quote")
        return None, None, None

def store_premiums():
    while True:
        strike_price, call_premium, put_premium = fetch_atm_premiums()
        if strike_price and call_premium and put_premium:
            total_premium = call_premium + put_premium
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df = pd.DataFrame([[current_time, strike_price, call_premium, put_premium, total_premium]], 
                              columns=['Timestamp', 'Strike_Price', 'Call_Premium', 'Put_Premium', 'Total_Premium'])
            df.to_csv('atm_premiums.csv', mode='a', header=False, index=False)
            print(f"Stored ATM premiums: Strike Price: {strike_price}, Call: {call_premium}, Put: {put_premium}, Total: {total_premium} at {current_time}", flush=True)
        else:
            print("Failed to fetch ATM premiums", flush=True)
        time.sleep(300)  # Sleep for 5 minutes

# Create the CSV file and write the header if it doesn't exist
df = pd.DataFrame(columns=['Timestamp', 'Strike_Price', 'Call_Premium', 'Put_Premium', 'Total_Premium'])
df.to_csv('atm_premiums.csv', mode='w', header=True, index=False)

# Start storing the premiums
store_premiums()






# # THIS CODE USE FOR NIFTY BANK - INDEX

# symbol = 'NSE:NIFTYBANK-INDEX'

# def fetch_atm_premiums():
#     quote = fyers.quotes({"symbols": symbol})
#     print("Underlying Quote Response:", quote)  # Debugging
#     if quote['s'] == 'ok':
#         data = quote['d'][0]
#         ltp = data['v']['lp']  # Last traded price
        
#         # Assuming strike prices are rounded to the nearest 50
#         strike_price = round(ltp / 100) * 100
#         print(strike_price)
        
#         # Correct format: DDMMMYYYY (e.g., 29AUG2024)
#         expiry = '24AUG'  # Use the correct expiry date "symbol":"NSE:NIFTY2451622000PE"
#         call_symbol = f'NSE:BANKNIFTY{expiry}{strike_price}CE'
#         put_symbol = f'NSE:BANKNIFTY{expiry}{strike_price}PE'

#         # Fetch Call Premium
#         call_quote = fyers.quotes({"symbols": call_symbol})
#         print("Call Option Quote Response:", call_quote)  # Debugging
#         call_premium = None
#         if call_quote['s'] == 'ok' and 'd' in call_quote and 'lp' in call_quote['d'][0]['v']:
#             call_premium = call_quote['d'][0]['v']['lp']
#         else:
#             print(f"Failed to fetch call premium for symbol {call_symbol}. Error: {call_quote}")

#         # Fetch Put Premium
#         put_quote = fyers.quotes({"symbols": put_symbol})
#         print("Put Option Quote Response:", put_quote)  # Debugging
#         put_premium = None
#         if put_quote['s'] == 'ok' and 'd' in put_quote and 'lp' in put_quote['d'][0]['v']:
#             put_premium = put_quote['d'][0]['v']['lp']
#         else:
#             print(f"Failed to fetch put premium for symbol {put_symbol}. Error: {put_quote}")

#         return strike_price, call_premium, put_premium
#     else:
#         print("Failed to get underlying quote")
#         return None, None, None

# def store_premiums():
#     while True:
#         strike_price, call_premium, put_premium = fetch_atm_premiums()
#         if strike_price and call_premium and put_premium:
#             total_premium = call_premium + put_premium
#             current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#             df = pd.DataFrame([[current_time, strike_price, call_premium, put_premium, total_premium]], 
#                               columns=['Timestamp', 'Strike_Price', 'Call_Premium', 'Put_Premium', 'Total_Premium'])
#             df.to_csv('atm_premiums.csv', mode='a', header=False, index=False)
#             print(f"Stored ATM premiums: Strike Price: {strike_price}, Call: {call_premium}, Put: {put_premium}, Total: {total_premium} at {current_time}", flush=True)
#         else:
#             print("Failed to fetch ATM premiums", flush=True)
#         time.sleep(60)  # Sleep for 5 minutes

# # Create the CSV file and write the header if it doesn't exist
# df = pd.DataFrame(columns=['Timestamp', 'Strike_Price', 'Call_Premium', 'Put_Premium', 'Total_Premium'])
# df.to_csv('atm_premiums.csv', mode='a', header=True, index=False)

# # Start storing the premiums
# store_premiums()




# # use this code for FINNIFTY INDEX

# symbol = 'NSE:FINNIFTY-INDEX'

# def fetch_atm_premiums():
#     quote = fyers.quotes({"symbols": symbol})
#     print("Underlying Quote Response:", quote)  # Debugging
#     if quote['s'] == 'ok':
#         data = quote['d'][0]
#         ltp = data['v']['lp']  # Last traded price
        
#         # Assuming strike prices are rounded to the nearest 50
#         strike_price = round(ltp / 50) * 50  #this is for finnifty and nifty 
#         print(strike_price)
        
#         # Correct format: DDMMMYYYY (e.g., 29AUG2024)
#         expiry = '24SEP'  # Use the correct expiry date "symbol":"NSE:NIFTY2451622000PE"
#         call_symbol = f'NSE:FINNIFTY{expiry}{strike_price}CE'
#         put_symbol = f'NSE:FINNIFTY{expiry}{strike_price}PE'

#         # Fetch Call Premium
#         call_quote = fyers.quotes({"symbols": call_symbol})
#         print("Call Option Quote Response:", call_quote)  # Debugging
#         call_premium = None
#         if call_quote['s'] == 'ok' and 'd' in call_quote and 'lp' in call_quote['d'][0]['v']:
#             call_premium = call_quote['d'][0]['v']['lp']
#         else:
#             print(f"Failed to fetch call premium for symbol {call_symbol}. Error: {call_quote}")

#         # Fetch Put Premium
#         put_quote = fyers.quotes({"symbols": put_symbol})
#         print("Put Option Quote Response:", put_quote)  # Debugging
#         put_premium = None
#         if put_quote['s'] == 'ok' and 'd' in put_quote and 'lp' in put_quote['d'][0]['v']:
#             put_premium = put_quote['d'][0]['v']['lp']
#         else:
#             print(f"Failed to fetch put premium for symbol {put_symbol}. Error: {put_quote}")

#         return strike_price, call_premium, put_premium
#     else:
#         print("Failed to get underlying quote")
#         return None, None, None

# def store_premiums():
#     while True:
#         strike_price, call_premium, put_premium = fetch_atm_premiums()
#         if strike_price and call_premium and put_premium:
#             total_premium = call_premium + put_premium
#             current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#             df = pd.DataFrame([[current_time, strike_price, call_premium, put_premium, total_premium]], 
#                               columns=['Timestamp', 'Strike_Price', 'Call_Premium', 'Put_Premium', 'Total_Premium'])
#             df.to_csv('atm_premiums.csv', mode='a', header=False, index=False)
#             print(f"Stored ATM premiums: Strike Price: {strike_price}, Call: {call_premium}, Put: {put_premium}, Total: {total_premium} at {current_time}", flush=True)
#         else:
#             print("Failed to fetch ATM premiums", flush=True)
#         time.sleep(300)  # Sleep for 5 minutes

# # Create the CSV file and write the header if it doesn't exist
# df = pd.DataFrame(columns=['Timestamp', 'Strike_Price', 'Call_Premium', 'Put_Premium', 'Total_Premium'])
# df.to_csv('atm_premiums.csv', mode='w', header=True, index=False)

# # Start storing the premiums
# store_premiums()
