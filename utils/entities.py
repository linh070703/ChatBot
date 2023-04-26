from typing import List, Dict, Tuple, Union, Optional, Literal
from unidecode import unidecode
import re
import emoji
 
_VIETNAMESE_CHARS = set( [ c for c in "ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễếệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵỷỹ" ])

class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def __repr__(self):
        return f'Message(role={self.role!r}, content={self.content!r})'

class Conversation:
    NO_BOT_ACTION = "NO_BOT_ACTION"
    TRANSFER_MONEY = "TRANSFER_MONEY"
    CHECK_BALANCE = "CHECK_BALANCE"
    ASK_ASSISTANT = "ASK_ASSISTANT"
    CREATE_CHAT_GROUP = "CREATE_CHAT_GROUP"
    
    def __init__(self, conversation: Union[str, Dict]):
        """
        Extract the conversation into objects from the raw conversation string.
        Example:
            >>> Conversation({"command": "Continue the following conversation as the assistant.",
            ... "messages": [
            ...     {"role": "Alex", "content": "Who won the world series in 2020?"},
            ...     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            ...     {"role": "Bob", "content": "Where was it played?"}
            ... ]})
            Conversation(
                command='Continue the following conversation as the assistant.',
                messages=[
                    Message(role='Alex', content='Who won the world series in 2020?'),
                    Message(role='assistant', content='The Los Angeles Dodgers won the World Series in 2020.'),
                    Message(role='Bob', content='Where was it played?')
                ]
            )
        """
        if not isinstance(conversation, dict):
            raise NotImplementedError("Please use the JSON format for the conversation.")

        self.command = conversation['command']
        self.userInfo = conversation.get('userInfo', {"status": ""})
        self.user_status = self.userInfo.get('status', "")
        self.messages = []
        for message in conversation['messages']:
            role = message['role']
            content = message['content']
            self.messages.append(Message(role=role, content=content))
        self.raw_conversation = self.prepare_model_input()
    
    def __repr__(self):
        return f'Conversation(command={self.command!r}, messages={self.messages!r})'
    
    def is_bot_text_started(self, current_output_stream: str) -> bool:
        return self.raw_conversation in current_output_stream
    
    def prepare_model_input(self) -> str:
        """
        Prepare the input for the model.
        Example:
            >>> Conversation({"command": "Continue the following conversation as the assistant.",
            ... "messages": [
            ...     {"role": "Alex", "content": "Who won the world series in 2020?"},
            ...     {"role": "Assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            ...     {"role": "Bob", "content": "Where was it played?"}
            ... ]}).prepare_model_input()
            'Continue the following conversation as the assistant.
            Alex: Who won the world series in 2020?
            Assistant: The Los Angeles Dodgers won the World Series in 2020.
            Bob: Where was it played?
            Assistant: '
        """
        output = self.command + '\n'
        # output += f"System: {self.user_status}\n"
        for message in self.messages:
            output += message.role.capitalize() + ': ' + message.content + '\n'
        # output += 'Assistant: '
        output = emoji.demojize(output)
        output = "".join([unidecode(c) if c not in _VIETNAMESE_CHARS else c for c in output])
        self.raw_conversation = output
        return output
    
    def postprocess_model_output(self, model_output: str) -> str:
        """
        Postprocess the output from the model.
        """
        out = model_output.split(self.raw_conversation)[-1].strip()
        # Handle emoji in the content
        emoji_pattern = re.compile(":([a-z_]+):")
        out = emoji_pattern.sub(
            lambda match: emoji.emojize(match.group(0))
            if emoji.emojize(match.group(0)) != match.group(0)
            else "",
            out,
        )
        return out
   
    def extract_action(self, model_output: str, get_raw: bool = False) -> Dict:
        """
        Extract the action from the model output.
        
        Action:NO_ACTION
        Action:TRANSFER_MONEY[amount=1000, from=user1, to=user2]
        Action:CHECK_BALANCE[from=user1]

        Args:
            model_output (str): The model output.
        
        Returns:
            Dict: The action.
        
        Example:
            >>> Conversation({
            ...     'command': 'Continue the following conversation as the assistan.',
            ...     'messages': [
            ...         {'role': 'user', 'content': 'Who won the world series in 2020?'},
            ... ]}).extract_action("Action:TRANSFER_MONEY[amount=1000, from=user1, to=user2]")
            {'command': 'TRANSFER_MONEY', 'params': {'amount': '1000', 'from': 'user1', 'to': 'user2'}}
            >>> Conversation({
            ...     'command': 'Continue the following conversation as the assistan.',
            ...     'messages': [
            ...         {'role': 'user', 'content': 'Who won the world series in 2020?'},
            ... ]}).extract_action("Action:CHECK_BALANCE[from=user1]")
            {'command': 'CHECK_BALANCE', 'params': {'from': 'user1'}}
            >>> Conversation({
            ...     'command': 'Continue the following conversation as the assistan.',
            ...     'messages': [
            ...         {'role': 'user', 'content': 'Who won the world series in 2020?'},
            ... ]}).extract_action("Action:NO_ACTION")
            {'command': 'NO_ACTION', 'params': {}}
            >>> Conversation({
            ...     'command': 'Continue the following conversation as the assistan.',
            ...     'messages': [
            ...         {'role': 'user', 'content': 'Who won the world series in 2020?'},
            ... ]}).extract_action("Action:CREATE_CHAT_GROUP[users=user1,user2,user3]")
            
        """
        last_raw = model_output.split("Action:")[-1]
        if get_raw:
            return last_raw.split("Response:")[0].strip()
        if last_raw.startswith("NO_BOT_ACTION"):
            return {
                "command": "NO_BOT_ACTION",
                "params": {}
            }
        elif last_raw.startswith("TRANSFER_MONEY"):
            return {
                "command": "TRANSFER_MONEY",
                "params": {
                    "amount": last_raw.split("amount=")[-1].split(",")[0],
                    "from": last_raw.split("from=")[-1].split(",")[0],
                    "to": last_raw.split("to=")[-1].split("]")[0]
                }
            }
        elif last_raw.startswith("CHECK_BALANCE"):
            return {
                "command": "CHECK_BALANCE",
                "params": {
                    "from": last_raw.split("from=")[-1].split("]")[0]
                }
            }
        elif last_raw.startswith("CREATE_CHAT_GROUP"):
            return {
                "command": "CREATE_CHAT_GROUP",
                "params": [
                    last_raw.split("members=")[-1].split("]")[0].split(",")
                ]
            }


    
    def extract_intent(
            self, model_output: str,
        ) -> Literal['NO_BOT_ACTION', 'ASK_ASSISTANT', 'TRANSFER_MONEY', 'CHECK_BALANCE', 'CREATE_CHAT_GROUP']:
        """
        Extract the intent from the model output.

        Args:
            model_output (str): The model output.
            
        Returns:
            Literal['NO_BOT_ACTION', 'ASK_ASSISTANT', 'TRANSFER_MONEY']: The intent.
            
        Example:
            >>> Conversation({
            ...     'command': 'Continue the following conversation as the assistan.',
            ...     'messages': [
            ...        {'role': 'user', 'content': 'Who won the world series in 2020?'},
            ...     ]}).extract_intent("Intent:NO_BOT_ACTION")
            'NO_BOT_ACTION'
            >>> Conversation({
            ...     'command': 'Continue the following conversation as the assistan.',
            ...     'messages': [
            ...        {'role': 'user', 'content': 'Who won the world series in 2020?'},
            ...     ]}).extract_intent("Intent:ASK_ASSISTANT")
            'ASK_ASSISTANT'
            >>> Conversation({
            ...     'command': 'Continue the following conversation as the assistan.',
            ...     'messages': [
            ...        {'role': 'user', 'content': 'Who won the world series in 2020?'},
            ...     ]}).extract_intent("Intent:TRANSFER_MONEY")
            'TRANSFER_MONEY'
        """
        raw_intent = model_output.split("Intent:")[-1]
        if raw_intent.__contains__("NO_BOT_ACTION"):
            return "NO_BOT_ACTION"
        elif raw_intent.__contains__("ASK_ASSISTANT"):
            return "ASK_ASSISTANT"
        elif raw_intent.__contains__("TRANSFER_MONEY"):
            return "TRANSFER_MONEY"
        elif raw_intent.__contains__("CHECK_BALANCE"):
            return "CHECK_BALANCE"
        elif raw_intent.__contains__("CREATE_CHAT_GROUP"):
            return "CREATE_CHAT_GROUP"
        else:
            return "CANNOT_EXTRACT_INTENT"

    def extract_response(
            self, model_output: str,
        ) -> str:
        """
        Extract the intent from the model output.

        Args:
            model_output (str): The model output.
            
        Returns:
            Literal['NO_BOT_ACTION', 'ASK_ASSISTANT', 'TRANSFER_MONEY']: The intent.
            
        Example:
            >>> Conversation({
            ...     'command': 'Continue the following conversation as the assistan.',
            ...     'messages': [
            ...        {'role': 'user', 'content': 'Who won the world series in 2020?'},
            ...     ]}).extract_intent("Assistant: It was the Dodgers.")
            'It was the Dodgers.'
        """
        return model_output.split("Assistant: ")[-1]


    def get_all_users(self) -> List[str]:
        """
        Get all users in the conversation, excluding the assistant.
        Example:
            >>> Conversation({
            ...     'command': 'Continue the following conversation as the assistan.',
            ...     'messages': [
            ...        {'role': 'Alex', 'content': 'Who won the world series in 2020?'},
            ...        {'role': 'assistant', 'content': 'The Dodgers won the world series in 2020.'},
            ...        {'role': 'Bob', 'content': 'Who won the world series in 2019?'},
            ...        {'role': 'assistant', 'content': 'The Nationals won the world series in 2019.'},
            ...        {'role': 'Bob', 'content': 'Who won the world series in 2018?'},
            ...        {'role': 'assistant', 'content': 'The Red Sox won the world series in 2018.'},
            ...     ]}).get_all_users()
            ['Bob:', 'Alex:', 'System:']
            
        """
        output = list(set([m.role.capitalize() + ':' for m in self.messages if m.role.lower() != 'assistant'])) + ['System:']
        # print(f'List of users: {output}')
        return output
    

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    # doctest.run_docstring_examples(Conversation.extract_action, globals(), verbose=True)
    # doctest.run_docstring_examples(Conversation.extract_intent, globals(), verbose=True)
