from flask import (
    Blueprint,
    render_template,
    request
)

from src.charts.utils.get_compare_metrics import get_compare_metrics
from src.charts.utils.get_earning_data import get_earning_data

chart = Blueprint('chart', __name__)

@chart.route('/compare', methods=['GET'])
def compare():
    symbols = request.args.get('symbols').split(',')

    metrics = {}
    for symbol in symbols:
        metrics[symbol] = get_compare_metrics(symbol)

    print(metrics)

    return render_template('iframe.html')


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
