from typing import Dict, List, Tuple, Union, Literal, Any
from utils.logger import print

def is_economical_question(message: str) -> bool:
    ...

def economical_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    ...