import math
import statistics

import tulipy as ti
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from time import sleep
from binance.client import Client
from binance.enums import *
from scipy import stats
from sklearn import linear_model
from sklearn.utils import shuffle
from time import sleep

assets = {
    "XLMUSDT": {"candles": [], "candles_up": [], "candles_down": [], "trade_placed": False, "type_of_trade": None, "up": "XLMUPUSDT", "down": "XLMDOWNUSDT", "size": 0, "time_in_trade": 0, "entry_price": None, "winning_trades": [], "losing_trades": [], "num_wins": 0, "num_losses": 0, "buy_and_hold_return": 0},
    "AAVEUSDT": {"candles": [], "candles_up": [], "candles_down": [], "trade_placed": False, "type_of_trade": None, "up": "AAVEUPUSDT", "down": "AAVEDOWNUSDT", "size": 0, "time_in_trade": 0, "entry_price": None, "winning_trades": [], "losing_trades": [], "num_wins": 0, "num_losses": 0, "buy_and_hold_return": 0},
    "YFIUSDT": {"candles": [], "candles_up": [], "candles_down": [], "trade_placed": False, "type_of_trade": None, "up": "YFIUPUSDT", "down": "YFIDOWNUSDT", "size": 0, "time_in_trade": 0, "entry_price": None, "winning_trades": [], "losing_trades": [], "num_wins": 0, "num_losses": 0, "buy_and_hold_return": 0},
    "DOTUSDT": {"candles": [], "candles_up": [], "candles_down": [], "trade_placed": False, "type_of_trade": None, "up": "DOTUPUSDT", "down": "DOTUSDT", "size": 0, "time_in_trade": 0, "entry_price": None, "winning_trades": [], "losing_trades": [], "num_wins": 0, "num_losses": 0, "buy_and_hold_return": 0},
    "TRXUSDT": {"candles": [], "candles_up": [], "candles_down": [], "trade_placed": False, "type_of_trade": None, "up": "TRXUPUSDT", "down": "TRXDOWNUSDT", "size": 0, "time_in_trade": 0, "entry_price": None, "winning_trades": [], "losing_trades": [], "num_wins": 0, "num_losses": 0, "buy_and_hold_return": 0},
    "EOSUSDT": {"candles": [], "candles_up": [], "candles_down": [], "trade_placed": False, "type_of_trade": None, "up": "EOSUPUSDT", "down": "EOSDOWNUSDT", "size": 0, "time_in_trade": 0, "entry_price": None, "winning_trades": [], "losing_trades": [], "num_wins": 0, "num_losses": 0, "buy_and_hold_return": 0},
    "LINKUSDT": {"candles": [], "candles_up": [], "candles_down": [], "trade_placed": False, "type_of_trade": None, "up": "LINKUPUSDT", "down": "LINKDOWNUSDT", "size": 0, "time_in_trade": 0, "entry_price": None, "winning_trades": [], "losing_trades": [], "num_wins": 0, "num_losses": 0, "buy_and_hold_return": 0},
    "ADAUSDT": {"candles": [], "candles_up": [], "candles_down": [], "trade_placed": False, "type_of_trade": None, "up": "ADAUPUSDT", "down": "ADADOWNUSDT", "size": 0, "time_in_trade": 0, "entry_price": None, "winning_trades": [], "losing_trades": [], "num_wins": 0, "num_losses": 0, "buy_and_hold_return": 0}
}

API_KEY = "YOUR API KEY"
SECRET_KEY = "YOUR SECRET KEY"

candles = []
opens = []
highs = []
lows = []
closes = []

capital = [100]

buy_orders = {}
exit_orders = {}
for ticker in assets:
    buy_orders[assets[ticker]["up"]] = []
    buy_orders[assets[ticker]["down"]] = []
    exit_orders[assets[ticker]["up"]] = []
    exit_orders[assets[ticker]["down"]] = []

years = 15/365
num_assets = len (assets)
active_trades = 0
num_trades = 0

total_wins = 0
total_losses = 0
win_returns = []
loss_returns = []

