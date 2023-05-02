import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from typing import List, Literal, Dict, Union, Any, Tuple
from utils.model_api import generate_conversation_chatgpt_api
from utils.logger import setup_logging_display_only, logging
from expert_system import loan, money_management, economical

PROMPT_GENERAL = """This is a Personal Finance Assistant system. This system can provide comprehensive response along with useful general detailed advices for user. Answer in language as same as User's question. English and Vietnamese are supported. Answers should be no more than 250 words and using markdown syntax when needed."""
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
    And many more...
How can I help you today?
"""


def ask_assistant(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    """
    Ask assistant for help.
    
    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "message". "user" is the name of user who sent the message. "message" is the message sent by the user.

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
        ...     {"user": "Minh", "message": "I want to ask for financial advice"},
        ... ])
        >>> print(response)
        Sure, I can help you with that. What do you want to ask?
        >>> print(suggestions)
        ['Help me create a monthly budget plan', 'Help me calculate my target saving plan', 'Help me detect if a loan is usury or not', 'Help me invest my money', 'Help me pay off my debt']
        >>> response, suggestions = ask_assistant(messages=[
        ...     {"user": "Minh", "message": "I want to ask for financial advice"},
        ...     {"user": "assistant", "message": "Sure, I can help you with that. What do you want to ask?"},
        ...     {"user": "Minh", "message": "Help me create a monthly budget plan"},
        ... ])
        >>> print(response)
    """
    if len(messages) == 0:
        return INTRODUCTION, []

    message = messages[-1]["message"]
    if money_management.is_money_management_question(message):
        return money_management.money_management_suggestion(messages)
    elif economical.is_economical_question(message):
        return economical.economical_suggestion(messages)
    elif loan.is_loan_question(message):
        return loan.loan_suggestion(messages)
    else:
        return general_suggestion(messages)

def general_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    """
    Suggest general advice
    """
    messages = messages[-12:]
    conversation = "\n".join([f"{'User' if message['user'].lower() != 'assistant' else 'Assistant'}: {message['message']}" for message in messages])
    model_input = f"{PROMPT_GENERAL}\n{conversation}\nAssistant: "
    print("Model input: \n", model_input)
    output = generate_conversation_chatgpt_api(model_input)
    print("Model output: \n", output)
    return output, []
    

if __name__ == "__main__":
    setup_logging_display_only()
    response, suggestions = general_suggestion(messages=[
        {"user": "Minh", "message": "I want to ask for financial advice"},
        {"user": "assistant", "message": "Sure, I can help you with that. What do you want to ask?"},
        {"user": "Minh", "message": "Help me create a monthly budget plan"},
    ])
    print(f"Response: {response}")
        