import os
import sys

sys.path.append("/home/thaiminhpv/Workspace/Code/FUNiX-ChatGPT-Hackathon/Chatbot/Chatbot/src/")

from typing import Dict, List, Tuple, Union, Literal, Any
from utils.logger import print, setup_logging_display_only
from utils.model_api import generate_general_call_chatgpt_api
import re
import logging

THANKS = ['Ok mình hiểu rồi', 'Cảm ơn bạn nhiều', 'Cảm ơn bạn nhiều lắm']

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
        or (
            "kế hoạch" in message
            and ("ngân sách" in message or "chi tiêu" in message)
        )
        or "ngân sách chi tiêu" in message
    )


def money_management_suggestion(messages: List[Dict[str, str]]) -> Tuple[str, List[str]]:
    """
    Args:
        messages (List[Dict[str, str]]): List of messages in conversation history. Each message is a dictionary with 2 keys: "user" and "content". "user" is the name of user who sent the message. "content" is the message sent by the user.

    Returns:
        Response (str): Response from the assistant.
        Suggestions (List[str]): List of suggestions for next user's message.
    
    Example:
    >>> money_management_suggestion([{"user": "user", "content": "Tạo kế hoạch ngân sách hàng tháng."}])
    ("Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?", [])
    >>> money_management_suggestion([
    ...    {"user": "Alex", "content": "Tạo kế hoạch ngân sách hàng tháng."},
    ...    {"user": "assistant", "content": "Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?"},
    ...    {"user": "Alex", "content": "5 triệu"}
    ... ])
    ("OK. Theo mình thì bạn nên dành 2 triệu 750 trăm cho các chi tiêu cần thiết, 500 nghìn cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành 250 nghìn cho việc từ thiện.", [])
    >>> money_management_suggestion([
    ...    {"user": "Alex", "content": "Tạo kế hoạch ngân sách hàng tháng."},
    ...    {"user": "assistant", "content": "Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?"},
    ...    {"user": "Alex", "content": "5 triệu"}
    ...    {"user": "assistant", "content": "OK. Theo mình thì bạn nên dành 2 triệu 750 trăm cho các chi tiêu cần thiết, 500 nghìn cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành 250 nghìn cho việc từ thiện."},
    ...    {"user": "Alex", "content": "Vì sao mình nên dành từng đó cho các chi tiêu cần thiết?"}
    ... ])
    """
    messages = messages[-5:]
    
    conversation = "\n".join([f"- {' '.join(message['user'].split())}: {' '.join(message['content'].split())}" for message in messages])
    last_user = messages[-1]['user']
    model_input = f"""This is a Personal Finance Assistant system that can provide user advices based on the pre-defined script. English and Vietnamese are supported. There are 3 stages in total. After user's request, system will display the current stage of the conversation, followed by "Analyzing: " no more than 100 words. Finally, system will response to the user as in pre-defined script. If user's message intention is not match the response expectation in the pre-defined script, system will display the current stage of the conversation as "BREAK" and end the conversation. System can use calculator syntax as {{300*20%}} to calculate the result.

## Script:
### Stage 1:
Expectation: User ask about money management plan.
- User: Tạo kế hoạch ngân sách hàng tháng.
Analyzing: User is asking about creating a monthly budget plan, which is in the scope of money management.
Current stage: Stage 1
- Assistant: Okay, mình sẽ giúp bạn lên kế hoạch chi tiêu nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?
### Stage 2:
Expectation: Assistant will ask User about their income and then User response with their income.
- User: 5 triệu
Analyzing: User is telling their income, which still is in the scope of money management.
Current stage: Stage 2
- Assistant: OK. Theo mình thì bạn nên dành {{salary*55%}} cho các chi tiêu cần thiết, {{salary*10%}} cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành {{salary*5%}} cho việc từ thiện.
### Stage 3:
Expectation: Assistant will response with the budget plan. User will response with their feedback on why they should spend that amount of money on each category.
- User: Vì sao mình nên dành từng đó cho các chi tiêu cần thiết?
Analyzing: User is asking about the reason why they should spend that amount of money on each category, which is still in the scope of money management.
Current stage: Stage 3
- Assistant: Việc dành 55% cho chi tiêu cần thiết là để đảm bảo rằng bạn có đủ tiền để chi trả các chi phí cố định hàng tháng và đảm bảo cuộc sống hàng ngày của mình không bị ảnh hưởng bởi thiếu hụt tài chính. Nếu bạn không thể đáp ứng các chi phí cơ bản này, thì việc chi tiêu cho các mục đích giải trí và đầu tư sẽ không có ý nghĩa.

## Real conversation:
...
{conversation}
Analyzing:"""
    logging.info(f"Model input: \n{model_input}")
    output = generate_general_call_chatgpt_api(
        inputs=model_input,
        temperature=0,
        max_tokens=256,
        stop=(f'- {last_user}:',)
    )
    logging.info(f"Model output: \n{output}")

    current_stage = get_current_stage(output)
    
    if current_stage == 'BREAK':
        return None, [] 
    
    response_message = output.split(current_stage)[-1].split('- Assistant:')[-1].split('Current stage:')[0].strip()
    response_message = " ".join(response_message.split())
    
    if current_stage == 'Stage 1':
        return response_message, ['5 triệu']  
    if current_stage == 'Stage 2':
        return response_message, ['Vì sao mình nên dành từng đó cho các chi tiêu cần thiết', 'Vì sao mình nên dành từng đó cho tiết kiệm dài hạn', 'Vì sao mình nên dành từng đó cho giáo dục', 'Vì sao mình nên dành từng đó cho hưởng thụ', 'Vì sao mình nên dành từng đó cho tự do tài chính', 'Vì sao mình nên dành từng đó cho từ thiện']
    if current_stage == 'Stage 3':
        if "chi tiêu cần thiết" in output:
            return """Việc dành 55% cho chi tiêu cần thiết là để đảm bảo rằng bạn có đủ tiền để chi trả các chi phí cố định hàng tháng và đảm bảo cuộc sống hàng ngày của mình không bị ảnh hưởng bởi thiếu hụt tài chính. Nếu bạn không thể đáp ứng các chi phí cơ bản này, thì việc chi tiêu cho các mục đích giải trí và đầu tư sẽ không có ý nghĩa.""", THANKS
        elif "tiết kiệm dài hạn" in output:
            return """Dưới đây là một số lý do vì sao bạn nên cân nhắc việc tiết kiệm dài hạn:

- Có sự cân bằng trong tài chính: Để đảm bảo sự ổn định tài chính, bạn cần có sự cân bằng giữa chi tiêu và tiết kiệm. Việc dành quá nhiều tiền cho tiết kiệm dài hạn có thể dẫn đến việc không đủ tiền trang trải các chi phí cần thiết trong cuộc sống.
- Tính linh hoạt tài chính: Việc dành quá nhiều tiền cho tiết kiệm dài hạn có thể giảm tính linh hoạt tài chính. Nếu bạn đầu tư quá nhiều vào tiết kiệm dài hạn, bạn có thể gặp khó khăn khi cần tiền gấp trong các tình huống khẩn cấp như bệnh tật, sự cố gia đình, hoặc khó khăn về tài chính trong kinh doanh.
- Đầu tư vào các khoản có lợi suất cao hơn: Đôi khi, việc đầu tư tiền vào các khoản có lợi suất cao hơn, chẳng hạn như đầu tư vào cổ phiếu hoặc bất động sản có thể mang lại lợi nhuận cao hơn so với tiền gửi tiết kiệm dài hạn. Do đó, bạn cần phải cân nhắc việc đầu tư vào các loại tài sản khác nhau để đảm bảo tính đa dạng và tối ưu hóa lợi nhuận.

Tóm lại, việc dành 10% thu nhập cho tiết kiệm dài hạn là một cách tốt để bảo vệ tài chính và đầu tư vào tương lai của bạn. Tuy nhiên, bạn cũng cần phải cân nhắc các yếu tố khác như tính linh hoạt tài chính và đầu tư vào các loại tài sản khác nhau để đảm bảo tính cân bằng và tối ưu hóa lợi nhuận.""", THANKS
        elif "giáo dục" in output:
            return """Dưới đây là một số lý do nên dành một phần thu nhập để đầu tư vào giáo dục:

- Nâng cao kỹ năng và trình độ: Giáo dục giúp bạn phát triển kỹ năng và trình độ cần thiết để thành công trong cuộc sống. Khi bạn đầu tư vào giáo dục, bạn đang đầu tư vào bản thân để trở nên có giá trị hơn trên thị trường lao động và trong các cơ hội kinh doanh.
- Mở rộng cơ hội nghề nghiệp: Đầu tư vào giáo dục có thể mở ra nhiều cơ hội nghề nghiệp cho bạn. Bạn có thể tìm kiếm các khóa học hoặc chương trình đào tạo mới để phát triển kỹ năng và trình độ, hoặc đầu tư vào việc học tiếng Anh hay các ngôn ngữ khác để mở rộng khả năng tìm việc.
- Đầu tư vào tương lai của bạn: Đầu tư vào giáo dục không chỉ giúp bạn phát triển kỹ năng và trình độ, mà còn là đầu tư vào tương lai của bạn. Có nhiều cơ hội kinh doanh và việc làm mới sẽ xuất hiện trong tương lai, và việc đầu tư vào giáo dục giúp bạn sẵn sàng để đón nhận những thách thức mới này.
- Cải thiện sức khỏe tinh thần: Học hỏi và đầu tư vào giáo dục cũng có thể giúp cải thiện sức khỏe tinh thần. Học hỏi là một hoạt động kích thích trí não và có thể giúp giảm stress và tăng khả năng giải quyết vấn đề.

Tóm lại, đầu tư vào giáo dục là một cách tốt để đầu tư vào bản thân và tương lai của bạn. Việc dành 10% thu nhập để đầu tư vào giáo dục có thể giúp bạn phát triển kỹ năng, trình độ, mở rộng cơ hội nghề nghiệp và cải thiện sức khỏe tinh thần.""" , THANKS
        elif "hưởng thụ" in output:
            return """Dưới đây là một số lý do tại sao nên dành một phần thu nhập để hưởng thụ:

- Giảm stress: Điều quan trọng trong cuộc sống là có thời gian để thư giãn và giảm stress. Dành thời gian và tiền bạc để hưởng thụ những thứ mình yêu thích như đi du lịch, mua sắm, thưởng thức đồ ăn ngon, hoặc tham gia các hoạt động giải trí có thể giúp giảm stress và tăng cường sức khỏe tinh thần.
- Tăng động lực: Hưởng thụ những thứ mình yêu thích có thể giúp tăng động lực và năng lượng để làm việc chăm chỉ hơn. Việc có thời gian để thư giãn và thưởng thức những thứ mình yêu thích giúp bạn cảm thấy thỏa mãn hơn và động lực hơn để tiếp tục làm việc.
- Giúp cân bằng cuộc sống: Việc dành thời gian và tiền bạc để hưởng thụ giúp cân bằng cuộc sống của bạn. Nếu chỉ tập trung vào công việc hoặc tiết kiệm mà không có thời gian để thư giãn và hưởng thụ, bạn có thể trở nên căng thẳng và thiếu cân bằng.
- Tạo kỷ niệm: Hưởng thụ những thứ mình yêu thích là cách tạo ra những kỷ niệm đáng nhớ. Những kỷ niệm đó có thể giúp bạn tạo ra những mối quan hệ tốt hơn và cải thiện chất lượng cuộc sống.

Tóm lại, dành 10% thu nhập để hưởng thụ là cách để đảm bảo rằng bạn có thời gian và tài chính để thưởng thức những thứ bạn yêu thích và giảm stress trong cuộc sống. Việc hưởng thụ cũng có thể giúp tăng động lực, cân bằng cuộc sống và tạo ra những kỷ niệm đáng nhớ.""" , THANKS
        elif "tự do tài chính" in output:
            return """Dưới đây là một số lý do tại sao nên dành một phần thu nhập để đầu tư vào tự do tài chính:

- Tự do tài chính: Khi bạn có một nguồn thu nhập bổ sung từ đầu tư, bạn sẽ có sự lựa chọn và quyền tự do về tài chính hơn. Bạn có thể sử dụng tiền thu được để đáp ứng nhu cầu và mục tiêu của mình, như vượt qua khó khăn tài chính, tiết kiệm cho ngày hưu trí, đầu tư vào bất động sản, hoặc trải nghiệm cuộc sống mà không lo lắng về tài chính.
- Tăng giá trị tài sản: Đầu tư là cách để tăng giá trị tài sản của bạn. Nếu đầu tư một phần thu nhập vào các khoản đầu tư an toàn và hiệu quả, bạn có thể tạo ra một nguồn thu nhập bổ sung và tăng giá trị tài sản của mình theo thời gian.
- Đảm bảo tài chính trong tương lai: Đầu tư vào tự do tài chính là cách để đảm bảo tài chính trong tương lai. Bạn có thể đầu tư vào các khoản tiết kiệm, quỹ đầu tư, chứng khoán hoặc bất động sản để đảm bảo nguồn thu nhập ổn định và bảo vệ tài chính trong trường hợp xảy ra sự cố tài chính.
- Phát triển tư duy tài chính: Việc đầu tư vào tự do tài chính cũng có thể giúp bạn phát triển tư duy tài chính và kỹ năng quản lý tài chính. Bạn sẽ học được cách đầu tư thông minh, quản lý tiền bạc hiệu quả và đưa ra các quyết định tài chính đúng đắn.

Tóm lại, dành 10% thu nhập để đầu tư vào tự do tài chính là cách để tạo ra nguồn thu nhập bổ sung và đảm bảo tài chính trong tương lai. Đầu tư vào tự do tài chính cũng giúp bạn tăng giá trị tài sản, phát triển tư duy tài chính và đảm bảo tài chính trong trường hợp xảy ra sự cố.
""", THANKS
        elif "từ thiện" in output:
            return """Dưới đây là một số lý do tại sao nên dành một phần thu nhập để hỗ trợ các hoạt động từ thiện:

- Giúp đỡ cộng đồng: Khi bạn đóng góp cho các hoạt động từ thiện, bạn đang giúp đỡ các nhóm và cá nhân khác trong cộng đồng. Những khoản đóng góp của bạn có thể giúp đỡ những người có hoàn cảnh khó khăn, giảm bớt đói nghèo và cải thiện cuộc sống cho những người cần giúp đỡ.
- Cảm giác hạnh phúc: Việc giúp đỡ người khác cũng có thể mang lại cảm giác hạnh phúc và hài lòng cho bạn. Bạn sẽ cảm thấy hạnh phúc và tự hào vì đã đóng góp cho một mục đích tốt đẹp và giúp đỡ những người khác.
- Tạo ra sự kết nối xã hội: Các hoạt động từ thiện cũng có thể giúp tạo ra sự kết nối xã hội. Bạn có thể gặp gỡ những người mới, giao lưu và học hỏi kinh nghiệm từ các hoạt động từ thiện. Ngoài ra, việc tham gia các hoạt động từ thiện cũng có thể giúp tạo ra một sự kết nối xã hội tích cực và giúp bạn cảm thấy phần nào là một phần của cộng đồng.
- Tạo dấu ấn tích cực: Khi bạn đóng góp cho các hoạt động từ thiện, bạn đang giúp tạo dấu ấn tích cực và đóng góp vào một mục đích lớn hơn. Điều này có thể mang lại sự tự hào và cảm giác rằng bạn đang giúp đỡ xã hội và thế giới tốt đẹp hơn.
""", THANKS

    
    return None, []


