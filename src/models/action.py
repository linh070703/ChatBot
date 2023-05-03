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

def get_action_params_with_validator(
        messages: List[Dict[str, str]],
        action: Literal["TRANSFER", "CREATE_CHAT_GROUP", "TRANSFER_TO_EACH_USERS"],
    ) -> Tuple[bool, Union[Dict[str, str], str]]:
    """
    Get action parameters from conversation history and user's intention.

    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.
        action (Literal["TRANSFER", "CREATE_CHAT_GROUP"]): User's intention, which is one of "TRANSFER" or "CREATE_CHAT_GROUP".
    
    Returns:
        is_enough_params (bool): Whether the action parameters are enough or not. If enough, then Action parameters are returned. Otherwise, Normal message is returned.
        Dict[str, str]: Action parameters. If action is "TRANSFER", then the returned dictionary should have 2 keys: "receiver" and "amount". If action is "CREATE_CHAT_GROUP", then the returned dictionary should have 1 key: "members".
        request_message (str): Normal message. This message is returned when the action parameters are not enough.

    Example:
        >>> messages = [
        ...     {"user": "Minh", "content": "Tao muốn chuyển khoản cho Nam 6966 k VND tiền bún đậu"},
        ... ]
        >>> get_action_params_with_validator(messages, action="TRANSFER")
        True, {
            "receiver": "Nam",
            "amount": "6966000",
            "msg": "bún đậu",
        }
        >>> messages = [    
        ...     {"user": "Minh", "content": "Chuyển mỗi người 100k."},
        ... ]
        >>> get_action_params_with_validator(messages, action="TRANSFER_TO_EACH_USERS")
        False, Nội dung chuyển khoản là gì bạn nhỉ?
        >>> messages = [
        ...     {"user": "Minh", "content": "Tao muốn tạo nhóm chat với Nam và Lan."},
        ... ]
        >>> get_action_params_with_validator(messages, action="CREATE_CHAT_GROUP")
        True, {
            "members": [
                "Nam",
                "Lan",
            ],
            "group_name": None, # group name can be None
        }
    """
    params, model_raw_output = get_action_params(messages, action)
    is_enough_params, request_message = validate_param(messages, model_raw_output, action, params)
    if is_enough_params:
        return is_enough_params, params
    else:
        return is_enough_params, request_message


def get_action_params(
        messages: List[Dict[str, str]],
        action: Literal["TRANSFER", "CREATE_CHAT_GROUP", "TRANSFER_TO_EACH_USERS"],
    ) -> Dict[str, str]:
    """
    Get action parameters from conversation history and user's intention.

    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.
        action (Literal["TRANSFER", "CREATE_CHAT_GROUP"]): User's intention, which is one of "TRANSFER" or "CREATE_CHAT_GROUP".
    
    Returns:
        Dict[str, str]: Action parameters. If action is "TRANSFER", then the returned dictionary should have 2 keys: "receiver" and "amount". If action is "CREATE_CHAT_GROUP", then the returned dictionary should have 1 key: "members".

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
            "members": [
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
    return params, output + "]"

def validate_param(
        messages: List[Dict[str, str]],
        model_raw_output: str,
        action: Literal["TRANSFER", "CREATE_CHAT_GROUP", "TRANSFER_TO_EACH_USERS"],
        params: Dict[str, str],
    ) -> Tuple[bool, Union[str, None]]:
    """
    Get action parameters from conversation history and user's intention.

    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.
        action (Literal["TRANSFER", "CREATE_CHAT_GROUP"]): User's intention, which is one of "TRANSFER" or "CREATE_CHAT_GROUP".
    
    Returns:
        Dict[str, str]: Action parameters. If action is "TRANSFER", then the returned dictionary should have 2 keys: "receiver" and "amount". If action is "CREATE_CHAT_GROUP", then the returned dictionary should have 1 key: "members".

    Example:
        >>> params, model_raw_output = get_action_params(messages=[
        ...     {"user": "Minh", "content": "Tao muốn chuyển khoản cho Nam 6966 k VND tiền bún đậu"},
        ... ], action="TRANSFER")
        >>> print(params, model_raw_output)
        {
            "receiver": "Nam",
            "amount": "6966000",
            "msg": "bún đậu",
        }, '[Nam,6966000|bún đậu]'
        >>> is_enough_params, request_message = validate_param(messages, model_raw_output, action="TRANSFER", params=params)
        >>> print(is_enough_params, request_message)
        True, None

        >>> params, model_raw_output = get_action_params(messages=[
        ...     {"user": "Minh", "content": "Chuyển mỗi người 100k."},
        ... ], action="TRANSFER_TO_EACH_USERS")
        >>> print(params, model_raw_output)
        {
            "amount_each": "100000",
            "msg": None,
        }, '[100000|null]'
        >>> is_enough_params, request_message = validate_param(messages, model_raw_output, action="TRANSFER_TO_EACH_USERS", params=params)
        >>> print(is_enough_params, request_message)
        False, "Bạn muốn nội dung chuyển khoản là gì?"

        >>> params, model_raw_output = get_action_params(messages=[
        ...     {"user": "Minh", "content": "Tao muốn tạo nhóm chat với Nam và Lan."},
        ... ], action="CREATE_CHAT_GROUP")
        >>> print(params, model_raw_output)
        {
            "members": [
                "Nam",
                "Lan",
            ],
            "group_name": None,
        }, '[Nam,Lan|null]'
        >>> is_enough_params, request_message = validate_param(messages, model_raw_output, action="CREATE_CHAT_GROUP", params=params)
        >>> print(is_enough_params, request_message)
        True, None # Because group name is not required
    """
    if action == "TRANSFER":
        if "receiver" in params and (params["receiver"] is None or params["receiver"].strip() == ""):
            return False, "Bạn muốn chuyển khoản cho ai?"
        if "amount" in params and (params["amount"] is None or params["amount"].strip() == ""):
            return False, "Bạn muốn chuyển khoản bao nhiêu?"
        if "msg" in params and (params["msg"] is None or params["msg"].strip() == ""):
            return False, "Bạn muốn nội dung chuyển khoản là gì?"
    elif action == "CREATE_CHAT_GROUP":
        if "members" in params and (params["members"] is None or len(params["members"]) == 0):
            return False, "Bạn muốn tạo nhóm chat với ai?"
        if "group_name" in params and (params["group_name"] is None or params["group_name"].strip() == ""):
            # return False, "Bạn muốn đặt tên nhóm chat là gì?"
            return True, None  # This is special case, because group name is not required
    elif action == "TRANSFER_TO_EACH_USERS":
        if "amount_each" in params and (params["amount_each"] is None or params["amount_each"].strip() == ""):
            return False, "Bạn muốn chuyển khoản bao nhiêu?"
        if "msg" in params and (params["msg"] is None or params["msg"].strip() == ""):
            return False, "Bạn muốn nội dung chuyển khoản là gì?"

    return validate_by_model(messages, model_raw_output, action, params)

def validate_by_model(
        messages: List[Dict[str, str]],
        model_raw_output: str,
        action: Literal["TRANSFER", "CREATE_CHAT_GROUP", "TRANSFER_TO_EACH_USERS"],
        params: Dict[str, str],
    ) -> Tuple[bool, Union[str, None]]:
    """
    Using AI model to validate action parameters that can not be validated by rules in validate_param()
    """
    ...

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
        