slippage = 0.0004
transaction_fee = 0.001
spread = 0.004

buy_and_hold_returns = []

print ("Loading API client...")
client = Client (API_KEY, SECRET_KEY)
print ("\nDone!")

for ticker in assets:
    print ("\nGetting historical OHLC data for "+ticker+"...")
    klines = client.get_historical_klines (ticker, Client.KLINE_INTERVAL_3MINUTE, "15 Dec, 2020", "1 Jan, 2021")
    klines_up = client.get_historical_klines (assets[ticker]["up"], Client.KLINE_INTERVAL_3MINUTE, "15 Dec, 2020", "1 Jan, 2021")
    klines_down = client.get_historical_klines (assets[ticker]["down"], Client.KLINE_INTERVAL_3MINUTE, "15 Dec, 2020", "1 Jan, 2021")

    for i in range (len (klines)):
        assets[ticker]["candles"].append ([float (klines[i][1]), float (klines[i][2]), float (klines[i][3]), float (klines[i][4]), float (klines[i][0])])

    buy_and_hold_return = (assets[ticker]["candles"][-1][0] / assets[ticker]["candles"][0][0] - 1) * 100
    assets[ticker]["buy_and_hold_return"] = buy_and_hold_return
    buy_and_hold_returns.append ((assets[ticker]["candles"][-1][0] / assets[ticker]["candles"][0][0] - 1) * 100)

    for i in range (len (klines_up)):
        assets[ticker]["candles_up"].append ([float (klines_up[i][1]), float (klines_up[i][2]), float (klines_up[i][3]), float (klines_up[i][4]), float (klines_up[i][0])])

    for i in range (len (klines_down)):
        assets[ticker]["candles_down"].append ([float (klines_down[i][1]), float (klines_down[i][2]), float (klines_down[i][3]), float (klines_down[i][4]), float (klines_down[i][0])])

    print ("\nDone!\n")

