from typing import Dict, List, Tuple, Union, Literal, Any

def is_money_management_question(message: str) -> bool:
    """
    Lên kế hoạch tiết kiệm.

    Args:
        message (str): Message from user.
    
    Returns:
        bool: True if the message is about money management, False otherwise.
    
    Example:
    >>> is_money_management_question("Tôi muốn lên kế hoạch tiết kiệm.")
    True
    >>> is_money_management_question("Tính toán kế hoạch tiết kiệm mục tiêu của bạn.")
    True
    """

    return (
        "kế hoạch tiết kiệm" in message 
    )


def money_management_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    ...