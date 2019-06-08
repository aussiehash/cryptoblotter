import secrets
import json
import logging
import math
import pandas as pd
import numpy as np
from flask import render_template, request, jsonify, Blueprint
from flask_login import current_user, login_required
from cryptoalpha import db
from cryptoalpha.models import Trades, listofcrypto
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cryptoalpha.users.utils import generatenav, alphavantage_historical

api = Blueprint('api', __name__)


@api.route("/cryptolist", methods=['GET', 'POST'])
# List of available tickers. Also takes argument {term} so this can be used
# in autocomplete forms
def cryptolist():
    getlist = listofcrypto.query.all()

    if request.method == 'GET':
        check = request.args.get('json')
        q = request.args.get('term')
        if check == "true":
            jsonlist = []
            for item in getlist:
                if (q.upper() in item.symbol) or (q in item.name):
                    tmp = {}
                    tmp["name"] = item.name
                    tmp["symbol"] = item.symbol
                    jsonlist.append(tmp)

            return (jsonify(jsonlist))

    return (render_template('cryptolist.html',
                            title="List of Crypto Currencies",
                            listofcrypto=getlist))


@api.route("/aclst", methods=['GET', 'POST'])
@login_required
# Returns JSON for autocomplete on account names.
# Takes on input ?term - which is the string to be found
def aclst():
    list = []
    if request.method == 'GET':
        tradeaccounts = Trades.query.filter_by(
            user_id=current_user.username).group_by(
            Trades.trade_account)
        q = request.args.get('term')
        for item in tradeaccounts:
            if q.upper() in item.trade_account.upper():
                list.append(item.trade_account)

        list = json.dumps(list)

        return list


@api.route("/histvol", methods=['GET', 'POST'])
@login_required
# Returns a json with data to create the vol chart
# takes inputs from get:
# ticker, meta (true returns only metadata), rolling (in days)
# metadata (max, mean, etc)
def histvol():
    # if there's rolling variable, get it, otherwise default to 30
    if request.method == 'GET':
        try:
            q = int(request.args.get('rolling'))
        except ValueError:
            q = 30
    else:
        q = 30

    ticker = request.args.get('ticker')
    metadata = request.args.get('meta')

    # When ticker is not sent, will calculate for portfolio
    if not ticker:
        transactions = Trades.query.filter_by(
            user_id=current_user.username).order_by(
            Trades.trade_date)
        if transactions.count() == 0:
            return render_template('empty.html')

        data = generatenav(current_user.username)
        data['vol'] = data['NAV'].pct_change().rolling(q).std()*(365**0.5)*100
        # data.set_index('date', inplace=True)
        vollist = data[['vol']].copy()
        vollist.index = vollist.index.strftime('%Y-%m-%d')
        datajson = vollist.to_json()

    if ticker:
        filename = 'cryptoalpha/historical_data/'+ticker+'.json'

        try:
            with open(filename) as data_file:
                local_json = json.loads(data_file.read())
                data_file.close()
                prices = pd.DataFrame(local_json[
                    'Time Series (Digital Currency Daily)']).T
                prices['4b. close (USD)'] = prices[
                    '4b. close (USD)'].astype(np.float)
                prices['vol'] = prices[
                    '4b. close (USD)'].pct_change().rolling(q).std()*(
                        365**0.5)*100
                pricelist = prices[['vol']].copy()
                datajson = pricelist.to_json()

        except (FileNotFoundError, KeyError):
            datajson = "Ticker Not Found"
            logging.error(f"File not Found Error: ID: {id}")

    if metadata is not None:
        metatable = {}
        metatable['mean'] = vollist.vol.mean()
        metatable['max'] = vollist.vol.max()
        metatable['min'] = vollist.vol.min()
        metatable['last'] = vollist.vol[-1]
        metatable['lastvsmean'] = ((
            vollist.vol[-1] / vollist.vol.mean()) - 1) * 100
        metatable = json.dumps(metatable)
        return (metatable)

    return datajson


