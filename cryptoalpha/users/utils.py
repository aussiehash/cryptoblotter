import os
import json
import re
import secrets
import logging
import requests
import configparser
import hashlib
import pickle
import pandas as pd
import numpy as np
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flask_login import current_user
from cryptoalpha import db, mail
from cryptoalpha.config import Config
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

# ---------------------------------------------------------
# Helper Functions start here
# ---------------------------------------------------------

# --------------------------------------------
# Read Global Variables from config(s)
# Include global variables and error handling
# --------------------------------------------
ALPHAVANTAGE_API_KEY = Config.ALPHAVANTAGE_API_KEY
If not ALPHAVANTAGE_API_KEY:
    logging.error("WARNING! ALPHAVANTAGE_API_KEY not found. Please include "+
        "at environment variables: "+
        "$EXPORT ALPHAVANTAGE_API_KEY="<Your Key Here>")
config = configparser.ConfigParser()
config.read('config.ini')

try:
    RENEW_NAV = config['MAIN']['RENEW_NAV']
except KeyError:
    RENEW_NAV = 60
    logging.error("Could not find RENEW_NAV at config.ini. Defaulting to 60.")
try:
    PORTFOLIO_MIN_SIZE_NAV = config['MAIN']['PORTFOLIO_MIN_SIZE_NAV']
except KeyError:
    PORTFOLIO_MIN_SIZE_NAV = 5
    logging.error("Could not find PORTFOLIO_MIN_SIZE_NAV at config.ini." +
                  " Defaulting to 5.")


def multiple_price_grab(tickers, fx):
    # tickers should be in comma sep string format like "BTC,ETH,LTC"
    baseURL = \
        "https://min-api.cryptocompare.com/data/pricemultifull?fsyms="\
        + tickers+"&tsyms="+fx+",BTC"
    try:
        request = requests.get(baseURL)
    except requests.exceptions.ConnectionError:
        return ("ConnectionError")

    data = request.json()
    return (data)


def rt_price_grab(ticker):
    baseURL =\
        "https://min-api.cryptocompare.com/data/price?fsym="+ticker +\
        "&tsyms=USD,BTC"
    request = requests.get(baseURL)
    data = request.json()
    return (data)


def cost_calculation(user, ticker):
    # This function calculates the cost basis assuming 3 different methods
    # FIFO, LIFO and avg. cost
    if ticker == 'USD':
        return (0)

    df = pd.read_sql_table('trades', db.engine)
    df = df[(df.user_id == user)]
    df = df[(df.trade_asset_ticker == ticker)]
    # Find current open position on asset
    summary_table = df.groupby(['trade_asset_ticker', 'trade_operation'])[
        ["cash_value", "trade_fees", "trade_quantity"]].sum()
    open_position = summary_table.sum()['trade_quantity']

    # Drop Deposits and Withdraws - keep only Buy and Sells
    if open_position > 0:
        df = df[df.trade_operation.str.match('B')]
    elif open_position < 0:
        df = df[df.trade_operation.str.match('S')]

    # Let's return a dictionary for this user with FIFO, LIFO and Avg. Cost
    cost_matrix = {}

    # ---------------------------------------------------
    # FIFO
    # ---------------------------------------------------

    fifo_df = df.sort_values(by=['trade_date'], ascending=True)

    fifo_df['acum_Q'] = fifo_df['trade_quantity'].cumsum()
    fifo_df['acum_Q'] = np.where(fifo_df['acum_Q'] < open_position,
                                 fifo_df['acum_Q'], open_position)
    # Keep only the number of rows needed for open position
    fifo_df = fifo_df.drop_duplicates(subset="acum_Q", keep='first')
    fifo_df['Q'] = fifo_df['acum_Q'].diff()
    if fifo_df['acum_Q'].count() == 1:
        fifo_df['Q'] = fifo_df['acum_Q']
    # Adjust Cash Value only to account for needed position
    fifo_df['adjusted_cv'] = fifo_df['cash_value'] * fifo_df['Q'] /\
        fifo_df['trade_quantity']

    cost_matrix['FIFO'] = {}
    cost_matrix['FIFO']['cash'] = fifo_df['adjusted_cv'].sum()

    cost_matrix['FIFO']['quantity'] = open_position
    cost_matrix['FIFO']['count'] = fifo_df['trade_operation'].count()
    cost_matrix['FIFO']['average_cost'] = fifo_df['adjusted_cv'].sum()\
        / open_position
    print("FIFO")
    print(fifo_df)

    # ---------------------------------------------------
    #  LIFO
    # ---------------------------------------------------

    lifo_df = df.sort_values(by=['trade_date'], ascending=False)

    lifo_df['acum_Q'] = lifo_df['trade_quantity'].cumsum()
    lifo_df['acum_Q'] = np.where(lifo_df['acum_Q'] < open_position,
                                 lifo_df['acum_Q'], open_position)
    # Keep only the number of rows needed for open position
    lifo_df = lifo_df.drop_duplicates(subset="acum_Q", keep='first')
    lifo_df['Q'] = lifo_df['acum_Q'].diff()
    if lifo_df['acum_Q'].count() == 1:
        lifo_df['Q'] = lifo_df['acum_Q']
    # Adjust Cash Value only to account for needed position
    lifo_df['adjusted_cv'] = lifo_df['cash_value'] * lifo_df['Q'] /\
        lifo_df['trade_quantity']

    cost_matrix['LIFO'] = {}
    cost_matrix['LIFO']['cash'] = lifo_df['adjusted_cv'].sum()

    cost_matrix['LIFO']['quantity'] = open_position
    cost_matrix['LIFO']['count'] = lifo_df['trade_operation'].count()
    cost_matrix['LIFO']['average_cost'] = lifo_df['adjusted_cv'].sum()\
        / open_position

    print("LIFO")
    print(lifo_df)

    print("Cost Matrix")
    print(cost_matrix)

    return (cost_matrix)


def generate_pos_table(user, fx, hidesmall):
    # New version to generate the front page position summary

    df = pd.read_sql_table('trades', db.engine)
    df = df[(df.user_id == user)]
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    list_of_tickers = df.trade_asset_ticker.unique().tolist()

    # Create string of tickers and grab all prices in one request
    ticker_str = ""
    for ticker in list_of_tickers:
        ticker_str = ticker_str + "," + ticker
    price_list = multiple_price_grab(ticker_str, fx)
    if price_list == "ConnectionError":
        return ("ConnectionError", "ConnectionError")

    summary_table = df.groupby(['trade_asset_ticker', 'trade_operation'])[
        ["cash_value", "trade_fees", "trade_quantity"]].sum()

    summary_table['count'] = df.groupby([
        'trade_asset_ticker', 'trade_operation'])[
        "cash_value"].count()

    consol_table = df.groupby(['trade_asset_ticker'])[
        ["cash_value", "trade_fees", "trade_quantity"]].sum()

    consol_table['symbol'] = consol_table.index.values
    consol_table = consol_table.drop('USD')

    # Functions to filter and apply to the data

    def find_price_data(ticker):
        price_data = price_list["RAW"][ticker]['USD']
        return (price_data)

    def find_price_data_BTC(ticker):
        price_data = price_list["RAW"][ticker]['BTC']
        return (price_data)

    consol_table['price_data_USD'] = consol_table['symbol'].\
        apply(find_price_data)
    consol_table['price_data_BTC'] = consol_table['symbol'].\
        apply(find_price_data_BTC)

    consol_table['usd_price'] =\
        consol_table.price_data_USD.map(lambda v: v['PRICE'])
    consol_table['chg_pct_24h'] =\
        consol_table.price_data_USD.map(lambda v: v['CHANGEPCT24HOUR'])
    consol_table['btc_price'] =\
        consol_table.price_data_BTC.map(lambda v: v['PRICE'])

    consol_table['usd_position'] = consol_table['usd_price'] *\
        consol_table['trade_quantity']

    consol_table['chg_usd_24h'] =\
        consol_table['chg_pct_24h']/100*consol_table['usd_position']

    consol_table['btc_position'] = consol_table['btc_price'] *\
        consol_table['trade_quantity']
    consol_table['usd_perc'] = consol_table['usd_position']\
        / consol_table['usd_position'].sum()
    consol_table['btc_perc'] = consol_table['btc_position']\
        / consol_table['btc_position'].sum()
    consol_table.loc[consol_table.usd_perc <= 0.01, 'small_pos'] = 'True'
    consol_table.loc[consol_table.usd_perc >= 0.01, 'small_pos'] = 'False'

    # Should rename this to breakeven:
    consol_table['average_cost'] = consol_table['cash_value']\
        / consol_table['trade_quantity']

    consol_table['total_pnl_gross_USD'] = consol_table['usd_position'] -\
        consol_table['cash_value']
    consol_table['total_pnl_net_USD'] = consol_table['usd_position'] -\
        consol_table['cash_value'] - consol_table['trade_fees']

    summary_table['symbol_operation'] = summary_table.index.values
    # This is wrong:
    summary_table['average_price'] = summary_table['cash_value'] /\
        summary_table['trade_quantity']

    # create a dictionary in a better format to deliver to html table
    table = {}
    table['TOTAL'] = {}
    table['TOTAL']['cash_flow_value'] = summary_table.sum()['cash_value']
    table['TOTAL']['trade_fees'] = summary_table.sum()['trade_fees']
    table['TOTAL']['trade_count'] = summary_table.sum()['count']
    table['TOTAL']['usd_position'] = consol_table.sum()['usd_position']
    table['TOTAL']['btc_position'] = consol_table.sum()['btc_position']
    table['TOTAL']['chg_usd_24h'] = consol_table.sum()['chg_usd_24h']
    table['TOTAL']['chg_perc_24h'] = ((table['TOTAL']['chg_usd_24h']
                                       / table['TOTAL']['usd_position']))*100
    table['TOTAL']['total_pnl_gross_USD'] =\
        consol_table.sum()['total_pnl_gross_USD']
    table['TOTAL']['total_pnl_net_USD'] =\
        consol_table.sum()['total_pnl_net_USD']
    table['TOTAL']['refresh_time'] = datetime.now()
    pie_data = []

    # Drop small positions if hidesmall (small position = <0.01%)
    if hidesmall:
        consol_table = consol_table[consol_table.small_pos == 'False']
        list_of_tickers = consol_table.index.unique().tolist()

    for ticker in list_of_tickers:
        if ticker == 'USD':
            continue
        table[ticker] = {}
        table[ticker]['breakeven'] = 0
        if consol_table['small_pos'][ticker] == 'False':
            tmp_dict = {}
            tmp_dict['y'] = consol_table['usd_perc'][ticker]*100
            tmp_dict['name'] = ticker
            pie_data.append(tmp_dict)
            table[ticker]['breakeven'] = \
                consol_table['price_data_USD'][ticker]['PRICE'] -\
                (consol_table['total_pnl_net_USD'][ticker] /
                 consol_table['trade_quantity'][ticker])

        table[ticker]['cost_matrix'] = cost_calculation(user, ticker)
        table[ticker]['cost_matrix']['LIFO']['unrealized_pnl'] = \
            (consol_table['usd_price'][ticker] -
             table[ticker]['cost_matrix']['LIFO']['average_cost']) * \
            consol_table['trade_quantity'][ticker]
        table[ticker]['cost_matrix']['FIFO']['unrealized_pnl'] = \
            (consol_table['usd_price'][ticker] -
             table[ticker]['cost_matrix']['FIFO']['average_cost']) * \
            consol_table['trade_quantity'][ticker]

        table[ticker]['cost_matrix']['LIFO']['realized_pnl'] = \
            consol_table['total_pnl_net_USD'][ticker] -\
            table[ticker]['cost_matrix']['LIFO']['unrealized_pnl']
        table[ticker]['cost_matrix']['FIFO']['realized_pnl'] = \
            consol_table['total_pnl_net_USD'][ticker] -\
            table[ticker]['cost_matrix']['FIFO']['unrealized_pnl']

        table[ticker]['cost_matrix']['LIFO']['unrealized_be'] =\
            consol_table['price_data_USD'][ticker]['PRICE'] -\
            (table[ticker]['cost_matrix']['LIFO']['unrealized_pnl'] /
             consol_table['trade_quantity'][ticker])
        table[ticker]['cost_matrix']['FIFO']['unrealized_be'] =\
            consol_table['price_data_USD'][ticker]['PRICE'] -\
            (table[ticker]['cost_matrix']['FIFO']['unrealized_pnl'] /
             consol_table['trade_quantity'][ticker])

        table[ticker]['position'] = consol_table['trade_quantity'][ticker]
        table[ticker]['usd_position'] = consol_table['usd_position'][ticker]
        table[ticker]['chg_pct_24h'] = consol_table['chg_pct_24h'][ticker]
        table[ticker]['chg_usd_24h'] = consol_table['chg_usd_24h'][ticker]
        table[ticker]['usd_perc'] = consol_table['usd_perc'][ticker]
        table[ticker]['btc_perc'] = consol_table['btc_perc'][ticker]
        table[ticker]['total_fees'] = consol_table['trade_fees'][ticker]

        table[ticker]['usd_price_data'] =\
            consol_table['price_data_USD'][ticker]
        table[ticker]['usd_price_data']['LASTUPDATE'] =\
            (datetime.utcfromtimestamp(
                table[ticker]['usd_price_data']['LASTUPDATE']).strftime
                ('%H:%M:%S'))

        table[ticker]['btc_price'] = consol_table['price_data_BTC'][ticker]
        table[ticker]['total_pnl_gross_USD'] =\
            consol_table['total_pnl_gross_USD'][ticker]
        table[ticker]['total_pnl_net_USD'] =\
            consol_table['total_pnl_net_USD'][ticker]
        table[ticker]['small_pos'] = consol_table['small_pos'][ticker]
        table[ticker]['cash_flow_value'] =\
            summary_table['cash_value'][ticker].to_dict()
        table[ticker]['trade_fees'] = \
            summary_table['trade_fees'][ticker].to_dict()
        table[ticker]['trade_quantity'] = \
            summary_table['trade_quantity'][ticker].to_dict()
        table[ticker]['count'] = summary_table['count'][ticker].to_dict()
        table[ticker]['average_price'] = \
            summary_table['average_price'][ticker].to_dict()

    return(table, pie_data)


def cleancsv(text):  # Function to clean CSV fields - leave only digits and .
    if text is None:
        return (0)
    acceptable = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
    str = ""
    for char in text:
        if char in acceptable:
            str = str + char
    str = float(str)
    return(str)


def generatepnltable(user, ticker, method, start_date=0, end_date=99999):
    # MARK FOR DELETION OR RESTRUCTURE
    # start by reading a pandas dataframe from the dbase
    # methods can be FIFO, LIFO or AVERAGE
    # defaults to AVERAGE
    df = pd.read_sql_table('trades', db.engine)
    df = df[(df.user_id == user)]
    df = df[(df.trade_asset_ticker == ticker)]
    # Filter only buy and sells, ignore deposit / withdraw
    df = df[(df.trade_operation == "B") | (df.trade_operation == "S")]
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    tmpdf = df.copy()

    # Since tmpdf is a copy of df, Pandas may generate warnings
    # when changing tmpdf but not df. Weird but more info here:
    # https://goo.gl/FLguwy
    pd.options.mode.chained_assignment = None  # default='warn'

    tmpdf.set_index('trade_date', inplace=True)
    if method == "FIFO":
        tmpdf.sort_index(inplace=True)
    if method == "LIFO":
        tmpdf.sort_index(inplace=True, ascending=False)

    currentpos = 0
    realpnl = {}
    metadata = {}

    # Interact through all transactions looking for changes in sign
    for index, row in df.iterrows():

        if currentpos == 0:
            currentpos = currentpos + float(row['trade_quantity'])
            continue

        # Look for a change in direction (reducing position)
        direction = row['trade_quantity'] / abs(row['trade_quantity'])
        possign = currentpos / abs(currentpos)

        quantity = abs(float(row['trade_quantity']))

        currentpos = currentpos + float(row['trade_quantity'])

        # This means we are only adding to the position, do nothing
        if direction == possign:
            continue

        realpnl[row['trade_reference_id']] = []
        # create an empty dic for metadata on this unwind

        metadata[row['trade_reference_id']] = {}
        metadata[row['trade_reference_id']]['method'] = method
        metadata[row['trade_reference_id']]['start_date'] = start_date
        metadata[row['trade_reference_id']]['end_date'] = end_date
        unwinddate = row['trade_date']
        unwindvalue = abs(float(row['trade_quantity']) * float(row[
            'trade_price']))
        metadata[row['trade_reference_id']]['unwind_value'] = unwindvalue

        # Start looping through transactions to look for unwinds until
        # all quantities are done
        cumcf = 0
        while quantity != 0:
            rowquant = abs(float(tmpdf.iloc[0].trade_quantity))
            rowcf = abs(float(tmpdf.iloc[0].cash_value))

            # If looped through all trades and hit end of list
            # No more unwinds, adjust position
            if tmpdf.iloc[0].trade_reference_id == row['trade_reference_id']:
                # This means the loop completed and the current transaction is
                # larger than all previous transactions. For example:
                # B 10 , B 10, S 30
                tmpdf.drop(tmpdf.head(1).index, inplace=True)
                currentpos = quantity
                break

            # find match trades for this unwind
            # and store under a dic with trade_id of realized trade

            # if this transaction is not enough to match unwind
            # take the full row out
            if rowquant <= quantity:
                recordtrade = {}
                recordtrade["id"] = tmpdf.iloc[0].trade_reference_id
                recordtrade["holding_period"] = (unwinddate -
                                                 tmpdf.iloc[0].name).days
                quantity = quantity - rowquant
                recordtrade["cumquant"] = quantity
                realpnl[row['trade_reference_id']].append(recordtrade)
                cumcf = cumcf + rowcf
                tmpdf.drop(tmpdf.head(1).index, inplace=True)

            # This transaction has enough quantity - unwind partially only
            else:
                # Adjust the CF to reflect only partially
                cumcf = cumcf + (rowcf * quantity / rowquant)
                #  CHECK THIS:
                tmpdf.iloc[0].trade_quantity = quantity
                recordtrade = {}
                recordtrade["id"] = tmpdf.iloc[0].trade_reference_id
                recordtrade["holding_period"] = (unwinddate -
                                                 tmpdf.iloc[0].name).days
                quantity = 0
                recordtrade["cumquant"] = quantity
                realpnl[row['trade_reference_id']].append(recordtrade)
                tmpdf.iloc[0].trade_quantity = rowquant - quantity

        metadata[row['trade_reference_id']]['match_value'] = cumcf
        metadata[row['trade_reference_id']]['realpnl'] = unwindvalue - cumcf

    return (realpnl, metadata)


def generatenav(user, force=False):
    logging.info(f"[generatenav] Starting NAV Generator for user {user}")
    # Variables
    # Portfolios smaller than this size do not account for NAV calculations
    # Otherwise, there's an impact of dust left in the portfolio (in USD)
    # This is set in config.ini file
    min_size_for_calc = int(PORTFOLIO_MIN_SIZE_NAV)
    logging.info(f"[generatenav] Force update status is {force}")
    # This process can take some time and it's intensive to run NAV
    # generation every time the NAV is needed. A compromise is to save
    # the last NAV generation locally and only refresh after a period of time.
    # This period of time is setup in config.ini as RENEW_NAV (in minutes).
    # If last file is newer than 60 minutes (default), the local saved file
    # will be used.
    # Unless force is true, then a rebuild is done regardless
    # Local files are  saved under a hash of username.
    if force:
        logging.info("[generatenav] FORCE update is on. Not using local file")
        usernamehash = hashlib.sha256(current_user.username.encode(
            'utf-8')).hexdigest()
        filename = "cryptoalpha/nav_data/"+usernamehash + ".nav"
        logging.info(f"[generatenav] {filename} marked for deletion.")
        # Since this function can be run as a thread, it's safer to delete
        # the current NAV file if it exists. This avoids other tasks reading
        # the local file which is outdated
        try:
            os.remove(filename)
            logging.info("[generatenav] Local NAV file found and deleted")
        except OSError:
            logging.info("[generatenav] Local NAV file was not found" +
                         " for removal - continuing")

    if not force:
        usernamehash = hashlib.sha256(current_user.username.encode(
            'utf-8')).hexdigest()
        filename = "cryptoalpha/nav_data/"+usernamehash + ".nav"
        try:
            # Check if NAV saved file is recent enough to be used
            # Local file has to have a saved time less than RENEW_NAV min old
            # See config.ini to change RENEW_NAV
            modified = datetime.utcfromtimestamp(os.path.getmtime(filename))
            elapsed_seconds = (datetime.utcnow() - modified).total_seconds()
            logging.info(f"Last time file was modified {modified} is " +
                         f" {elapsed_seconds} seconds ago")
            if (elapsed_seconds/60) < int(RENEW_NAV):
                nav_pickle = pd.read_pickle(filename)
                logging.info(f"Success: Open {filename} - no need to rebuild")
                print("Loaded NAV from pickle")
                print(nav_pickle)
                return (nav_pickle)
            else:
                logging.info("File found but too old - rebuilding NAV")

        except FileNotFoundError:
            logging.warn(f"[generatenav] File not found to load NAV" +
                         " - rebuilding")

    # Panda dataframe with transactions
    df = pd.read_sql_table('trades', db.engine)
    df = df[(df.user_id == user)]
    logging.info("[generatenav] Success - read trades from database")
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    start_date = df['trade_date'].min()
    start_date -= timedelta(days=1)  # start on t-1 of first trade
    df = df.set_index('trade_date')
    end_date = datetime.today()

    # Create a list of all tickers that were traded in this portfolio
    tickers = df.trade_asset_ticker.unique()

    # Create a DF, fill with dates and fill with operation and prices then NAV
    dailynav = pd.DataFrame(columns=['date'])
    # Fill the dates from first trade until today
    dailynav['date'] = pd.date_range(start=start_date, end=end_date)
    dailynav = dailynav.set_index('date')
    dailynav['PORT_usd_pos'] = 0
    dailynav['PORT_cash_value'] = 0

    # Create a dataframe for each position's prices:
    # prices = {}
    for id in tickers:
        if id == "USD":
            continue
        filename = 'cryptoalpha/historical_data/'+id+'.json'
        try:
            with open(filename) as data_file:
                local_json = json.loads(data_file.read())
                data_file.close()
                prices = pd.DataFrame(local_json[
                    'Time Series (Digital Currency Daily)']).T
                prices.reset_index(inplace=True)
                # Reassign index to the date column
                prices = prices.set_index(
                    list(prices.columns[[0]]))
                prices = prices['4a. close (USD)']
                # convert string date to datetime
                prices.index = pd.to_datetime(prices.index)
                # rename index to date to match dailynav name
                prices.index.rename('date', inplace=True)
                prices.rename(id+'_price', inplace=True)
                # Fill dailyNAV with prices for each ticker
                dailynav = pd.merge(dailynav, prices, on='date', how='left')
                # Update today's price with realtime data
                try:
                    dailynav[id+"_price"][-1] = rt_price_grab(id)['USD']
                except IndexError:
                    pass

                # Replace NaN with prev value, if no prev value then zero
                dailynav[id+'_price'].fillna(method='ffill', inplace=True)
                dailynav[id+'_price'].fillna(0, inplace=True)
                # Now let's find trades for this ticker and include in dailynav
                tradedf = df[['trade_asset_ticker',
                              'trade_quantity', 'cash_value']].copy()
                # Filter trades only for this ticker
                tradedf = tradedf[tradedf['trade_asset_ticker'] == id]
                # consolidate all trades in a single date Input
                tradedf = tradedf.groupby(level=0).sum()
                tradedf.sort_index(ascending=True, inplace=True)
                # include column to cumsum quant
                tradedf['cum_quant'] = tradedf['trade_quantity'].cumsum()
                # merge with dailynav - 1st rename columns to include ticker
                tradedf.index.rename('date', inplace=True)
                tradedf.rename(columns={'trade_quantity': id+'_quant',
                                        'cash_value': id+'_cash_value',
                                        'cum_quant': id+'_pos'},
                               inplace=True)

                # merge
                dailynav = pd.merge(dailynav, tradedf, on='date', how='left')
                # for empty days just trade quantity = 0, same for CV
                dailynav[id+'_quant'].fillna(0, inplace=True)
                dailynav[id+'_cash_value'].fillna(0, inplace=True)
                # Now, for positions, fill with previous values, NOT zero,
                # unless there's no previous
                dailynav[id+'_pos'].fillna(method='ffill', inplace=True)
                dailynav[id+'_pos'].fillna(0, inplace=True)
                # Calculate USD position
                dailynav[id+'_usd_pos'] = dailynav[id+'_price'].astype(
                    float) * dailynav[id+'_pos'].astype(float)

                # Before calculating NAV, clean the df for small
                # dust positions. Otherwise, a portfolio close to zero but with
                # 10 sats for example, would still have NAV changes
                dailynav[id+'_usd_pos'].round(2)
                logging.info(
                    f"Success: imported prices from file:{filename}")

        except (FileNotFoundError, KeyError):
            logging.error(f"File not Found Error: ID: {id}")

    # Another loop to sum the portfolio values - maybe there is a way to
    # include this on the loop above. But this is not a huge time drag unless
    # there are too many tickers in a portfolio

    for id in tickers:
        if id == "USD":
            continue
        # Include totals in new columns
        # This is raising an error if prices are not updated
        try:
            dailynav['PORT_usd_pos'] = dailynav['PORT_usd_pos'] +\
                dailynav[id+'_usd_pos']
        except KeyError:
            logging.warning(f"[GENERATENAV] Ticker {id} was not found " +
                            "on NAV Table - continuing but this is not good.")
            continue
        dailynav['PORT_cash_value'] = dailynav['PORT_cash_value'] +\
            dailynav[id+'_cash_value']

    # Now, finally, let's calculate NAV and return on period

    # Create a new column with the portfolio change only due to market move
    # discounting all cash flows for that day
    dailynav['adj_portfolio'] = dailynav['PORT_usd_pos'] -\
        dailynav['PORT_cash_value']
    # dailynav['adj_portfolio'] = dailynav['adj_portfolio'].clip(lower=0)
    # dailynav['adj_portfolio'] = dailynav['adj_portfolio'].round(0)
    # For the period return let's use the Modified Dietz Rate of return method
    # more info here: https://tinyurl.com/y474gy36
    # There is one caveat here. If end value is zero (i.e. portfolio fully
    # redeemed, the formula needs to be adjusted)
    dailynav.loc[dailynav.PORT_usd_pos > min_size_for_calc,
                 'port_dietz_ret'] =\
        ((dailynav['PORT_usd_pos'] -
          dailynav['PORT_usd_pos'].shift(1)) -
         dailynav['PORT_cash_value']) /\
        (dailynav['PORT_usd_pos'].shift(1) +
         abs(dailynav['PORT_cash_value']))

    # Fill empty and NaN with zero
    dailynav['port_dietz_ret'].fillna(0, inplace=True)

    dailynav['adj_port_chg_usd'] = (dailynav['PORT_usd_pos'] -
                                    dailynav['PORT_usd_pos'].shift(1)) -\
        dailynav['PORT_cash_value']
    # let's fill NaN with zeros
    dailynav['adj_port_chg_usd'].fillna(0, inplace=True)
    dailynav['port_perc_factor'] = (dailynav['port_dietz_ret']) + 1
    dailynav['NAV'] = dailynav['port_perc_factor'].cumprod()
    dailynav['NAV'] = dailynav['NAV'] * 100
    dailynav['PORT_ac_CFs'] = dailynav['PORT_cash_value'].cumsum()
    logging.info(
        f"[generatenav] Success: NAV Generated for user {user}")

    # Save NAV Locally as Pickle
    usernamehash = hashlib.sha256(current_user.username.encode(
        'utf-8')).hexdigest()
    filename = "cryptoalpha/nav_data/"+usernamehash + ".nav"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    dailynav.to_pickle(filename)
    logging.info(f"[generatenav] NAV saved to {filename}")

    print("Daily NAV")
    print(dailynav)
    return dailynav


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/images',
                                picture_fn)

    # Image is resized to save server space
    # This is done through a package called Pillow

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


