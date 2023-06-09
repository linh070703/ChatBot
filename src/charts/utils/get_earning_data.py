import requests
import os

API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
LIMIT = 10

def get_earning_data(symbol):
	endpoint = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={API_KEY}'
	
	response = requests.get(endpoint)
	data = response.json()
	
	quarterlyEarnings = data['quarterlyEarnings']

	# get first LIMIT quarterly earnings
	quarterlyEarnings = quarterlyEarnings[:LIMIT]

	return quarterlyEarnings