def get_current_stage(model_output: str) -> Literal['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4', 'BREAK']:
    """
    Get current stage of the conversation.
    
    Args:
        model_output (str): Model output.
        
    Returns:
        current_stage (str): Current stage of the conversation.
    
    Examples:
    >>> get_current_stage(" User is asking about the reason why they should spend that amount of money on each category, which is still in the scope of money management.\nCurrent stage: Stage 3\n- Assistant: Việc dành 55% cho chi tiêu cần thiết là để đảm bảo rằng bạn có đủ tiền để chi trả các chi phí cố định hàng tháng và đảm bảo cuộc sống hàng ngày của mình không bị ảnh hưởng bởi thiếu hụt tài chính. Nếu bạn không thể đáp ứng các chi phí cơ")
    'Stage 3'
    """
    current_stage = re.search(r"Current stage: (Stage \d)", model_output).group(1)
    current_stage = " ".join(current_stage.split())
    logging.info(f"Current stage: {current_stage}")
    if current_stage == "Stage 4":
        return "BREAK"
    
    # catch BREAK
    if "BREAK" in model_output:
        return "BREAK"

    return current_stage


if __name__ == "__main__":
    setup_logging_display_only()
    out = money_management_suggestion([
        {"user": "Alex", "content": "Tôi muốn được tư vấn về tài chính cá nhân."},
        {"user": "Assistant", "content": "Chào Alex, mình sẽ giúp bạn lên kế hoạch chi tiêu hàng tháng nhé. Thu nhập hiện tại mỗi tháng của bạn là bao nhiêu nhỉ?"},
        {"user": "Alex", "content": "12 triệu"},
        {"user": "Assistant", "content": "OK. Theo mình thì bạn nên dành 6 triệu 600 trăm cho các chi tiêu cần thiết, 1 triệu 200 nghìn cho từng quỹ: tiết kiệm dài hạn, giáo dục, hưởng thụ và tự do tài chính. Và dành 600 nghìn cho việc từ thiện."},
        {"user": "Alex", "content": "Tạo sao lại để từ thiện nhỉ?"},
    ])
    print(f"Final output: {out}")