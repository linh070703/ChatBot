from flask import (
	Blueprint,
	render_template,
	request
)

from src.charts.utils.get_metrics import get_metrics

chart = Blueprint('chart', __name__)

@chart.route('/compare', methods=['GET'])
def compare():
	symbols = request.args.get('symbols').split(',')
	
	metrics = {}
	for symbol in symbols:
		metrics[symbol] = get_metrics(symbol)

	print(metrics)

	return render_template('iframe.html')