@api.route("/tradedetails", methods=['GET'])
@login_required
# Function that returns a json with trade details given an id
# also, set tradesonly to true to only receive the
# asset side of transaction (buy or sell)
# id = trade hash
def tradedetails():
    if request.method == 'GET':
        id = request.args.get('id')
        # if tradesonly is true then only look for buy and sells
        tradesonly = request.args.get('trades')
        df = pd.read_sql_table('trades', db.engine)
        # Filter only the trades for current user
        df = df[(df.user_id == current_user.username)]
        df = df[(df.trade_reference_id == id)]
        # Filter only buy and sells, ignore deposit / withdraw
        if tradesonly:
            df = df[(df.trade_operation == "B") | (df.trade_operation == "S")]
        # df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_reference_id', inplace=True)
        df.drop('user_id', axis=1, inplace=True)
        details = df.to_json()
        return(details)


@api.route("/portstats", methods=['GET', 'POST'])
@login_required
# Function retuns summary statistics for portfolio NAV and values
def portstats():
    meta = {}
    # Looking to generate the following data here and return as JSON
    # for AJAX query on front page:
    # Start date, End Date, Start NAV, End NAV, Returns (1d, 1wk, 1mo, 1yr,
    # YTD), average daily return. Best day, worse day. Std dev of daily ret,
    # Higher NAV, Lower NAV + dates. Higher Port Value (date).
    data = generatenav(current_user.username)

    meta['start_date'] = (data.index.min()).date().strftime("%B %d, %Y")
    meta['end_date'] = data.index.max().date().strftime("%B %d, %Y")
    meta['start_nav'] = data['NAV'][0]
    meta['end_nav'] = data['NAV'][-1]
    meta['max_nav'] = data['NAV'].max()
    meta['max_nav_date'] = data[data['NAV'] ==
                                data['NAV'].max()].index.strftime(
        "%B %d, %Y")[0]
    meta['min_nav'] = data['NAV'].min()
    meta['min_nav_date'] = data[data['NAV'] ==
                                data['NAV'].min()].index.strftime(
        "%B %d, %Y")[0]
    meta['end_portvalue'] = data['PORT_usd_pos'][-1]
    meta['max_portvalue'] = data['PORT_usd_pos'].max()
    meta['max_port_date'] = data[data['PORT_usd_pos'] ==
                                 data['PORT_usd_pos'].max()
                                 ].index.strftime("%B %d, %Y")[0]
    meta['min_portvalue'] = round(data['PORT_usd_pos'].min(), 0)
    meta['min_port_date'] = data[data['PORT_usd_pos'] ==
                                 data['PORT_usd_pos'].min()
                                 ].index.strftime("%B %d, %Y")[0]
    meta['return_SI'] = (meta['end_nav'] / meta['start_nav']) - 1
    meta['return_1d'] = (meta['end_nav'] / data['NAV'][-2]) - 1
    meta['return_1wk'] = (meta['end_nav'] / data['NAV'][-7]) - 1
    meta['return_30d'] = (meta['end_nav'] / data['NAV'][-30]) - 1
    meta['return_90d'] = (meta['end_nav'] / data['NAV'][-90]) - 1
    meta['return_ATH'] = (meta['end_nav'] / meta['max_nav']) - 1
    yr_ago = pd.to_datetime(datetime.today() - relativedelta(years=1))
    yr_ago_NAV = data.NAV[data.index.get_loc(yr_ago, method='nearest')]
    meta['return_1yr'] = meta['end_nav'] / yr_ago_NAV - 1

    # create chart data for a small NAV chart

    meta = json.dumps(meta)
    return meta


@api.route("/navchartdatajson", methods=['GET', 'POST'])
@login_required
#  Creates a table with dates and NAV values
def navchartdatajson():
    data = generatenav(current_user.username)
    # Generate data for NAV chart
    navchart = data[['NAV']].copy()
    # dates need to be in Epoch time for Highcharts
    navchart.index = (navchart.index - datetime(1970, 1, 1)).total_seconds()
    navchart.index = navchart.index * 1000
    navchart.index = navchart.index.astype(np.int64)
    navchart = navchart.to_dict()
    navchart = navchart['NAV']
    navchart = json.dumps(navchart)
    return navchart


