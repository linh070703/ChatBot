from typing import Dict, List, Tuple, Union, Literal, Any
import logging

def is_loan_question(message: str) -> bool:
    ...

def loan_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    ...

def detect_usury():
    ...