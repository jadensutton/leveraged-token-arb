import numpy as np

from time import sleep
from datetime import datetime
from datetime import timedelta
from binance.client import Client
from binance.enums import *

assets = {
    "XLMUSDT": {"candles": [], "candles_up": [], "trade_placed": False, "up": "XLMUPUSDT", "size": 0, "time_in_trade": 0},
    "AAVEUSDT": {"candles": [], "candles_up": [], "trade_placed": False, "up": "AAVEUPUSDT", "size": 0, "time_in_trade": 0},
    "YFIUSDT": {"candles": [], "candles_up": [], "trade_placed": False, "up": "YFIUPUSDT", "size": 0, "time_in_trade": 0},
    "DOTUSDT": {"candles": [], "candles_up": [], "trade_placed": False, "up": "DOTUPUSDT", "size": 0, "time_in_trade": 0},
    "TRXUSDT": {"candles": [], "candles_up": [], "trade_placed": False, "up": "TRXUPUSDT", "size": 0, "time_in_trade": 0}
}

API_KEY = "YOUR API KEY"
SECRET_KEY = "YOUR SECRET KEY"

period = 180
active_trades = 0
active_algos = 1
num_assets = len (assets)

slippage = 0.0004
transaction_fee = 0.001
spread = 0.004

print ("Loading API client...")
client = Client (API_KEY, SECRET_KEY)

print ("\nDone!")

def get_historical_data ():
    for ticker in assets:
        print ("\nGetting historical OHLC data for " + ticker + "...")
        klines = client.get_historical_klines (ticker, Client.KLINE_INTERVAL_3MINUTE, "12 minutes ago UTC")
        klines_up = client.get_historical_klines (assets[ticker]["up"], Client.KLINE_INTERVAL_3MINUTE, "12 minutes ago UTC")

        for i in range (len (klines)):
            assets[ticker]["candles"].append ([float (klines[i][1]), float (klines[i][2]), float (klines[i][3]), float (klines[i][4])])
            assets[ticker]["candles_up"].append ([float (klines_up[i][1]), float (klines_up[i][2]), float (klines_up[i][3]), float (klines_up[i][4])])

        assets[ticker]["candles"] = assets[ticker]["candles"][-1:]
        assets[ticker]["candles_up"] = assets[ticker]["candles_up"][-1:]
        print ("\nDone!\n")

def update_data ():
    for ticker in assets:
        success = False
        while success == False:
            try:
                new_candle = list (map (float, client.get_klines (symbol=ticker, interval=Client.KLINE_INTERVAL_3MINUTE)[-1][1:5]))
                success = True

            except Exception as e:
                print (e)

        assets[ticker]["candles"].append (new_candle)
        assets[ticker]["candles"].pop (0)

        success = False
        while success == False:
            try:
                new_candle_up = list (map (float, client.get_klines (symbol=assets[ticker]["up"], interval=Client.KLINE_INTERVAL_3MINUTE)[-1][1:5]))
                success = True

            except Exception as e:
                print (e)

        assets[ticker]["candles_up"].append (new_candle_up)
        assets[ticker]["candles_up"].pop (0)

def place_trade (ticker, size):
    token = assets[ticker]["up"]
    price = float (client.get_avg_price (symbol=token)["price"])
    quantity = (size / price) // 0.01 / 100

    order = client.order_market_buy (
        symbol=token,
        quantity=quantity
    )

    global active_trades
    active_trades += 1

def close_position (ticker):
    token = assets[ticker]["up"]
    coin = token.replace ("USDT", "")
    quantity = float (client.get_asset_balance (asset=coin)["free"]) // 0.01 / 100

    order = client.order_market_sell (
        symbol=token,
        quantity=quantity
    )

    global active_trades
    active_trades -= 1

def generate_signal (ticker, capital_divisor):
    candles = assets[ticker]["candles"]
    candles_up = assets[ticker]["candles_up"]

    opens = []
    closes = []
    for candle in candles:
        opens.append (candle[0])
        closes.append (candle[3])

    opens_up = []
    closes_up = []
    for candle in candles_up:
        opens_up.append (candle[0])
        closes_up.append (candle[3])

    curr_open = opens[-1]
    curr_close = closes[-1]
    curr_open_up = opens_up[-1]
    curr_close_up = closes_up[-1]

    if curr_close > curr_open and curr_close_up < curr_open_up and (curr_open_up / curr_close_up - 1) > (spread +  2 * slippage + 2 * transaction_fee):
        size = capital / (capital_divisor * active_algos)

        print ("\nBUY ORDER", assets[ticker]["up"])
        print ("Price:", curr_close)
        print ("")

        assets[ticker]["trade_placed"] = True
        assets[ticker]["time_in_trade"] = 0

        return True, size

    return False, None

def check_position (ticker):
    candles = assets[ticker]["candles"]
    time_in_trade = assets[ticker]["time_in_trade"]
    time_in_trade += 1

    if time_in_trade >= 3:
        print ("EXIT", assets[ticker]["up"])

        close_position (ticker)

        assets[ticker]["trade_placed"] = False
        assets[ticker]["time_in_trade"] = 0

    else:
        assets[ticker]["time_in_trade"] = time_in_trade

get_historical_data ()

start_at = datetime (2021, 1, 13, 4, 0, 58)
prev_candle = start_at
now = datetime.now ()
while now != start_at:
    now = datetime.now ()

while True:
    next_candle = prev_candle + timedelta (seconds=period)

    for ticker in assets:
        if assets[ticker]["trade_placed"] == False:
            capital = float (client.get_asset_balance (asset="USDT")["free"]) * 0.95
            signal, size = generate_signal (ticker, (num_assets - active_trades))
            if signal == True:
                place_trade (ticker, size)

        else:
            check_position (ticker)

    capital = float (client.get_asset_balance (asset="USDT")["free"]) * 0.95
    print ("\nSummary")
    print ("\tAvailable Balance: $" + str (capital))
    print ("\tActive Trades:", active_trades)

    prev_candle = next_candle
    now = datetime.now ()
    while now != next_candle:
        now = datetime.now ()

    update_data ()