@api.route("/manage_custody",  methods=['GET'])
@login_required
# Back-end function to manage positions after requests are sent from
# the edit position tool from account_positions.html
def manage_custody():
    tradedetails = "EMPTY"
    # If method is post then do actions
    if request.method == "GET":
        action = request.args.get('action')
        if action == "delete_dust":
            try:
                ticker = request.args.get('ticker')
                quant_before = request.args.get('quant_before')
                from_account = request.args.get('from_account')
                # Implement the trade and write to dbase
                tradedetails = f'Trade included to wipe out {ticker} ' + \
                    f'dust amount of {quant_before} from ' +\
                    f'{from_account}'

                tradedate = datetime.now()
                # Create a unique ID
                random_hex = secrets.token_hex(21)
                if float(quant_before) < 0:
                    acc = "B"
                else:
                    acc = "S"
                trade = Trades(user_id=current_user.username,
                               trade_date=tradedate,
                               trade_account=from_account,
                               trade_asset_ticker=ticker,
                               trade_operation=acc,
                               trade_price="0",
                               trade_quantity=float(quant_before) * (-1),
                               trade_fees=0,
                               cash_value=0,
                               trade_notes=tradedetails,
                               trade_reference_id=random_hex)
                db.session.add(trade)
                db.session.commit()

            except KeyError:
                tradedetails = "Error"

        elif action == "move_dust":
            try:
                ticker = request.args.get('ticker')
                quant_before = request.args.get('quant_before')
                from_account = request.args.get('from_account')
                to_account = request.args.get('to_account')

                tradedetails = f"Trade included to move dust amount of " +\
                    f"{quant_before} from {from_account} to {to_account}"
                tradedate = datetime.now()
                if float(quant_before) < 0:
                    acc = "D"
                else:
                    acc = "W"

                # There are two sides to this trade. A deposit and withdraw.
                # First Original Account - Create a unique ID
                random_hex = secrets.token_hex(21)
                trade = Trades(user_id=current_user.username,
                               trade_date=tradedate,
                               trade_account=from_account,
                               trade_asset_ticker=ticker,
                               trade_operation=acc,
                               trade_price="0",
                               trade_quantity=float(quant_before) * (-1),
                               trade_fees=0,
                               cash_value=0,
                               trade_notes=tradedetails+" (Original Account)",
                               trade_reference_id=random_hex)
                db.session.add(trade)
                db.session.commit()

                # Now the new Account
                if float(quant_before) < 0:
                    acc = "W"
                else:
                    acc = "D"

                random_hex = secrets.token_hex(21)
                trade_2 = Trades(user_id=current_user.username,
                                 trade_date=tradedate,
                                 trade_account=to_account,
                                 trade_asset_ticker=ticker,
                                 trade_operation=acc,
                                 trade_price="0",
                                 trade_quantity=float(quant_before) * (1),
                                 trade_fees=0,
                                 cash_value=0,
                                 trade_notes=tradedetails+" (Target Account)",
                                 trade_reference_id=random_hex)
                db.session.add(trade_2)
                db.session.commit()

            except KeyError:
                tradedetails = "Error"

        elif action == "adjust_dust":
            try:
                ticker = request.args.get('ticker')
                quant_before = request.args.get('quant_before')
                from_account = request.args.get('from_account')
                to_quant = request.args.get('to_quant')
                tradedetails = f"Trade included to adjust dust amount " +\
                    f"of {quant_before} from to {to_quant} at {from_account}"
                tradedate = datetime.now()
                # Create a unique ID
                random_hex = secrets.token_hex(21)
                quant_adjust = float(to_quant) - float(quant_before)
                if quant_adjust > 0:
                    acc = "B"
                else:
                    acc = "S"
                trade = Trades(user_id=current_user.username,
                               trade_date=tradedate,
                               trade_account=from_account,
                               trade_asset_ticker=ticker,
                               trade_operation=acc,
                               trade_price="0",
                               trade_quantity=quant_adjust,
                               trade_fees=0,
                               cash_value=0,
                               trade_notes=tradedetails,
                               trade_reference_id=random_hex)
                db.session.add(trade)
                db.session.commit()

            except KeyError:
                tradedetails = "Error"

        elif action == "position_move":
            try:
                ticker = request.args.get('ticker')
                quant_before = request.args.get('quant_before')
                from_account = request.args.get('from_account')
                to_account = request.args.get('to_account')
                tradedetails = f"Trade included to move {quant_before} " +\
                    f"{ticker} from account {from_account} to " +\
                    f"account {to_account}"
                tradedate = datetime.now()
                if float(quant_before) < 0:
                    acc = "D"
                else:
                    acc = "W"

                # There are two sides to this trade. A deposit and withdraw.
                # First Original Account - Create a unique ID
                random_hex = secrets.token_hex(21)
                trade = Trades(user_id=current_user.username,
                               trade_date=tradedate,
                               trade_account=from_account,
                               trade_asset_ticker=ticker,
                               trade_operation=acc,
                               trade_price="0",
                               trade_quantity=float(quant_before) * (-1),
                               trade_fees=0,
                               cash_value=0,
                               trade_notes=tradedetails+" (Original Account)",
                               trade_reference_id=random_hex)
                db.session.add(trade)
                db.session.commit()

                # Now the new Account
                if float(quant_before) < 0:
                    acc = "W"
                else:
                    acc = "D"

                random_hex = secrets.token_hex(21)
                trade_2 = Trades(user_id=current_user.username,
                                 trade_date=tradedate,
                                 trade_account=to_account,
                                 trade_asset_ticker=ticker,
                                 trade_operation=acc,
                                 trade_price="0",
                                 trade_quantity=float(quant_before) * (1),
                                 trade_fees=0,
                                 cash_value=0,
                                 trade_notes=tradedetails+" (Target Account)",
                                 trade_reference_id=random_hex)
                db.session.add(trade_2)
                db.session.commit()

            except KeyError:
                tradedetails = "Error"
            tradedetails = f"Trade included to move position from " +\
                f"{from_account} to {to_account}"

        elif action == "position_adjust":
            try:
                ticker = request.args.get('ticker')
                quant_before = request.args.get('quant_before')
                from_account = request.args.get('from_account')
                to_quant = request.args.get('to_quant')
                tradedetails = f"Trade included to adjust position from " +\
                    f"{quant_before} to to {to_quant}"
                tradedate = datetime.now()
                # Create a unique ID
                random_hex = secrets.token_hex(21)
                quant_adjust = float(to_quant) - float(quant_before)
                if quant_adjust > 0:
                    acc = "B"
                else:
                    acc = "S"
                trade = Trades(user_id=current_user.username,
                               trade_date=tradedate,
                               trade_account=from_account,
                               trade_asset_ticker=ticker,
                               trade_operation=acc,
                               trade_price="0",
                               trade_quantity=quant_adjust,
                               trade_fees=0,
                               cash_value=0,
                               trade_notes=tradedetails,
                               trade_reference_id=random_hex)
                db.session.add(trade)
                db.session.commit()

            except KeyError:
                tradedetails = "Error"

    return(json.dumps(tradedetails))


