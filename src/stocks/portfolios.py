from typing import Literal, Dict, List, Tuple, Union, Any, Optional
import pandas as pd
import logging
import requests
import os
from src.expert_system.utils.calculator import format_vnd

API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
LIMIT = 10

def get_top_portfolios(top=10) -> str:
    """Useful for getting current top portfolios."""
    title, top_portfolios = _get_top_portfolios()
    top_portfolios = top_portfolios.to_markdown()
#     res = f"""## {title}
# {top_portfolios}
# """
    return top_portfolios

def _get_top_portfolios(top=10) -> Tuple[str, pd.DataFrame]:
	endpoint = f'https://www.alphavantage.co/query?function=TOURNAMENT_PORTFOLIO&apikey={API_KEY}'
	
	response = requests.get(endpoint)
	data = response.json()

	df = pd.DataFrame(data['ranking'])
	df = df[:top]
	
	df.set_index('rank', inplace=True)

	df['portfolio'] = df['portfolio'].apply(map_to_readable_format)
	title = df['measurement_start'].unique().tolist()[0] + ' - ' + df['measurement_end'].unique().tolist()[0]


	df['USD'] = df['start_value_usd'].astype(str) + ' → ' + df['end_value_usd'].astype(str)
	df['percent_gain'].apply(lambda x: str(round(float(x), 2)) + '%')
	df = df[['portfolio', 'USD', 'percent_gain']]

	df.columns = ['Portfolio', 'USD', 'Percent Gain']
	df.index.name = 'Rank'
 
	return title, df


def map_to_readable_format(portfolios: List[Dict[str, str]]) -> str:
    """Map to readable format."""
    if len(portfolios) == 1:
        output = portfolios[0]['symbol']
    else:
        total_share = sum([int(portfolio['shares']) for portfolio in portfolios])
        output = ', '.join([f'{portfolio["symbol"]} ({round(int(portfolio["shares"]) / total_share * 100, 2)}%)' for portfolio in portfolios])
    return output