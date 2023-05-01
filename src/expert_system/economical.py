from typing import Dict, List, Tuple, Union, Literal, Any

def is_economical_question(message: Dict[str, str]) -> bool:
    ...

def economical_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    ...