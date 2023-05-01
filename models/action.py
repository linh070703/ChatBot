import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Literal, Dict, Union, Any, Tuple
from utils.model_api import generate_action_params_chatgpt_api
from utils.logger import setup_logging_display_only

PROMPT = """ This is a financial assistant system. This system is able to take corresponding action when user request. English and Vietnamese are supported. There are 3 possible system's action: TRANSFER[<receiver>,<amount>], TRANSFER_TO_EACH_USERS[<amount_each>], CREATE_CHAT_GROUP[<user_comma_separated>].
Note that when TRANSFER, money abbreviation should be expanded without comma or dot. E.g. (30k=30000, 24tr=24000000)"""
# Minh: Tao muốn chuyển khoản cho Nam 6966 k VND.
# Minh's request system action: TRANSFER[Nam,6966000]

def get_action_params(
        messages: List[Dict[str, str]],
        action: Literal["TRANSFER", "CREATE_CHAT_GROUP", "TRANSFER_TO_EACH_USERS"],
    ) -> Dict[str, str]:
    """
    Get action parameters from conversation history and user's intention.

    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "message". "user" is the name of user who sent the message. "message" is the message sent by the user.
        action (Literal["TRANSFER", "CREATE_CHAT_GROUP"]): User's intention, which is one of "TRANSFER" or "CREATE_CHAT_GROUP".
    
    Returns:
        Dict[str, str]: Action parameters. If action is "TRANSFER", then the returned dictionary should have 2 keys: "receiver" and "amount". If action is "CREATE_CHAT_GROUP", then the returned dictionary should have 1 key: "users".

    Example:
        >>> messages = [
        ...     {"user": "Minh", "message": "Tao muốn chuyển khoản cho Nam 6966 k VND."},
        ... ]
        >>> dectect_user_intention(messages, action="TRANSFER")
        {
            "receiver": "Nam",
            "amount": "6966000",
        }
        >>> messages = [    
        ...     {"user": "Minh", "message": "Chuyển mỗi người 100k."},
        ... ]
        >>> dectect_user_intention(messages, action="TRANSFER_TO_EACH_USERS")
        {
            "amount_each": "100000",
        }
        >>> messages = [
        ...     {"user": "Minh", "message": "Tao muốn tạo nhóm chat với Nam và Lan."},
        ... ]
        >>> dectect_user_intention(messages, action="CREATE_CHAT_GROUP")
        {
            "users": [
                "Nam",
                "Lan",
            ]
        }
    """
    assert action in ["TRANSFER", "CREATE_CHAT_GROUP", "TRANSFER_TO_EACH_USERS"], f"Invalid action: {action}"
    conversation = "\n".join([f"{message['user']}: {message['message']}" for message in messages])
    last_user = messages[-1]['user']
    model_input = f"{PROMPT}\n{conversation}\n{last_user}'s request system action: {action}"
    print("Model input: \n", model_input)
    output = generate_action_params_chatgpt_api(model_input)
    print("Model output: \n", output + "]")
    params = {}
    if action == "TRANSFER":
        params["receiver"] = output.split("[")[1].split(",")[0]
        params["amount"] = output.split("[")[1].split(",")[1]
    elif action == "CREATE_CHAT_GROUP":
        params["users"] = output.split("[")[1].split(",")
    elif action == "TRANSFER_TO_EACH_USERS":
        params["amount_each"] = output.split("[")[1].split(",")[0]
    return params


if __name__ == "__main__":
    setup_logging_display_only()
    out = get_action_params(messages=[
        {"user": "Minh", "message": "Hello, I want to check my account balance"},
        {"user": "Lan", "message": "Ready for a party?"},
        {"user": "Minh", "message": "Yes, I am ready."},
        {"user": "Minh", "message": "I want to transfer 3289723 VND to Hung."},
        {"user": "Cường", "message": "Chuyển quà sinh nhật mỗi cháu 400k"},
        {"user": "Hung", "message": "I want to create a chat group with Minh, Lan, and Cường named 'Party'."},
        {"user": "Minh", "message": "I want to transfer 3289723 VND to Hung với lời nhắn là 'Chúc mừng sinh nhật'."},
    ], action="TRANSFER")
    print("Output: ", out)
        