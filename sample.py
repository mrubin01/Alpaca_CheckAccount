import sys
from datetime import datetime
import config
import pandas as pd
import yfinance as yf
import alpaca_trade_api as tradeapi
import warnings
warnings.simplefilter("ignore")
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

"""
This will calculate the increase/decrease for a ticker step-by-step.
The TOTAL INCREASE is calculated as the difference between the value of all shares at purchase
and the current value + the dividend received 

"""
# Instantiate REST API Connection
api_live = tradeapi.REST(key_id=config.API_KEY_LIVE, secret_key=config.SECRET_KEY_LIVE,
                         base_url=config.URL_LIVE, api_version='v2')

# a list with a dict for each symbol
positions = api_live.list_positions()

ticker_to_test = "ASG"

for p in positions:
    if p.symbol == ticker_to_test:
        currentPrice = p.current_price
        qty = p.qty
        dividend = config.dividend_ytd_dict[p.symbol]

        dividend_ytd_net = config.dividend_ytd_dict[p.symbol] * 0.85
        dividend_full_year_net = config.dividend_full_year_dict[p.symbol] * 0.85

        current_price_plus_div = round(float(p.current_price) + dividend_ytd_net, 3)
        value_at_purchase = float(p.avg_entry_price) * float(p.qty)
        current_value = float(p.current_price) * float(p.qty)

        current_value_plus_div = current_value + config.net_dividend_received_ytd_dict[p.symbol]

print(currentPrice)
print(qty)

# dividend and net dividend per share
print(dividend)
print(dividend_ytd_net)

# net dividend per share full year: this may or may not be the same as dividend_ytd_net
print(dividend_full_year_net)

# value of all the shares at purchase based on the avg price (no dividend included)
print(value_at_purchase)
# value of all the shares now based on the current price (no dividend included)
print(round(float(current_value), 3))

# currentPrice + dividend_full_year_net
print(current_price_plus_div)

# Use this formula, not (float(currentPrice) + float(dividend_ytd_net)) * int(qty) as the former
# comes directly from the file alpaca_dividend_history.xlsx
# float(p.current_price) * float(p.qty) + config.net_dividend_received_ytd_dict[p.symbol]
print(current_value_plus_div)

# The increase is ((current_value_plus_div - value_at_purchase) / value_at_purchase) * 100
delta = current_value_plus_div - value_at_purchase
increase = (delta / value_at_purchase) * 100

if increase >= 0:
    print("TOTAL INCREASE: +" + str(round(increase, 3)) + "%")
else:
    print("TOTAL INCREASE: " + str(round(increase, 3)) + "%")