@api.route("/portfolio_compare_json",  methods=['GET'])
@login_required
# Compare portfolio performance to a list of assets
# Takes arguments:
# tickers  - (comma separated. ex: BTC,ETH,AAPL)
# start    - start date in the format YYMMDD
# end      - end date in the format YYMMDD
# method   - "chart": returns NAV only data for charts
#          - "all": returns all data (prices and NAV)
#          - "meta": returns metadata information
def portfolio_compare_json():
    if request.method == "GET":
        tickers = request.args.get('tickers').upper()
        tickers = tickers.split(",")
        start_date = request.args.get('start')
        method = request.args.get('method')

        # Check if start and end dates exist, if not assign values
        if not start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except (ValueError, TypeError) as e:
                start_date = 0

        end_date = request.args.get('end')
        if not end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except (ValueError, TypeError) as e:
                end_date = datetime.now()
    data = {}

    logging.info("[portfolio_compare_json] NAV requested in list of " +
                 "tickers, requesting generatenav.")
    nav = generatenav(current_user.username)
    # Trim to leave only dates and NAV
    nav_only = nav['NAV']

    # Now go over tickers and merge into nav_only df
    messages = {}
    meta_data = {}
    for ticker in tickers:
        if ticker == "NAV":
            # Ticker was NAV, skipped
            continue
        data, notification, meta = alphavantage_historical(ticker)
        # If notification is an error, skip this ticker
        if notification == "error":
            messages[ticker] = data
            continue
        data.reset_index(inplace=True)
        data = data.set_index(
            list(data.columns[[0]]))
        try:
            data = data['4a. close (USD)']
        except KeyError:
            try:
                data = data['4. close']
            except KeyError:
                messages[ticker] = "Key Error on Data"
                continue

        # convert string date to datetime
        data.index = pd.to_datetime(data.index)
        # rename index to date to match dailynav name
        data.index.rename('date', inplace=True)
        data.rename(ticker+'_price', inplace=True)
        data = data.astype(float)
        # Fill dailyNAV with prices for each ticker
        nav_only = pd.merge(nav_only, data, on='date', how='left')
        messages[ticker] = "ok"
        meta_data[ticker] = meta
        logging.info(f"[portfolio_compare_json] {ticker}: Success - Merged OK")

    nav_only.fillna(method='pad', inplace=True)
    # Trim this list only to start_date to end_date:
    mask = ((nav_only.index >= start_date) & (nav_only.index <= end_date))
    nav_only = nav_only.loc[mask]
    # Now create the list of normalized Returns for the available period
    # Plus create a table with individual analysis for each ticker and NAV
    nav_only['NAV_norm'] = (nav_only['NAV'] / nav_only['NAV'][0]) * 100
    nav_only['NAV_ret'] = nav_only['NAV_norm'].pct_change()
    table = {}
    table['meta'] = {}
    table['meta']['start_date'] = (nav_only.index[0]).strftime('%m-%d-%Y')
    table['meta']['end_date'] = nav_only.index[-1].strftime('%m-%d-%Y')
    table['meta']['number_of_days'] = ((nav_only.index[-1] -
                                        nav_only.index[0])).days
    table['meta']['count_of_points'] = nav_only['NAV'].count().astype(float)
    table['NAV'] = {}
    table['NAV']['start'] = nav_only['NAV'][0]
    table['NAV']['end'] = nav_only['NAV'][-1]
    table['NAV']['return'] = (nav_only['NAV'][-1] / nav_only['NAV'][0]) - 1
    table['NAV']['avg_return'] = nav_only['NAV_ret'].mean()
    table['NAV']['ann_std_dev'] = nav_only['NAV_ret'].std() * math.sqrt(365)
    for ticker in tickers:
        if messages[ticker] == "ok":
            # Include new columns for return and normalized data
            nav_only[ticker+'_norm'] = (nav_only[
                ticker+'_price'] / nav_only[ticker+'_price'][0]) * 100
            nav_only[ticker+'_ret'] = nav_only[ticker+'_norm'].pct_change()
            # Create Metadata
            table[ticker] = {}
            table[ticker]['start'] = nav_only[ticker+'_price'][0]
            table[ticker]['end'] = nav_only[ticker+'_price'][-1]
            table[ticker]['return'] = (nav_only[ticker+'_price'][-1] /
                                       nav_only[ticker+'_price'][0]) - 1
            table[ticker]['comp2nav'] = table[ticker]['return'] - \
                table['NAV']['return']
            table[ticker]['avg_return'] = nav_only[ticker+'_ret'].mean()
            table[ticker]['ann_std_dev'] = nav_only[ticker+'_ret'].std() *\
                math.sqrt(365)

    logging.info("[portfolio_compare_json] Success")

    # Create Correlation Matrix
    filter_col = [col for col in nav_only if col.endswith('_ret')]
    nav_matrix = nav_only[filter_col].copy()
    corr_matrix = nav_matrix.corr(method='pearson').round(2)
    corr_html = corr_matrix.to_html(classes='table small text-center',
                                    border=0, justify='center')

    # Now, let's return the data in the correct format as requested
    if method == "chart":
        return jsonify({"data": nav_only.to_json(),
                        "messages": messages,
                        "meta_data": meta_data,
                        "table": table,
                        "corr_html": corr_html})

    return (nav_only.to_json())
