from typing import Dict, List, Tuple, Union, Literal, Any

def is_money_management_question(message: str) -> bool:
    ...

def money_management_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    ...