for i in range (len (assets["XLMUSDT"]["candles"])):
    for ticker in assets:
        if i >= 40:
            candles = assets[ticker]["candles"]
            candles_up = assets[ticker]["candles_up"]
            candles_down = assets[ticker]["candles_down"]

            opens = []
            closes = []

            opens_up = []
            closes_up = []

            opens_down = []
            closes_down = []

            for n in range (len (candles)):
                opens.append (candles[n][0])
                closes.append (candles[n][3])

                opens_up.append (candles_up[n][0])
                closes_up.append (candles_up[n][3])

                opens_down.append (candles_down[n][0])
                closes_down.append (candles_down[n][3])

            curr_open = opens[i]
            curr_close = closes[i]

            curr_up_open = opens_up[i]
            curr_up_close = closes_up[i]

            curr_down_open = opens_down[i]
            curr_down_close = closes_down[i]

            ema = ti.ema (np.array (opens[:i]), 40)[-1]

            trade_placed = assets[ticker]["trade_placed"]
            time_in_trade = assets[ticker]["time_in_trade"]
            type_of_trade = assets[ticker]["type_of_trade"]
            entry_price = assets[ticker]["entry_price"]
            winning_trades = assets[ticker]["winning_trades"]
            losing_trades = assets[ticker]["losing_trades"]
            num_wins = assets[ticker]["num_wins"]
            num_losses = assets[ticker]["num_losses"]
            size = assets[ticker]["size"]

            if trade_placed == False:
                if curr_close > curr_open and curr_up_close < curr_up_open and (curr_up_open / curr_up_close - 1) > (spread +  2 * slippage + 2 * transaction_fee) and curr_close >= ema:
                    size = math.floor ((capital[-1] / num_assets * 100000000) / 100000000.0)
                    entry_price = ((curr_up_close * (1 + spread)) * (1 + slippage)) * (1 + transaction_fee)

                    trade_placed = True
                    type_of_trade = "UP"

                    buy_orders[assets[ticker]["up"]].append (i)
                    #signals[ticker].append ([slope / curr_price, stdev / curr_price, curr_price / moving_average])
                    num_trades += 1
                    time_in_trade = 1

                    print ("UP ORDER", ticker)

                elif curr_close < curr_open and curr_down_close < curr_down_open and (curr_down_open / curr_down_close - 1) > (0.01 + (spread +  2 * slippage + 2 * transaction_fee)) and curr_close <= ema:
                    size = math.floor ((capital[-1] / num_assets * 100000000) / 100000000.0)
                    entry_price = ((curr_down_close * (1 + spread)) * (1 + slippage)) * (1 + transaction_fee)

                    trade_placed = True
                    type_of_trade = "DOWN"

                    buy_orders[assets[ticker]["down"]].append (i)
                    #signals[ticker].append ([slope / curr_price, stdev / curr_price, curr_price / moving_average])
                    num_trades += 1
                    time_in_trade = 1

                    print ("DOWN ORDER", ticker)

            elif time_in_trade >= 4:
                if type_of_trade == "UP":
                    print ("EXIT TRADE", ticker)

                    exit_price = (curr_up_close * (1 - slippage)) * (1 - transaction_fee)
                    trade_placed = False

                    active_trades -= 1

                    exit_orders[assets[ticker]["up"]].append(i)

                    change = (((exit_price / entry_price) - 1)) + 1
                    capital[-1] = ((capital[-1] - size) + (change * size))

                    trade_return = (change - 1) * 100

                    if exit_price > entry_price:
                        print ("WIN", ticker, "Long",entry_price,"->",exit_price)
                        winning_trades.append (trade_return)
                        win_returns.append (trade_return)
                        total_wins += 1
                        num_wins += 1

                    else:
                        print ("LOSS", ticker, "Long",entry_price,"->",exit_price)
                        losing_trades.append (trade_return)
                        loss_returns.append (trade_return)
                        total_losses += 1
                        num_losses += 1

                elif type_of_trade == "DOWN":
                    print ("EXIT TRADE", ticker)

                    exit_price = (curr_down_close * (1 - slippage)) * (1 - transaction_fee)
                    trade_placed = False

                    active_trades -= 1

                    exit_orders[assets[ticker]["down"]].append(i)

                    change = (((exit_price / entry_price) - 1)) + 1
                    capital[-1] = ((capital[-1] - size) + (change * size))

                    trade_return = (change - 1) * 100

                    if exit_price > entry_price:
                        print ("WIN", ticker, "Long",entry_price,"->",exit_price)
                        winning_trades.append (trade_return)
                        win_returns.append (trade_return)
                        total_wins += 1
                        num_wins += 1

                    else:
                        print ("LOSS", ticker, "Long",entry_price,"->",exit_price)
                        losing_trades.append (trade_return)
                        loss_returns.append (trade_return)
                        total_losses += 1
                        num_losses += 1

            else:
                time_in_trade += 1

            assets[ticker]["trade_placed"] = trade_placed
            assets[ticker]["type_of_trade"] = type_of_trade
            assets[ticker]["time_in_trade"] = time_in_trade
            assets[ticker]["entry_price"] = entry_price
            assets[ticker]["winning_trades"] = winning_trades
            assets[ticker]["losing_trades"] = losing_trades
            assets[ticker]["num_wins"] = num_wins
            assets[ticker]["num_losses"] = num_losses
            assets[ticker]["size"] = size

    capital.append (capital[-1])

returns = []
drawdown_periods = [0]
in_drawdown = False
local_maximum = 0
for n in range (len (capital)):
    if n > 0:
        returns.append (capital[n] / capital[n - 1] - 1)
        curr_value = capital[n]
        prev_value = capital[n - 1]
        if in_drawdown == True:
            if curr_value > local_maximum:
                in_drawdown = False
            else:
                drawdown_periods[-1] += 1

        elif curr_value < prev_value:
            in_drawdown = True
            local_maximum = prev_value
            drawdown_periods.append (1)

max_drawdown = max (drawdown_periods) / len (capital)
sharpe = math.sqrt (175200) * statistics.mean (returns) / statistics.stdev (returns)
period_return = (capital[-1] / capital[0] - 1) * 100
annualized_return = (((capital[-1] / capital[0]) ** (1 / years)) - 1) * 100

