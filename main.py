import sys
from datetime import datetime
import config
import yfinance as yf
import alpaca_trade_api as tradeapi
import warnings
warnings.simplefilter("ignore")

"""
This script downloads the data for a Live account from Alpaca by using the credentials in config.py.
For each symbol it will download: price, avg entry price, qty.
It will add data related to dividends as shown in config.py and will calculate the difference in % between the value 
at purchase and the current value + the net dividends: current price + (dividend * 0.85).
Based on the increase/decrease, the symbols will be categorized in winners or losers.

Set the 3 variables below to True to:
- show winners/losers, dividend yield YTD and for the full year, the overall avg increase and value;
- write the most relevant info to a txt file;
- show additional info like industry, sector and the buying power.

"""

# Get all positions on Alpaca: avg entry price, dividends, current price, increase/decrease...
get_account_info = True
# Set this variable to True to write account info to file
write_info_to_file = False
# Set this variable to True to show industry/sector of each symbol and the account buying power
get_ticker_info = False

# Instantiate REST API Connection
api_live = tradeapi.REST(key_id=config.API_KEY_LIVE, secret_key=config.SECRET_KEY_LIVE,
                         base_url=config.URL_LIVE, api_version='v2')

# a list with a dict for each symbol
positions = api_live.list_positions()

# Calculate the current value for each symbol (current price * qty), add the dividends YTD and
# compare it with the avg buy price, the increase/decrease will be shown as a percentage (TOTAL INCREASE)
# Show also the dividend yield YTD and that at the end of the year
winners = []
avg_increase_winners = []
losers = []
avg_increase_losers = []
winners_and_losers = []
avg_increase_winners_losers = []
total_value_plus_net_div = 0

other_assets = []
total_current_value_other_assets = 0
total_value_at_purchase_other_assets = 0

# Account info
if get_account_info:
    for p in positions:
        if p.asset_class == "us_equity":
            # subtract the 15% withholding tax from the dividends
            dividend_ytd_net = config.dividend_ytd_dict[p.symbol] * 0.85
            dividend_full_year_net = config.dividend_full_year[p.symbol] * 0.85

            current_price_plus_div = round(float(p.current_price) + dividend_ytd_net, 3)
            value_at_purchase = float(p.avg_entry_price) * float(p.qty)
            current_value = float(p.current_price) * float(p.qty)
            current_value_plus_div = current_price_plus_div * float(p.qty)
            total_value_plus_net_div += current_value_plus_div

            if float(p.current_price) != 0:
                dividend_yield_ytd = (dividend_ytd_net / float(p.current_price)) * 100
                dividend_yield_full_year = (dividend_full_year_net / float(p.current_price)) * 100
            else:
                dividend_yield_ytd = 0
                dividend_yield_full_year = 0

            # current_value_and_div = current_value + config.dividend_ytd_dict[p.symbol]
            if value_at_purchase != 0:
                increase_perc = (current_value_plus_div - value_at_purchase) / value_at_purchase * 100
            else:
                increase_perc = None

            if increase_perc is not None:
                winners_and_losers.append(p.symbol)
                avg_increase_winners_losers.append(increase_perc)
                if increase_perc > 0:
                    winners.append(p.symbol)
                    avg_increase_winners.append(increase_perc)
                else:
                    losers.append(p.symbol)
                    avg_increase_losers.append(increase_perc)
            else:
                continue

            print(p.symbol)
            print("Current Price: " + p.current_price)
            print("Current Price + dividends: " + str(current_price_plus_div))
            print("Avg Entry Price: " + p.avg_entry_price)
            print("Shares: " + p.qty)
            print("Class: " + p.asset_class)
            print("Exchange: " + p.exchange)
            print("VALUE WHEN PURCHASED: " + str(round(value_at_purchase, 3)))
            print("CURRENT VALUE INCLUDING DIVIDENDS YTD: " + str(round(current_value_plus_div, 3)))
            print("CURRENT DIVIDEND YIELD: " + str(round(dividend_yield_ytd, 3)) + "%")
            print("DIVIDEND YIELD AT END OF THE YEAR: " + str(round(dividend_yield_full_year, 3)) + "%")
            if increase_perc is None:
                print("TOTAL INCREASE: " + "missing data")
            elif increase_perc >= 0:
                print("TOTAL INCREASE: +" + str(round(increase_perc, 3)) + "%")
            else:
                print("TOTAL INCREASE: " + str(round(increase_perc, 3)) + "%")
            print()
            print(" ---------- " * 3)
        else:
            # non us-assets like cryptos
            other_assets.append(p.symbol)
            current_value = round(float(p.current_price), 3) * float(p.qty)
            value_at_purchase = float(p.avg_entry_price) * float(p.qty)

            total_current_value_other_assets += current_value
            total_value_at_purchase_other_assets += value_at_purchase

    print("===== WINNERS =====")
    print(winners)
    print("Avg Increase Winners: " + str(round(sum(avg_increase_winners) / len(winners), 3)) + "\n")
    print("===== LOSERS =====")
    print(losers)
    print("Avg Decrease Losers: " + str(round(sum(avg_increase_losers) / len(losers), 3)) + "\n")
    print("===== OVERALL AVG INCREASE (PRICE + (DIVIDENDS - WITHHOLDING TAX 15%)) =====")
    print(str(round(sum(avg_increase_winners_losers) / len(winners_and_losers), 3)) + "%")
    print()
    print("Total Amount deposited: " + str(config.total_deposit))
    print("Total Value including net dividends: " + str(round(total_value_plus_net_div, 3)))
    print()
    print("Other assets: " + str(other_assets))
    print("Value at purchase: " + str(round(total_value_at_purchase_other_assets, 3)))
    print("Current value: " + str(round(total_current_value_other_assets, 3)))


# Write info to file
dateTime = str(datetime.now())
total_value_div_other_assets = str(round(total_value_plus_net_div, 3) + round(total_current_value_other_assets, 3))

if write_info_to_file:
    with open("accountHistory.txt", "a") as f:
        f.write("\n" + dateTime)
        f.write("\n")
        f.write("Overall increase (net of withholding tax 15%): " + str(round(sum(avg_increase_winners_losers) / len(winners_and_losers), 3)) + "%")
        f.write("\n")
        f.write("Total Amount deposited: " + str(config.total_deposit))
        f.write("\n")
        f.write("Total Value + dividends + other assets: " + total_value_div_other_assets)
        f.write("\n")
        f.write("#" * 20)
        f.write("\n")


# Show additional info for each symbol
position_list = []
for p in positions:
    position_list.append(p.symbol)

if get_ticker_info:
    for p in position_list:
        ticker = yf.Ticker(p)
        try:
            print(p, ticker.info['industry'], '|', ticker.info['sector'])
        except Exception as e:
            print(p + ' has no data')
            pass

    account = api_live.get_account()
    print('${} is available as buying power.'.format(account.buying_power))

# industry, sector, longBusinessSummary, longName

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('OK')
