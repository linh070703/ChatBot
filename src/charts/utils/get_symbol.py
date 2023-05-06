import os
from alpha_vantage.timeseries import TimeSeries

def get_symbol(company_name):
	# Initialize the TimeSeries object with your API key
	ts = TimeSeries(
		key=os.environ.get('ALPHA_VANTAGE_API_KEY'),
		output_format='pandas'
	)

	# Use the Alpha Vantage API to get the stock symbol for the company
	symbol_data, _ = ts.get_symbol_search(company_name)
	company_symbol = symbol_data.iloc[0]['1. symbol']

	return company_symbol
