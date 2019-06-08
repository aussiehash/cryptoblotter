import pandas as pd
import numpy as np
from flask import render_template, request, Blueprint
from flask_login import current_user, login_required
from cryptoalpha import db, mhp as mrh
from cryptoalpha.models import Trades
from datetime import datetime
from cryptoalpha.users.utils import (generatenav, generate_pos_table,
                                     generatepnltable)

portfolio = Blueprint('portfolio', __name__)


@portfolio.route("/portfolio")
@login_required
# Home Page - details of the portfolio
def portfolio_main():
    user = current_user.username
    transactions = Trades.query.filter_by(user_id=current_user.username)
    if transactions.count() == 0:
        return render_template('empty.html')

    portfolio_data, pie_data = generate_pos_table(user, "USD", False)
    if portfolio_data == "ConnectionError":
        return render_template('offline.html', title="Connection Error")
    return render_template('portfolio.html', title="Portfolio View",
                           portfolio_data=portfolio_data, pie_data=pie_data)


@portfolio.route("/navchart")
# Page with a single historical chart of NAV
# Include portfolio value as well as CF_sumcum()
@login_required
def navchart():
    data = generatenav(current_user.username)
    navchart = data[['NAV']].copy()
    # dates need to be in Epoch time for Highcharts
    navchart.index = (navchart.index - datetime(1970, 1, 1)).total_seconds()
    navchart.index = navchart.index * 1000
    navchart.index = navchart.index.astype(np.int64)
    navchart = navchart.to_dict()
    navchart = navchart['NAV']

    port_value_chart = data[['PORT_cash_value',
                             'PORT_usd_pos', 'PORT_ac_CFs']].copy()
    port_value_chart['ac_pnl'] = port_value_chart['PORT_usd_pos'] -\
        port_value_chart['PORT_ac_CFs']
    # dates need to be in Epoch time for Highcharts
    port_value_chart.index = (port_value_chart.index -
                              datetime(1970, 1, 1)).total_seconds()
    port_value_chart.index = port_value_chart.index * 1000
    port_value_chart.index = port_value_chart.index.astype(np.int64)
    port_value_chart = port_value_chart.to_dict()

    return render_template('navchart.html', title="NAV Historical Chart",
                           navchart=navchart,
                           port_value_chart=port_value_chart)


@portfolio.route("/heatmap")
@login_required
# Returns a monthly heatmap of returns and statistics
def heatmap():
    # If no Transactions for this user, return empty.html
    transactions = Trades.query.filter_by(
        user_id=current_user.username).order_by(
        Trades.trade_date)
    if transactions.count() == 0:
        return render_template('empty.html')

    # Generate NAV Table first
    data = generatenav(current_user.username)
    data['navpchange'] = ((data['NAV'] / data['NAV'].shift(1)) - 1)
    returns = data['navpchange'].copy()
    # Run the mrh function to generate heapmap table
    heatmap = mrh.get(returns, eoy=True)

    heatmap_stats = heatmap.copy()
    cols = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
            'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'eoy']
    cols_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                   'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    years = heatmap.index.to_list()
    heatmap_stats['MAX'] = heatmap_stats[
        heatmap_stats[cols_months] != 0].max(axis=1)
    heatmap_stats['MIN'] = heatmap_stats[
        heatmap_stats[cols_months] != 0].min(axis=1)
    heatmap_stats['POSITIVES'] = heatmap_stats[
        heatmap_stats[cols_months] > 0].count(axis=1)
    heatmap_stats['NEGATIVES'] = heatmap_stats[
        heatmap_stats[cols_months] < 0].count(axis=1)
    heatmap_stats['POS_MEAN'] = heatmap_stats[
        heatmap_stats[cols_months] > 0].mean(axis=1)
    heatmap_stats['NEG_MEAN'] = heatmap_stats[
        heatmap_stats[cols_months] < 0].mean(axis=1)
    heatmap_stats['MEAN'] = heatmap_stats[
        heatmap_stats[cols_months] != 0].mean(axis=1)

    return render_template('heatmap.html',
                           title="Monthly Returns HeatMap",
                           heatmap=heatmap,
                           heatmap_stats=heatmap_stats,
                           years=years, cols=cols)


@portfolio.route("/volchart", methods=['GET', 'POST'])
@login_required
# Only returns the html - request for data is done through jQuery AJAX
def volchart():
    return render_template('volchart.html',
                           title="Historical Volatility Chart")


@portfolio.route("/pnl", methods=['GET', 'POST'])
@login_required
# Function to return a table with realized PnL and matching Tables
# takes ticker, method and dates as arguments
def pnl():
    if request.method == 'GET':
        id = request.args.get('id')
        method = request.args.get('method')
        start = request.args.get('start')
        end = request.args.get('end')

    realpnl, metadata = generatepnltable(current_user.username, id,
                                         method, start, end)
    # realpnl = json.dumps(realpnl, indent=4)
    return render_template('pnl.html', realpnl=realpnl, metadata=metadata,
                           title="PnL History")


@portfolio.route("/portfolio_compare",  methods=['GET'])
@login_required
def portfolio_compare():
    return render_template('portfolio_compare.html',
                           title="Portfolio Comparison")