def alphavantage_historical(id):
    # Downloads Historical prices from Alphavantage
    # Can handle both Stock and Crypto tickers - try stock first, then crypto
    # Returns:
    #  - data matrix (prices)
    #  - notification messages: error, stock, crypto
    #  - Metadata:
    #     "Meta Data": {
    #     "1. Information": "Daily Prices and Volumes for Digital Currency",
    #     "2. Digital Currency Code": "BTC",
    #     "3. Digital Currency Name": "Bitcoin",
    #     "4. Market Code": "USD",
    #     "5. Market Name": "United States Dollar",
    #     "6. Last Refreshed": "2019-06-02 (end of day)",
    #     "7. Time Zone": "UTC"
    # },
    # To limit the number of requests to ALPHAVANTAGE, if data is Downloaded
    # successfully, it will be saved locally to be reused during that day

    # Alphavantage Keys can be generated free at
    # https://www.alphavantage.co/support/#api-key

    try:
        ALPHAVANTAGE_API_KEY = config['API_KEYS']['ALPHAVANTAGE_API_KEY']
    except KeyError:
        ALPHAVANTAGE_API_KEY = ""
        logging.error("Cannot read config.ini for Alphavantage API Key")

    filename = "cryptoalpha/alphavantage_data/" + id + ".aap"
    meta_filename = "cryptoalpha/alphavantage_data/" + id + "_meta.aap"
    try:
        # Check if saved file is recent enough to be used
        # Local file has to have a modified time in today
        today = datetime.now().date()
        filetime = datetime.fromtimestamp(os.path.getctime(filename))

        if filetime.date() == today:
            logging.info("[ALPHAVANTAGE] Local file is fresh. Using it.")
            id_pickle = pd.read_pickle(filename)
            with open(meta_filename, 'rb') as handle:
                meta_pickle = pickle.load(handle)
            logging.info(f"Success: Open {filename} - no need to rebuild")
            return (id_pickle, "downloaded", meta_pickle)
        else:
            logging.info("[ALPHAVANTAGE] File found but too old" +
                         " - downloading a fresh one.")

    except FileNotFoundError:
        logging.info(f"[ALPHAVANTAGE] File not found for {id} - downloading")

    baseURL = "https://www.alphavantage.co/query?"
    func = "DIGITAL_CURRENCY_DAILY"
    market = "USD"
    globalURL = baseURL + "function=" + func + "&symbol=" + id +\
        "&market=" + market + "&apikey=" + ALPHAVANTAGE_API_KEY
    logging.info(f"[ALPHAVANTAGE] {id}: Downloading data")
    logging.info(f"[ALPHAVANTAGE] Fetching URL: {globalURL}")
    try:
        logging.info(f"[ALPHAVANTAGE] Requesting URL: {globalURL}")
        request = requests.get(globalURL, timeout=10)
    except requests.exceptions.ConnectionError:
        logging.error("[ALPHAVANTAGE] Connection ERROR " +
                      "while trying to download prices")
        return("Connection Error", 'error', 'empty')
    data = request.json()
    # Try first as a crypto request
    try:
        meta_data = (data['Meta Data'])
        logging.info(f"[ALPHAVANTAGE] Downloaded historical price for {id}")
        df = pd.DataFrame.from_dict(data[
            'Time Series (Digital Currency Daily)'],
            orient="index")
        # Save locally for reuse today
        filename = "cryptoalpha/alphavantage_data/" + id + ".aap"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_pickle(filename)
        meta_filename = "cryptoalpha/alphavantage_data/" + id + "_meta.aap"
        with open(meta_filename, 'wb') as handle:
            pickle.dump(meta_data, handle,
                        protocol=pickle.HIGHEST_PROTOCOL)
        logging.info(f"[ALPHAVANTAGE] {filename}: Filed saved locally")
        return (df, 'crypto', meta_data)
    except KeyError:
        logging.info(
            f"[ALPHAVANTAGE] Ticker {id} not found as Crypto. Trying Stock.")
        # Data not found - try as STOCK request
        func = "TIME_SERIES_DAILY_ADJUSTED"
        globalURL = baseURL + "function=" + func + "&symbol=" + id +\
            "&market=" + market + "&outputsize=full&apikey=" +\
            ALPHAVANTAGE_API_KEY
        try:
            request = requests.get(globalURL, timeout=10)
        except requests.exceptions.ConnectionError:
            logging.error("[ALPHAVANTAGE] Connection ERROR while" +
                          " trying to download prices")
            return("Connection Error", "error", "empty")
        data = request.json()
        try:
            meta_data = (data['Meta Data'])
            logging.info(
                f"[ALPHAVANTAGE] Downloaded historical price for stock {id}")
            df = pd.DataFrame.from_dict(
                data['Time Series (Daily)'],
                orient="index")
            # Save locally for reuse today
            filename = "cryptoalpha/alphavantage_data/" + id + ".aap"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            df.to_pickle(filename)
            meta_filename = "cryptoalpha/alphavantage_data/" + id + "_meta.aap"
            with open(meta_filename, 'wb') as handle:
                pickle.dump(meta_data, handle,
                            protocol=pickle.HIGHEST_PROTOCOL)
            logging.info(f"[ALPHAVANTAGE] {filename}: Filed saved locally")
            return (df, "stock", meta_data)

        except KeyError:
            logging.warning(
                f"[ALPHAVANTAGE] {id} not found as Stock or Crypto" +
                " - INVALID TICKER")
            return("Invalid Ticker", "error", "empty")


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='cryptoblotterrp@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
                {url_for('users.reset_token', token=token, _external=True)}


                If you did not make this request then simply ignore this email
                 and no changes will be made.
                '''
    mail.send(msg)


def daily_maint():
    # -------------------------------------------------
    # Daily task to import prices from Alphavantage
    # loops through all tickers in database and downloads
    # then creates a txt file with the last update date
    # This is done to reduce number of API calls and
    # to speed up historical data usage
    # -------------------------------------------------
    logging.info("Starting Maintenance Routine")
    # For info on how the below was setup refer to:
    # https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/
    from cryptoalpha import db, create_app
    app = create_app()
    app.app_context().push()
    # Daily Maintenance Job
    with app.app_context():
        print(db)
        df = pd.read_sql_table('trades', db.engine)
    # ------ end of context -----

    tickers = df.trade_asset_ticker.unique()
    loggin.info(f"[daily_maint] Read the tickers to download data: {tickers}")
    for id in tickers:
        if id == "USD":
            continue
        filename = 'cryptoalpha/historical_data/'+id+'.json'

        try:

            with open(filename) as data_file:
                local_json = json.loads(data_file.read())
                data_file.close()
                lstup = ((local_json['Meta Data']['6. Last Refreshed']))
                # leave only numerical values on the Meta Data
                lstup = re.sub('[^0-9]', '', lstup)
                lstup = datetime.strptime(lstup, '%Y%m%d')
                ytday = (datetime.today().date())
                ytday -= timedelta(days=1)
                if lstup.date() == ytday:
                    logging.info(f"Ticker: {id} ---- " +
                                 "No need to update - local file is fresh")
                    continue

        except FileNotFoundError:
            logging.info(f"No json found for ticker {id}." +
                         " Downloading a new one")

        except TypeError:
            logging.error("File found but with invalid data")

        except KeyError:
            logging.error("Invalid Metadata")

        logging.info("Grabbing data from Alphavantage.")
        baseURL = "https://www.alphavantage.co/query?"
        func = "DIGITAL_CURRENCY_DAILY"
        market = "USD"
        globalURL = baseURL + "function=" + func + "&symbol=" + id +\
            "&market=" + market + "&apikey=" + ALPHAVANTAGE_API_KEY
        logging.info(f" URL = {globalURL}")

        try:
            request = requests.get(globalURL, timeout=2)
            data = request.json()
        except:
            data = 0

        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

        logging.info(f"Done with {filename}")


def daily_maint_scheduler():
    # TIMERS for Maintenance Routine
    # daily_maint()  # Run at start and then wait xxx minutes to re-run
    try:
        daily_maint()
        logging.info("Daily Maintenance executed ok at launch")
    except ImportError:
        print("Daily Maintenance skipped but will run again soon")
    sched = BackgroundScheduler(daemon=False)
    # sched.remove_job('sched')
    sched.add_job(daily_maint, 'cron', hour='3,9,12')
    sched.start()
    logging.info("[daily_maint_scheduler] Scheduled the daily Maintenance")

daily_maint_scheduler()
