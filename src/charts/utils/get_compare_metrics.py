import requests
from bs4 import BeautifulSoup

def get_compare_metrics(symbol):
	endpoint = f'https://volafy.net/equity/{symbol}'

	try:
		# Get HTML and parse it
		response = requests.get(endpoint)

		soup = BeautifulSoup(response.text, 'html.parser')

		# Get metrics
		elements_volatility = soup.find_all('span', class_='volatility-card_colItemValue__9Usfd')
		volatility = elements_volatility[3].text

		elements_return = soup.find_all('div', class_='symbol-title-price_priceWrapper__5jyjK')[0]
		# get text of last child
		return_value = elements_return.contents[-1].text

		# remove % sign and parse to float
		volatility = float(volatility[:-1])
		return_value = float(return_value.split('%')[0])

		return {
			'volatility': volatility,
			'return': return_value
		}
	except:
		print('Error')
		return None

