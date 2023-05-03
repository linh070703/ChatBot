from typing import List, Dict, Any, Union, Literal, Tuple, Optional

def get_response_message(
        params: Dict[str, str],
        action: Literal['TRANSFER', 'TRANSFER_TO_EACH_USERS', 'CREATE_CHAT_GROUP']
    ) -> str:
    """
    Get response message from assistant.
    """
    if action == 'TRANSFER':
        return f"Chuyển {params['amount']} cho {params['receiver']} thành công."
    elif action == 'TRANSFER_TO_EACH_USERS':
        return f"Đã chuyển cho mỗi người {params['amount_each']} thành công."
    elif action == 'CREATE_CHAT_GROUP':
        return f"Tạo nhóm chat {params['group_name']} thành công."