import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from typing import List, Literal, Dict, Union, Any, Tuple
from utils.model_api import generate_general_call_chatgpt_api
from utils.logger import setup_logging_display_only, print
from models.translator import convert_answer_language_to_same_as_question, batch_convert_answer_language_to_same_as_question
import logging
from expert_system import loan, money_management, economical
from models.langchain import advisor

VIETNAMESE_MODE = True

PROMPT_GENERAL = """This is a Personal Finance Assistant system. This system can provide comprehensive response along with useful general detailed advices for user. Answer in language as same as User's question. Answers should be no more than 250 words and use markdown syntax when needed."""
INTRODUCTION = """Hi, I am your personal finance assistant. I can help you with the following tasks:

- Check your account balance
- Transfer money to another account
- Create a chat group
- Ask for financial advice, such as:
    + Create a monthly budget plan.
    + Calculate your target saving plan.
    + Detect if a loan is usury or not.
    + Advice on how to invest your money.
    + Advice on how to pay off your debt.
    + And many more...

How can I help you today?
""" if not VIETNAMESE_MODE else """Xin chào, tôi là trợ lý tài chính cá nhân của bạn. Tôi có thể giúp bạn với các công việc sau:

- Kiểm tra số dư tài khoản
- Chuyển tiền đến tài khoản khác
- Tạo nhóm chat với bạn bè
- Yêu cầu tư vấn tài chính, như:
    + Tạo kế hoạch ngân sách hàng tháng của bạn.
    + Tính toán kế hoạch tiết kiệm mục tiêu của bạn.
    + Phát hiện xem một khoản vay có phí lãi nặng hay không.
    + Tư vấn về cách đầu tư tiền của bạn.
    + Tư vấn về cách thanh toán nợ của bạn.
    + Và nhiều hơn nữa...

Tôi có thể giúp gì cho bạn hôm nay?
"""

def match_question(messages) -> Tuple[Union[str, None], List[str]]:
    response = None
    suggestions = None
    # message: str = messages[-1]["content"]
    
    # message = convert_answer_language_to_same_as_question(question="Tiếng Việt", answer=message)
    # messages
    
    if money_management.is_money_management_question(messages):
        logging.info("Money management question detected")
        response, suggestions = money_management.money_management_suggestion(messages)
    elif economical.is_economical_question(messages):
        logging.info("Economical question detected")
        response, suggestions = economical.economical_suggestion(messages)
    # elif loan.is_loan_question(message):
    #     response, suggestions = loan.loan_suggestion(messages)

    logging.info("No pre-defined question matched")
    if response is not None:
        response = convert_answer_language_to_same_as_question(question=messages[-1]['content'], answer=response)
        suggestions = batch_convert_answer_language_to_same_as_question(question=messages[-1]['content'], answers=suggestions)

    return response, suggestions

def ask_assistant(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    """
    Ask assistant for help.
    
    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.

    Returns:
        Response (str): Response from the assistant.
        Suggestions (List[str]): List of suggestions for next user's message.
    
    Example:
        >>> introduction, suggestions = ask_assistant(messages=[])
        >>> print(introduction)
        Hi, I am your personal finance assistant. I can help you with the following tasks:
        - Check your account balance
        - Transfer money to another account
        - Create a chat group
        - Ask for financial advice, such as:
            + Create a monthly budget plan.
            + Calculate your target saving plan.
            + Detect if a loan is usury or not.
            + Advice on how to invest your money.
            + Advice on how to pay off your debt.
            And many more...
        How can I help you today?
        >>> print(suggestions)
        ['I want to check my account balance', 'I want to give Minh 40k for bún đậu mắm tôm', 'I want to create a chat group with Hung and Cuong', 'I want to ask for financial advice']
        >>> response, suggestions = ask_assistant(messages=[
        ...     {"user": "Minh", "content": "I want to ask for financial advice"},
        ... ])
        >>> print(response)
        Sure, I can help you with that. What do you want to ask?
        >>> print(suggestions)
        ['Help me create a monthly budget plan', 'Help me calculate my target saving plan', 'Help me detect if a loan is usury or not', 'Help me invest my money', 'Help me pay off my debt']
        >>> response, suggestions = ask_assistant(messages=[
        ...     {"user": "Minh", "content": "I want to ask for financial advice"},
        ...     {"user": "assistant", "content": "Sure, I can help you with that. What do you want to ask?"},
        ...     {"user": "Minh", "content": "Help me create a monthly budget plan"},
        ... ])
        >>> print(response)
    """
    if len(messages) == 0:
        return INTRODUCTION, [
            "Tôi muốn kiểm tra số dư tài khoản",
            "Tôi muốn chuyển 30k cho Minh",
            "Tôi muốn tạo nhóm chat với Hùng và Cường",
            "Tôi muốn được tư vấn tài chính"
        ]
    
    response, suggestions = match_question(messages)

    if response is not None:
        return response, suggestions
    else:
        # above cases all failed
        return general_suggestion(messages)


def general_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    """
    Suggest general advice
    """
    messages = messages[-4:]
    output = advisor.ask(messages)
    return output, []
    

if __name__ == "__main__":
    setup_logging_display_only()
    # response, suggestions = ask_assistant(messages=[
    #     {"user": "Minh", "content": "I want to ask for financial advice"},
    #     {"user": "assistant", "content": "Sure, I can help you with that. What do you want to ask?"},
    #     {"user": "Minh", "content": "Help me create a monthly budget plan"},
    # ])

    response, suggestions = general_suggestion(messages=[
        {"user": "Minh", "content": "Compare Bank of America, Apple, and Google"},
    ])
    logging.info(f"Response: {response}")
    logging.info(f"Suggestions: {suggestions}")
        