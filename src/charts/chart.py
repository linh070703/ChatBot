from flask import (
    Blueprint,
    render_template,
    request
)
import random

from src.charts.utils.get_compare_metrics import get_compare_metrics
from src.charts.utils.get_earning_data import get_earning_data

chart = Blueprint('chart', __name__)

@chart.route('/compare', methods=['GET'])
def compare():
    symbols = request.args.get('symbols').split(',')
    # convert to rgba with 0.5 alpha
    colors = [
        'rgba(158, 1, 66, 0.5)',
        'rgba(213, 62, 79, 0.5)',
        'rgba(244, 109, 67, 0.5)',
        'rgba(253, 174, 97, 0.5)',
        'rgba(254, 224, 139, 0.5)',
        'rgba(230, 245, 152, 0.5)',
        'rgba(171, 221, 164, 0.5)',
        'rgba(102, 194, 165, 0.5)',
        'rgba(50, 136, 189, 0.5)',
        'rgba(94, 79, 162, 0.5)',
    ]

    # metrics = {}
    volatilitys = []
    returns = []
    for symbol in symbols:
        metric = get_compare_metrics(symbol)

        if metric is not None:
            volatilitys.append(metric['volatility'])
            returns.append(metric['return'])
        else:
            volatilitys.append(0)
            returns.append(0)

    random.shuffle(colors)
    colors = colors[:len(symbols)]
    # suffle colors

    chart_title = 'Compare of ' + ', '.join(symbols)

    return render_template('compare.html', volatilitys=volatilitys, returns=returns, symbols=symbols, colors=colors, chart_title=chart_title)


@chart.route('/earning-bar', methods=['GET'])
def earning_bar():
    LIMIT = 8
    symbol = request.args.get('symbol')

    earning_data = get_earning_data(symbol)
    earning_data = earning_data[:min(LIMIT, len(earning_data))]


    labels = list(map(lambda x: x['fiscalDateEnding'], earning_data))
    reportedEPS = list(map(lambda x: round(float(x['reportedEPS']), 2), earning_data))
    estimatedEPS = list(map(lambda x: round(float(x['estimatedEPS']), 2), earning_data))

    return render_template('earning-bar.html', reportedEPS=reportedEPS, estimatedEPS=estimatedEPS, labels=labels, symbol=symbol)

@chart.route('/earning-line', methods=['GET'])
def earning_line():
    LIMIT = 16
    symbol = request.args.get('symbol')

    earning_data = get_earning_data(symbol)
    earning_data = earning_data[:min(LIMIT, len(earning_data))]

    labels = list(map(lambda x: x['fiscalDateEnding'], earning_data))
    reportedEPS = list(map(lambda x: round(float(x['reportedEPS']), 2), earning_data))

    return render_template('earning-line.html', reportedEPS=reportedEPS, labels=labels, symbol=symbol)