print ("\nBacktest Data")

print ("\nGeneral Statistics")
print ("\tPeriod Return: " + str ("%.2f" % period_return) + "%")
print ("\tBuy and Hold Return: " + str ("%.2f" % statistics.mean (buy_and_hold_returns)) + "%")
print ("\tSharpe Ratio:", sharpe)
print ("\tMax Drawdown:", max_drawdown, "days")
print ("\tWin Rate: " + str ("%.2f" % (100 * total_wins / (total_wins + total_losses))) + "%")
print ("\tW/L Ratio:", abs (statistics.mean (win_returns) / statistics.mean (loss_returns)))
print ("\tNumber of Trades:", num_trades)
print ("\tAverage Annualized Return: "+str ("%.2f" % annualized_return)+"%")
print ("\nReturns of a $"+str(capital[0])+" Investment in Algorithm Over",years,"Years")
print ("\tAlgorithm: $"+str ("%.2f" % capital[-1]))

print ("\nPair Statistics")

for ticker in assets:
    winning_trades = assets[ticker]["winning_trades"]
    losing_trades = assets[ticker]["losing_trades"]
    num_wins = assets[ticker]["num_wins"]
    num_losses = assets[ticker]["num_losses"]
    buy_and_hold_return = assets[ticker]["buy_and_hold_return"]

    opens = []
    candles = assets[ticker]["candles"]
    for candle in candles:
        opens.append (candle[0])

    up_opens = []
    candles = assets[ticker]["candles_up"]
    for candle in candles:
        up_opens.append (candle[0])

    down_opens = []
    candles = assets[ticker]["candles_down"]
    for candle in candles:
        down_opens.append (candle[0])

    try:
        win_rate = (num_wins / (num_wins + num_losses)) * 100

        print ("\n"+ticker)
        print ("\tWinning Trades:", num_wins)
        print ("\tLosing Trades:", num_losses)
        print ("\tWin Rate: "+str ("%.2f" % win_rate)+"%")
        print ("\tAverage Winning Trade Return: "+str ("%.2f" % statistics.mean (winning_trades))+"%")
        print ("\tAverage Losing Trade Loss: "+str ("%.2f" % statistics.mean (losing_trades))+"%")
        print ("\tUnderlying Asset Return: " + str ("%.2f" % buy_and_hold_return) + "%")
        print ("\tLargest Win: "+str ("%.2f" % max (winning_trades))+"%")
        print ("\tLargest Loss: "+str ("%.2f" % min (losing_trades))+"%")
        print ("\tAverage Win/Loss Ratio: "+str ("%.2f" % abs (statistics.mean (winning_trades) / statistics.mean (losing_trades)))+":1")

    except:
        pass

    #plt.plot (np.array (opens))
    plt.plot (np.array (up_opens))
    plt.plot (np.array (down_opens))

    for order in buy_orders[assets[ticker]["up"]]:
        plt.scatter (order, np.array (up_opens [order]), color="green")

    for order in exit_orders[assets[ticker]["up"]]:
        plt.scatter (order, np.array (up_opens [order]), color="black")

    for order in buy_orders[assets[ticker]["down"]]:
        plt.scatter (order, np.array (down_opens [order]), color="green")

    for order in exit_orders[assets[ticker]["down"]]:
        plt.scatter (order, np.array (down_opens [order]), color="black")

    plt.show ()

plt.figure ("Returns of Algorithm")
plt.title ("Performance of a $"+str(capital[0])+" Investment in the Algorithm")
plt.xlabel ("Trading Periods")
plt.ylabel ("Performance (%)")

for ticker in assets:
    opens = []
    candles = assets[ticker]["candles"]
    for candle in candles:
        opens.append (candle[0])

    plt.plot (100 * (np.array (opens) / opens[0] - 1), label=ticker)

plt.plot (100 * (np.array (capital) / capital[0] - 1), label="Capital")
plt.show()
