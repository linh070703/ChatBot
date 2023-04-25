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
    def __init__(self, conversation: Union[str, Dict]):
        """
        Extract the conversation into objects from the raw conversation string.
        Example:
            >>> Conversation('Continue the following conversation as the assistant.
            User: Who won the world series in 2020?
            Assistant: The Los Angeles Dodgers won the World Series in 2020.
            User: Where was it played?')
            Conversation(
                command='Continue the following conversation:',
                messages=[
                    Message(role='assistant', content='The Los Angeles Dodgers won the World Series in 2020.'),
                    Message(role='user', content='Where was it played?')
                ]
            )
            >>> Conversation({"command": "Continue the following conversation as the assistant.",
            "messages": [
            {"role": "Alex", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "Bob", "content": "Where was it played?"}]})
            Conversation(
                command='Continue the following conversation as the assistant.',
                messages=[
                    Message(role='Alex', content='Who won the world series in 2020?'),
                    Message(role='assistant', content='The Los Angeles Dodgers won the World Series in 2020.'),
                    Message(role='Bob', content='Where was it played?')
                ]
            )
        """
        if isinstance(conversation, dict):
            self.command = conversation['command']
            self.userInfo = conversation.get('userInfo', {"status": ""})
            self.user_status = self.userInfo.get('status', "")
            self.messages = []
            for message in conversation['messages']:
                role = message['role']
                content = message['content']
                self.messages.append(Message(role=role, content=content))
        else:
            conversation = conversation.strip()
            # extract command
            self.command = conversation.split('\n')[0]
            # extract messages
            # User first, then alternate between assistant and user. The assistant answer can span multiple lines. User's message can be multiple lines. User's name can be anything and then a colon.
            # match by regex
            # self.messages = []
            # self.user_status = ""
            # for message in re.findall(r"([A-Za-z0-9 ]+):(.*)", conversation):
            #     role = message[0].strip().lower()
            #     content = message[1].strip()
            #     self.messages.append(Message(role=role, content=content))
            raise NotImplementedError("Please use the JSON format for the conversation.")
        self.raw_conversation = self.prepare_model_input()
    
    def __repr__(self):
        return f'Conversation(command={self.command!r}, messages={self.messages!r})'
    
    def is_bot_text_started(self, current_output_stream: str) -> bool:
        return self.raw_conversation in current_output_stream
    
    def prepare_model_input(self) -> str:
        """
        Prepare the input for the model.
        Example:
            >>> Conversation('Continue the following conversation as the assistant.
            User: Who won the world series in 2020?
            Assistant: The Los Angeles Dodgers won the World Series in 2020.
            User: Where was it played?').prepare_model_input()
            'Continue the following conversation:
            User: Who won the world series in 2020?
            Assistant: The Los Angeles Dodgers won the World Series in 2020.
            User: Where was it played?
            Assistant: '
        """
        output = self.command + '\n'
        output += f"System: {self.user_status}\n"
        for message in self.messages:
            output += message.role.capitalize() + ': ' + message.content + '\n'
        output += 'Assistant: '
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
   
    def extract_action(self, model_output: str) -> Dict:
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
        """
        last_raw = model_output.split("Action:")[-1]
        if last_raw.startswith("NO_ACTION"):
            return {
                "command": "NO_ACTION",
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

    
    def extract_intent(self, model_output: str) -> Literal['NO_BOT_ACTION', 'ASK_ASSISTANT', 'TRANSFER_MONEY']:
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
        else:
            return "CANNOT_EXTRACT_INTENT"


    def get_all_users(self) -> List[str]:
        """
        Get all users in the conversation, excluding the assistant.
        Example:
            >>> Conversation('Continue the following conversation as the assistant.
            User: Who won the world series in 2020?
            Assistant: The Los Angeles Dodgers won the World Series in 2020.
            User: Where was it played?').get_all_users()
            ['User']
        """
        output = list(set([m.role.capitalize() + ':' for m in self.messages if m.role.lower() != 'assistant'])) + ['System:']
        print(f'List of users: {output}')
        return output
    

if __name__ == "__main__":
    import doctest
    doctest.run_docstring_examples(Conversation.extract_action, globals(), verbose=True)
    doctest.run_docstring_examples(Conversation.extract_intent, globals(), verbose=True)
