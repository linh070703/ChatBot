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


@chart.route('/earning', methods=['GET'])
def earning():
    symbol = request.args.get('symbol')

    earning_data = get_earning_data(symbol)

    # map to each element become reportedEPS - estimatedEPS
    data = list(map(lambda x: float(
        x['reportedEPS']) - float(x['estimatedEPS']), earning_data))
    
    # Round to 2 decimal places
    data = list(map(lambda x: round(x, 2), data))

    chart_title = 'My Chart Title'
    labels = list(map(lambda x: x['fiscalDateEnding'], earning_data))

    return render_template('iframe.html', data=data, labels=labels, chart_title=chart_title, symbol=symbol)
