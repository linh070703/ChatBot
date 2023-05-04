import os
from alpha_vantage.timeseries import TimeSeries

def get_metrics(symbol):
	ts = TimeSeries(
		key=os.environ.get('ALPHA_VANTAGE_API_KEY'),
		output_format='pandas'
	)
	data, meta_data = ts.get_intraday(symbol=symbol)

	volatility = (data['2. high'] - data['3. low']) / data['2. high']

	returns = data['4. close'].pct_change()

	initial_price = data.iloc[0]['4. close']
	current_price = data.iloc[-1]['4. close']
	roi = (current_price - initial_price) / initial_price * 100

	print(returns)
	

	return {
		'volatility': volatility.mean(),
		'return': returns[0],
		'roi': roi
	}
