from typing import Literal, Dict, List, Tuple, Union, Any, Optional
import pandas as pd
import logging
from src.expert_system.utils.calculator import format_vnd

def get_top_portfolios() -> str:
    """Useful for getting current top portfolios."""
    return "top portfolios"

def _get_top_portfolios() -> pd.DataFrame:
    """Useful for getting current top portfolios."""
    ...