import asyncio
import websockets
import json
import pandas as pd
import datetime

# Function to convert timestamp to a readable date
def timestamp_to_date(ts):
    return datetime.datetime.utcfromtimestamp(ts / 1000.0).strftime('%Y-%m-%d %H:%M:%S')

# Fetches the order book and calculates the mean of the best bid and ask prices
async def fetch_order_book(instrument_name, url):
    msg = {
        "jsonrpc": "2.0",
        "id": 8772,
        "method": "public/get_order_book",
        "params": {
            "instrument_name": instrument_name,
            "depth": 1  # Adjusted to only fetch the topmost bid and ask
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
        if result:
            bids = result.get('bids', [])
            asks = result.get('asks', [])
            if bids and asks:
                mark_price = result.get("mark_price")
                last_price = result.get("last_price")
                mark_iv = result.get("mark_iv")
                index_price = result.get("index_price")
                return {
                    "mark_price": mark_price,
                    "last_price": last_price,
                    "mark_iv": mark_iv,
                    "index_price":index_price
                }
        return {}

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
            order_book_data = await fetch_order_book(instrument_name, url)  # Fetch order book data
            instrument_data = {
                "option_type": instrument.get("option_type", ""),
                "strike": instrument.get("strike", ""),
                "creation": timestamp_to_date(instrument.get("creation_timestamp", 0)),
                "maturity": timestamp_to_date(instrument.get("expiration_timestamp", 0)),
                "mark_price": order_book_data.get("mark_price"),
                "last_price": order_book_data.get("last_price"),
                "mark_iv": order_book_data.get("mark_iv"),
                "index_price":order_book_data.get("index_price")
            }
            options_data.append(instrument_data)
        return pd.DataFrame(options_data)

url = 'wss://test.deribit.com/ws/api/v2'



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


print(btc_options)
print(eth_options)


btc_options.to_csv("btc_options.csv", index=False)
eth_options.to_csv("eth_options.csv", index=False)

