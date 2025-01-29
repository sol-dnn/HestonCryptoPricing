'''
Test Deribit Database:

API ID : _IhAu5WF
API KEY Name : opption_pricing
API KEY : gRzhL4N9iapzEtv3hgnHyJH4G4Bwafwhru6HWaGf3zk

Get a crypto options data ( price, implied volatility, strike, maturity, etc..) on BTC-USD and ETH-USD for a random day
If possible, get an option chain on Deribit (conséq data for a week or one month)

'''

import asyncio
import websockets
import json
import datetime


import asyncio
import websockets
import json
import pandas as pd
import datetime



# Function to convert timestamp to a readable date
def timestamp_to_date(ts):
    return datetime.datetime.utcfromtimestamp(ts / 1000.0).strftime('%Y-%m-%d %H:%M:%S')


def get_unix_timestamp(year, month, day):
    """Converts a given date to a UNIX timestamp in milliseconds."""
    dt = datetime.datetime(year, month, day, tzinfo=datetime.timezone.utc)
    return int(dt.timestamp() * 1000)  # convert seconds to milliseconds

# Function to get the mean of the top bid and ask prices and their implied volatilities
def get_mean_bid_ask(data):
    bids = data.get('bids', [])
    asks = data.get('asks', [])
    if bids and asks:
        mean_price = (bids[0][0] + asks[0][0]) / 2
        if 'bid_iv' in data and 'ask_iv' in data:
            mean_iv = (data['bid_iv'] + data['ask_iv']) / 2
        else:
            mean_iv = None
    else:
        mean_price = None
        mean_iv = None
    return mean_price, mean_iv



'''async def fetch_last_trade(instrument_name, url):
    start_timestamp = get_unix_timestamp(2020, 1, 1)  # Far back to ensure all trades are covered
    msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "public/get_last_trades_by_instrument_and_time",
        "params": {
            "instrument_name": instrument_name,
            "start_timestamp": start_timestamp,
            "count": 1,
            "sorting": "desc"  # Ensure we're getting the most recent first
        }
    }
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        data = json.loads(response)
        if 'error' in data:
            print("Error received from API:", data['error'])
            return {}
        last_trade = data['result']['trades'][0] if data['result']['trades'] else None
        if last_trade:
            return {
                "price": last_trade.get("price"),
                "index_price": last_trade.get("index_price"),
                "implied_volatility": last_trade.get("iv"),
                "timestamp": timestamp_to_date(last_trade.get("timestamp"))
            }
        return {}
    '''

async def fetch_order_book(instrument_name, url):
    msg = {
        "jsonrpc": "2.0",
        "id": 8772,
        "method": "public/get_order_book",
        "params": {
            "instrument_name": instrument_name,
            "depth": 1
        }
    }
    async with websockets.connect(url) as websocket:
        await websocket.send(json.dumps(msg))
        response = await websocket.recv()
        data = json.loads(response)
        if 'error' in data:
            print("Error received from API:", data['error'])
            return {}
        result = data.get('result', {})
        mean_price, mean_iv = get_mean_bid_ask(result)
        return {
            "mean_bid_ask_price": mean_price,
            "mean_bid_ask_iv": mean_iv,
            "mark_price": result.get("mark_price"),
            "last_price": result.get("last_price"),
            "mark_iv": result.get("mark_iv"),
            "timestamp": timestamp_to_date(result.get("timestamp"))
        }


async def fetch_options_data(msg, url):
    async with websockets.connect(url) as websocket:
        await websocket.send(msg)
        response = await websocket.recv()
        data = json.loads(response)
        if 'error' in data:
            print("Error received from API:", data['error'])
            return pd.DataFrame()  # Return empty DataFrame on error
        instruments = data.get('result', [])
        options_data = []
        for instrument in instruments:
            instrument_name = instrument.get("instrument_name", "")
            last_trade_data = await fetch_last_trade(instrument_name, url)  # Make sure to use await here
            instrument_data = {
                "kind": instrument.get("kind", ""),
                "option_type": instrument.get("option_type", ""),
                "base_currency": instrument.get("base_currency", ""),
                "strike": instrument.get("strike", ""),
                "creation": timestamp_to_date(instrument.get("creation_timestamp", 0)),
                "maturity": timestamp_to_date(instrument.get("expiration_timestamp", 0)),
                "last_trade_price": last_trade_data.get("price") if last_trade_data else None,
                "last_mark_price": last_trade_data.get("mark_price") if last_trade_data else None,
                "last_trade_index_price": last_trade_data.get("index_price") if last_trade_data else None,
                "last_trade_iv": last_trade_data.get("implied_volatility") if last_trade_data else None
                }
            options_data.append(instrument_data)
        return pd.DataFrame(options_data)
 

# Define the API message to fetch options instruments
btc_get_instruments_message = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "public/get_instruments",
    "params": {
        "currency": "BTC",
        "kind": "option"
    }
})

eth_get_instruments_message = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "public/get_instruments",
    "params": {
        "currency": "ETH",
        "kind": "option"
    }
})

url = 'wss://test.deribit.com/ws/api/v2'

# Run the async functions and get the DataFrame
btc_options = asyncio.run(fetch_options_data(btc_get_instruments_message, url))
eth_options = asyncio.run(fetch_options_data(eth_get_instruments_message, url))

print(btc_options)
print(eth_options)

# Run the async functions and get the DataFrame
btc_options = btc_options.dropna()
eth_options = eth_options.dropna()

# Filtrage pour exclure les lignes où la volatilité implicite est égale à 0
btc_options = btc_options[btc_options['last_trade_iv'] != 0]
eth_options = eth_options[eth_options['last_trade_iv'] != 0]


print(btc_options)
print(eth_options)


btc_options.to_csv("btc_options.csv", index=False)
eth_options.to_csv("eth_options.csv", index=False)
