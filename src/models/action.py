import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Literal, Dict, Union, Any, Tuple
from utils.model_api import generate_action_params_chatgpt_api
from utils.logger import setup_logging_display_only, pprint, print

PROMPT = """This is a financial assistant system. This system is able to take corresponding action when user request. English and Vietnamese are supported. There are 3 possible system's action: TRANSFER[<receiver>,<amount>|<msg (null)>], TRANSFER_TO_EACH_USERS[<amount_each>|<msg (null)>], CREATE_CHAT_GROUP[<user_comma_separated>|<group_name (null)>].
Note that when TRANSFER, money abbreviation should be expanded without comma or dot. E.g. (30k=30000, 24tr=24000000, 5 nghìn=5000, tám chục nghìn=80000)"""
# Minh: I want to transfer 3289723 VND to Hung với lời nhắn là 'Chúc mừng sinh nhật nhé, nhớ học giỏi'.
# Minh's request system action: TRANSFER[Hung,3289723|Chúc mừng sinh nhật nhé, nhớ học giỏi]

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
        ...     {"user": "Minh", "content": "Tao muốn chuyển khoản cho Nam 6966 k VND tiền bún đậu"},
        ... ]
        >>> get_action_params(messages, action="TRANSFER")
        {
            "receiver": "Nam",
            "amount": "6966000",
            "msg": "bún đậu",
        }
        >>> messages = [    
        ...     {"user": "Minh", "content": "Chuyển mỗi người 100k."},
        ... ]
        >>> get_action_params(messages, action="TRANSFER_TO_EACH_USERS")
        {
            "amount_each": "100000",
            "msg": None,
        }
        >>> messages = [
        ...     {"user": "Minh", "content": "Tao muốn tạo nhóm chat với Nam và Lan."},
        ... ]
        >>> get_action_params(messages, action="CREATE_CHAT_GROUP")
        {
            "users": [
                "Nam",
                "Lan",
            ],
            "group_name": None,
        }
    """
    assert action in ["TRANSFER", "CREATE_CHAT_GROUP", "TRANSFER_TO_EACH_USERS"], f"Invalid action: {action}"
    messages = messages[-2:]
    conversation = "\n".join([f"{message['user']}: {message['content']}" for message in messages])
    last_user = messages[-1]['user']
    model_input = f"{PROMPT}\n{conversation}\n{last_user}'s request system action: {action}"
    print("Model input: \n", model_input)
    output = generate_action_params_chatgpt_api(model_input)
    print("Model output: \n", output + "]")
    params = {}
    if action == "TRANSFER":
        params["receiver"] = output.split("|")[0].split("[")[1].split(",")[0].strip()
        params["amount"] = output.split("|")[0].split("[")[1].split(",")[1].strip()
        msg = output.split("[")[1].split("|")[1:]
        msg = "|".join(msg).split("]")[0].strip()
        if msg.lower() == "null" or msg.lower() == "none" or msg == "":
            params["msg"] = None
        else:
            params["msg"] = msg
    elif action == "CREATE_CHAT_GROUP":
        params["members"] = output.split("|")[0].split("[")[1].split(",")
        group_name = output.split("[")[1].split("|")[1:]
        group_name = "|".join(group_name).split("]")[0].strip()
        if group_name.lower() == "null" or group_name.lower() == "none" or group_name == "":
            params["group_name"] = None
        else:
            params["group_name"] = group_name
    elif action == "TRANSFER_TO_EACH_USERS":
        params["amount_each"] = output.split("|")[0].split("[")[1].split(",")[0].strip()
        msg = output.split("[")[1].split("|")[1:]
        msg = "|".join(msg).split("]")[0].strip()
        if msg.lower() == "null" or msg.lower() == "none" or msg == "":
            params["msg"] = None
        else:
            params["msg"] = msg
    return params


if __name__ == "__main__":
    setup_logging_display_only()
    out = get_action_params(messages=[
        {"user": "Minh", "content": "Hello, I want to check my account balance"},
        {"user": "Lan", "content": "Ready for a party?"},
        {"user": "Minh", "content": "Yes, I am ready."},
        {"user": "Minh", "content": "I want to transfer 3289723 VND to Hung."},
        {"user": "Cường", "content": "Chuyển quà sinh nhật mỗi cháu 400k"},
        {"user": "Minh", "content": "Chuyển Alisa ba chục nghìn tiền bún đậu"},
        {"user": "Minh", "content": "I want to transfer 3289723 VND to Hung với lời nhắn là 'Chúc mừng sinh nhật nhé, nhớ học giỏi'."},
        {"user": "Hung", "content": "I want to create a chat group for Minh, me, Lan, and Cường named 'Party| this sunday'."},
    ], action="CREATE_CHAT_GROUP")
    print("Output: ", out)
        